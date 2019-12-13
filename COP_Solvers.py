import copy
import numpy as np

class Beam_Solver():
    def set_preprocessing_vals(self, distance_matrix, max_dist, activities, n_days, adventure_dict, max_day_score):
        self.distance_matrix = distance_matrix
        self.max_dist = max_dist
        self.activities = activities
        self.adventure_dict = adventure_dict
        self.max_day = n_days
        self.max_day_score = max_day_score


    def reset_results(self):
        """
        This function resets the statistics of the different aspects of the
        CSP solver. We will be using the values here for grading, so please
        do not make any modification to these variables.
        """
        # Keep track of the best assignment and weight found.
        self.optimalAssignment = {}
        self.optimalWeight = 0

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        self.numAssignments = 0

        # Keep track of the number of times backtrack() gets called.
        self.numOperations = 0

        # Keep track of the number of operations to get to the very first successful
        # assignment (doesn't have to be optimal).
        self.firstAssignmentNumOperations = 0

        # List of all solutions found.
        self.allAssignments = []

    def print_stats(self):
        """
        Prints a message summarizing the outcome of the solver.
        """
        if self.optimalAssignment:
            print(("Found %d optimal assignments with weight %f in %d operations" % \
                (self.numOptimalAssignments, self.optimalWeight, self.numOperations)))
            print(("First assignment took %d operations" % self.firstAssignmentNumOperations))
        else:
            print("No solution was found.")

    def get_delta_weight(self, assignment, var, val):
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return the change of weights after assigning the variable with the proposed
        value.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0: return w
        for var2, factor in list(self.csp.binaryFactors[var].items()):
            if var2 not in assignment: continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            if w == 0: return w
        return w

    def solve(self, csp, K, method='Standard'):
        """
        Solves the given weighted CSP using heuristics as specified in the
        parameter. Note that unlike a typical unweighted CSP where the search
        terminates when one solution is found, we want this function to find
        all possible assignments. The results are stored in the variables
        described in reset_result().

        @param csp: A weighted CSP.
        @param mcv: When enabled, Most Constrained Variable heuristics is used.
        @param ac3: When enabled, AC-3 will be used after each assignment of an
            variable is made.
        """
        # CSP to be solved.
        self.csp = csp

        # Reset solutions from previous search.
        self.reset_results()

        # The dictionary of domains of every variable in the CSP.
        self.domains = [{var: list(self.csp.values[var]) for var in self.csp.variables}]

        if(method=='Standard'):
            self.beam([{}], 0, [1], self.domains, K)
        self.print_stats()

    def beam(self, assignment_list, numAssigned, weight_list, domain_list, K):
        if(numAssigned == self.csp.numVars):
            np_weight_list = np.asarray(weight_list)
            max_idx = np.argmax(np_weight_list)
            max_weight = np.max(np_weight_list)
            max_assignment = assignment_list[max_idx]
            self.numAssignments += 1
            newAssignment = {}
            for var in self.csp.variables:
                newAssignment[var] = max_assignment[var]
            self.allAssignments.append(newAssignment)

            self.numOptimalAssignments = 1
            self.optimalWeight = max_weight

            self.optimalAssignment = newAssignment
            if self.firstAssignmentNumOperations == 0:
                self.firstAssignmentNumOperations = self.numOperations
            return

        self.numOperations += len(assignment_list)
        new_weights = []
        new_assignments = []
        new_domains = []
        cur_var = 0
        for idx, assignment in enumerate(assignment_list):
            var = self.get_unassigned_variable(assignment, numAssigned)
            cur_var = var
            ordered_values = domain_list[idx][var]
            weight = weight_list[idx]

            n_ordered_vals = len(ordered_values)
            cur_explore = K
            if(n_ordered_vals < K):
                cur_explore = n_ordered_vals
            for k_idx in range(0,cur_explore):
                val = ordered_values[k_idx]
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    new_weight = deltaWeight*weight

                    new_weights += [new_weight]
                    new_assign = copy.deepcopy(assignment)
                    new_assign[var] = val
                    new_assignments += [new_assign]

                    new_dom = copy.deepcopy(domain_list[idx])
                    new_domains += [new_dom]

        np_new_weights = np.asarray(new_weights)
        ranked_idx = np.argsort(-1*np_new_weights)

        next_count = K
        if(len(new_weights) < K):
            next_count = len(new_weights)
        next_weights = [new_weights[i] for i in ranked_idx][:next_count]
        next_assignments = [new_assignments[i] for i in ranked_idx][:next_count]
        next_domains = [new_domains[i] for i in ranked_idx][:next_count]

        for idx in range(0, len(next_weights)):
            next_domains[idx] = self.beam_arc_consistency_check(cur_var, next_assignments[idx][cur_var], next_domains[idx])



        self.beam(next_assignments, numAssigned + 1, next_weights, next_domains, K)


    def get_unassigned_variable(self, assignment, n_assigned):
        #Assignment goes in chronological order of days
        return self.csp.variables[n_assigned]


    def beam_arc_consistency_check(self, var, val, domain):
        cur_day = var
        assigned_activity = val
        assigned_idx = int(self.adventure_dict[assigned_activity][2])
        if(cur_day == self.csp.numVars - 1):
            return
        for idx in range(cur_day + 1, self.csp.numVars):
            domain[idx].remove(assigned_activity)

        for act in self.activities:
            adventure = act['Title']
            if adventure not in domain[cur_day + 1]:
                continue
            else:
                cur_idx = int(self.adventure_dict[adventure][2])
                cur_distance = self.distance_matrix[assigned_idx, cur_idx]
                if(cur_distance > self.max_dist):
                    domain[cur_day + 1].remove(adventure)

        return domain



class Branch_and_Bound_Solver():
    def set_preprocessing_vals(self, distance_matrix, max_dist, activities, n_days, adventure_dict, max_day_score):
        self.distance_matrix = distance_matrix
        self.max_dist = max_dist
        self.activities = activities
        self.adventure_dict = adventure_dict
        self.max_day = n_days
        self.max_day_score = max_day_score


    def reset_results(self):
        """
        This function resets the statistics of the different aspects of the
        CSP solver. We will be using the values here for grading, so please
        do not make any modification to these variables.
        """
        # Keep track of the best assignment and weight found.
        self.optimalAssignment = {}
        self.optimalWeight = 0

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        self.numAssignments = 0

        # Keep track of the number of times backtrack() gets called.
        self.numOperations = 0

        # Keep track of the number of operations to get to the very first successful
        # assignment (doesn't have to be optimal).
        self.firstAssignmentNumOperations = 0

        # List of all solutions found.
        self.allAssignments = []

    def print_stats(self):
        """
        Prints a message summarizing the outcome of the solver.
        """
        if self.optimalAssignment:
            print(("Found %d optimal assignments with weight %f in %d operations" % \
                (self.numOptimalAssignments, self.optimalWeight, self.numOperations)))
            print(("First assignment took %d operations" % self.firstAssignmentNumOperations))
        else:
            print("No solution was found.")

    def get_delta_weight(self, assignment, var, val):
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return the change of weights after assigning the variable with the proposed
        value.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0: return w
        for var2, factor in list(self.csp.binaryFactors[var].items()):
            if var2 not in assignment: continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            if w == 0: return w
        return w

    def solve(self, csp):
        """
        Solves the given weighted CSP using heuristics as specified in the
        parameter. Note that unlike a typical unweighted CSP where the search
        terminates when one solution is found, we want this function to find
        all possible assignments. The results are stored in the variables
        described in reset_result().

        @param csp: A weighted CSP.
        @param mcv: When enabled, Most Constrained Variable heuristics is used.
        @param ac3: When enabled, AC-3 will be used after each assignment of an
            variable is made.
        """
        # CSP to be solved.
        self.csp = csp

        # Reset solutions from previous search.
        self.reset_results()

        # The dictionary of domains of every variable in the CSP.
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}

        self.branch_and_bound({}, 0, 1)
        self.print_stats()


    def below_bound(self, assignment, weight, n_assigned):
        n_unassigned = self.csp.numVars - n_assigned - 1
        running_weight = weight
        for idx in range(0,n_unassigned):
            reverse_count = -idx - 1
            max_day_score = self.max_day_score[reverse_count]
            running_weight = running_weight*max_day_score
        if(running_weight < self.optimalWeight):
            return True
        return False

    def branch_and_bound(self, assignment, numAssigned, weight):

        self.numOperations += 1
        assert weight > 0
        if numAssigned == self.csp.numVars:
            # A satisfiable solution have been found. Update the statistics.
            self.numAssignments += 1
            newAssignment = {}
            for var in self.csp.variables:
                newAssignment[var] = assignment[var]
                #newAssignment[var] = assignment[var]
            self.allAssignments.append(newAssignment)

            if len(self.optimalAssignment) == 0 or weight >= self.optimalWeight:
                if weight == self.optimalWeight:
                    self.numOptimalAssignments += 1
                else:
                    self.numOptimalAssignments = 1
                self.optimalWeight = weight

                self.optimalAssignment = newAssignment
                if self.firstAssignmentNumOperations == 0:
                    self.firstAssignmentNumOperations = self.numOperations
            return

        #if(self.below_bound(assignment, weight, numAssigned)):
        #    return

        # Select the next variable to be assigned.
        var = self.get_unassigned_variable(assignment, numAssigned)

        # Get an ordering of the values. (should be preordered)
        ordered_values = self.domains[var]

        for val in ordered_values:
            deltaWeight = self.get_delta_weight(assignment, var, val)
            if deltaWeight > 0:
                new_weight = deltaWeight*weight
                assignment[var] = val
                if(self.below_bound(assignment, new_weight, numAssigned)):
                    del assignment[var]
                    break
                # create a deep copy of domains as we are going to look
                # ahead and change domain values
                localCopy = copy.deepcopy(self.domains)
                # fix value for the selected variable so that hopefully we
                # can eliminate values for other variables
                self.domains[var] = [val]

                # enforce arc consistency
                self.modified_arc_consistency_check(var, val)
                self.branch_and_bound(assignment, numAssigned + 1, weight * deltaWeight)
                # restore the previous domains
                self.domains = localCopy
                del assignment[var]


    def get_unassigned_variable(self, assignment, n_assigned):
        #Assignment goes in chronological order of days
        return self.csp.variables[n_assigned]


    def modified_arc_consistency_check(self, var, val):
        cur_day = var
        assigned_activity = val
        assigned_idx = int(self.adventure_dict[assigned_activity][2])
        if(cur_day == self.csp.numVars - 1):
            return
        for idx in range(cur_day + 1, self.csp.numVars):
            self.domains[idx].remove(assigned_activity)

        for act in self.activities:
            adventure = act['Title']
            if adventure not in self.domains[cur_day + 1]:
                continue
            else:
                cur_idx = int(self.adventure_dict[adventure][2])
                cur_distance = self.distance_matrix[assigned_idx, cur_idx]
                if(cur_distance > self.max_dist):
                    self.domains[cur_day + 1].remove(adventure)
