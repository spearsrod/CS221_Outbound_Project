import json
import numpy as np
from COP_setup import create_final_cop
from preprocessing import load_activities, precompute_forecast_scores, write_precomputed_activities, precompute_distances, save_distances, get_distance_submatrix
import collections
from COP_Solvers import Branch_and_Bound_Solver, Beam_Solver
#from csp_setup import Special_COP_Solver, create_alternative_cop
import ast
import time
import sys
import yaml
import matplotlib.pyplot as plt

def load_weights(filename):
    weight_dict = {}
    with open(filename) as json_file:
        data = json.load(json_file)[0]
        for k,v in data.items():
            cur_def_dict = collections.defaultdict(float)
            for k2, v2 in v.items():
                cur_def_dict[k2] = v2
            weight_dict[k] = cur_def_dict
    return weight_dict

def index_activities(activities):
    for idx, act in enumerate(activities):
        act['Index'] = idx

def load_distance_mat(filename):
    return np.load(filename)

def prune_activities(activities):
    pruned_activities = []
    for act in activities:
        act_dict = {}
        act_dict['Title'] = act['Title']
        act_dict['Index'] = act['Index']
        act_dict['Precomputed Scores'] = act['Precomputed Scores']
        act_dict['Precomputed Activities'] = act['Precomputed Activities']
        act_dict['Activities'] = act['Activities']
        act_dict['Rating'] = act['Rating']
        pruned_activities += [act_dict]
    return pruned_activities

def normalize_scores(activities):
    overall_max_abs_score = 0
    for idx, act in enumerate(activities):
        score = act['Precomputed Scores']
        max_score = abs(max(score))
        min_score = abs(min(score))
        overall_max = 0
        if(max_score > min_score):
            overall_max = max_score
        else:
            overall_max = min_score
        # if(idx == 0):
        #     overall_max_score = max_score
        #     overall_min_score = min_score
        # else:
        if(overall_max > overall_max_abs_score):
            overall_max_abs_score = overall_max

    #print(overall_max_abs_score)

    for idx, act in enumerate(activities):
        scores = act['Precomputed Scores']
        new_scores = []
        for score in scores:
            new_score = score*1.0/overall_max_abs_score + 1
            new_scores += [new_score]
        act['Precomputed Scores'] = new_scores
    return activities

def get_viable_activities(acts, weights):
    viable_act_types = weights.keys()
    viable_activities = []
    for act in acts:
        sub_activities = act['Activities']
        max_score_activity = ''
        score_list = []
        max_score_sum = 0
        for sub_act in sub_activities:
            if(sub_act in viable_act_types):
                viable_activities += [act]
                break

    return viable_activities


def save_activity_scores(viable_activities, weights, new_file):

    print(viable_activities)
    precompute_forecast_scores(viable_activities, weights)
    index_activities(viable_activities)

    viable_activities = prune_activities(viable_activities)
    viable_activities = normalize_scores(viable_activities)

    
    write_precomputed_activities(viable_activities, new_file)

    return viable_activities

def precompute_values(activity_file, weight_file, new_activity_file, distance_file):
    acts = load_activities(activity_file)
    weights = load_weights(weight_file)

    viable_activities = get_viable_activities(acts, weights)
    pruned_activities = save_activity_scores(viable_activities, weights, new_activity_file)
    distance_matrix = precompute_distances(viable_activities)
    save_distances(distance_matrix, distance_file)

def load_precomputed_values(activity_file, weight_file, distance_file):
    activities = load_activities(activity_file)
    weights = load_weights(weight_file)
    distance_matrix = load_distance_mat(distance_file)
    return activities, weights, distance_matrix

def select_desired(desired_activities, activity_list, distance_matrix):
    new_list_idx = []
    trimmed_activity_list = []
    for idx, act in enumerate(activity_list):
        sub_acts = act['Activities']
        for sub_act in sub_acts:
            if(sub_act in desired_activities):
                new_list_idx += [idx]
                trimmed_activity_list += [act]
                break

    dist_sub_mat = get_distance_submatrix(new_list_idx, distance_matrix)

    for idx, act in enumerate(trimmed_activity_list):
        act['Index'] = idx
    return trimmed_activity_list, dist_sub_mat

def get_max_day_scores(adventure_dict, n_days):
	max_scores = np.zeros(n_days)
	for k,v in adventure_dict.items():
		scores = v[0]
		for idx in range(0,n_days):
			score = scores[idx]
			if(score > max_scores[idx]):
				max_scores[idx] = score
	return list(max_scores)


def run_problem(activity_file, weight_file, distance_file, n_days, desired_activities, max_dist, method='Backtrack', K=0):
	activity_list, weight_dict, distance_matrix = load_precomputed_values(activity_file, weight_file, distance_file)


	#print(len(activity_list))
	#activity_list = activity_list
	#distance_matrix = distance_matrix

	activity_list, distance_matrix = select_desired(desired_activities, activity_list, distance_matrix)

	csp, adventure_dict = create_final_cop(activity_list, n_days, max_dist, distance_matrix)



	max_day_scores = get_max_day_scores(adventure_dict, n_days)


	if(method=='Backtrack'):
		problem = Branch_and_Bound_Solver()
		print('Setting Preprocessing')
		print(len(activity_list))
		problem.set_preprocessing_vals(distance_matrix, max_dist, activity_list, n_days, adventure_dict, max_day_scores)
		print('Preprocessing Set')
		print('Solving COP')
		problem.solve(csp)
		print('COP solved')

	else:
		problem = Beam_Solver()
		print('Setting Preprocessing')
		print(len(activity_list))
		problem.set_preprocessing_vals(distance_matrix, max_dist, activity_list, n_days, adventure_dict, max_day_scores)
		print('Preprocessing Set')
		print('Solving COP')
		problem.solve(csp, K)
		print('COP solved')

	assignments = ['']*n_days
	for idx, kv in enumerate(problem.optimalAssignment.items()):
		k, v = kv
		print('Activity for Day '+ str(idx+1) + ':')
		print(v)
    # 	print(v)
    # for idx, assign in enumerate(assignments):
    #     print('Activity for Day '+ str(idx+1) + ':')
    #     print(assign)

	optimal_weight = problem.optimalWeight
	n_ops = problem.numOperations

	return problem.optimalAssignment.items(), optimal_weight, n_ops

	problem = Special_COP_Solver()
	print('Setting Preprocessing')
	problem.set_preprocessing_vals(distance_matrix, max_dist, activity_list, n_days)
	print('Preprocessing Set')
	print('Solving COP')
	problem.solve(csp, method=method, K = K)
	print('COP Solved')
	problem.print_stats()

	assignments = ['']*n_days
	for idx, kv in enumerate(problem.optimalAssignment.items()):
	    k, v = kv
	    if(isinstance(v,int) and v > 0):
	        first_key = k[0]
	        if(first_key != 'sum' and first_key != 'sum_last'):
	            k_dict = ast.literal_eval(first_key)
	            k_title = k_dict['Title']
	            assignments[v-1] = k_title
	for idx, assign in enumerate(assignments):
	    print('Activity for Day '+ str(idx+1) + ':')
	    print(assign)
	return

def parse_config(config_filename):
    f = open(config_filename)
    x = yaml.safe_load(f)
    max_travel = x['max_travel_distance_km']
    activities = x['desired_activities']
    n_days = x['number_of_days']
    return n_days, activities, max_travel


def main():
    #save_activity_scores('outbound_activity_info_forecasts.txt', 'final_weight_file.txt', 'final_precomputed_activities.txt')
    #sys.setrecursionlimit(1500)40
    #return


	n_days, desired_activities, max_dist = parse_config('user_input.yaml')

	days = [1,2,3,4,5,6]


	# backtrack_weights = np.zeros(len(days))
	# backtrack_ops = np.zeros(len(days))
	# start_time = time.time()
	# for idx2, n_days in enumerate(days):
	# 	start_time = time.time()
	# 	assignment, weight, ops = run_problem('final_precomputed_activities.txt', 'final_weight_file.txt', 'final_distance_matrix.npy', n_days, desired_activities, max_dist, method='Backtrack', K=0)
	# 	time_dif = time.time() - start_time
	# 	backtrack_weights[idx2] = weight
	# 	backtrack_ops[idx2] = ops


	# beam_50_weights = np.zeros(len(days))
	# beam_50_ops = np.zeros(len(days))
	# start_time = time.time()
	# for idx2, n_days in enumerate(days):
	# 	start_time = time.time()
	# 	assignment, weight, ops = run_problem('final_precomputed_activities.txt', 'final_weight_file.txt', 'final_distance_matrix.npy', n_days, desired_activities, max_dist, method='Beam', K=50)
	# 	time_dif = time.time() - start_time
	# 	beam_50_weights[idx2] = weight
	# 	beam_50_ops[idx2] = ops

	# beam_1_weights = np.zeros(len(days))
	# beam_1_ops = np.zeros(len(days))
	# start_time = time.time()
	# for idx2, n_days in enumerate(days):
	# 	start_time = time.time()
	# 	assignment, weight, ops = run_problem('final_precomputed_activities.txt', 'final_weight_file.txt', 'final_distance_matrix.npy', n_days, desired_activities, max_dist, method='Beam', K=1)
	# 	time_dif = time.time() - start_time
	# 	beam_1_weights[idx2] = weight
	# 	beam_1_ops[idx2] = ops

	# plt.figure()
	# plt.plot(days, np.divide(backtrack_weights, backtrack_weights)*100)
	# plt.plot(days, np.divide(beam_50_weights, backtrack_weights)*100)
	# plt.plot(days, np.divide(beam_1_weights, backtrack_weights)*100)
	# plt.xlabel('Days Forecast')
	# plt.ylabel('Percent of Possible Score')
	# plt.title('Score Comparison of Branch and Bound Backtrack, Beam Search, and Greedy Baseline Search')
	# plt.legend(['Brand and Bound', 'Beam Search K=50', 'Baseline Search'])

	# plt.figure()
	# plt.plot(days, np.log10(backtrack_ops))
	# plt.plot(days, np.log10(beam_50_ops))
	# plt.plot(days, np.log10(beam_1_ops))
	# plt.xlabel('Days Forecast')
	# plt.ylabel('Number of Operations (10^n)')
	# plt.title('Operation Comparison of Branch and Bound Backtrack, Beam Search, and Greedy Baseline Search')
	# plt.legend(['Brand and Bound', 'Beam Search K=50', 'Baseline Search'])
	# plt.show()

	# return 
	method = 'Beam'

	k = [5,10, 30, 50, 100]


	weight_mat = np.zeros((len(k), len(days)))
	ops_mat = np.zeros((len(k), len(days)))
	time_mat = np.zeros(ops_mat.shape)

	for idx, K in enumerate(k):
		for idx2, n_days in enumerate(days):
			start_time = time.time()

			assignment, weight, ops = run_problem('final_precomputed_activities.txt', 'final_weight_file.txt', 'final_distance_matrix.npy', n_days, desired_activities, max_dist, method, K)
			time_dif = time.time() - start_time
			print("--- %s seconds ---" % (time.time() - start_time))
			weight_mat[idx, idx2] = weight
			ops_mat[idx, idx2] = ops
			time_mat[idx, idx2] = time_dif

	plt.figure()
	day_legend = []
	for idx, day in enumerate(days):
		plt.plot(k, np.divide(weight_mat[:,idx], weight_mat[:4]*100))
		day_legend += ['Days Planned: ' + str(day)]
	plt.xlabel('K value')
	plt.ylabel('Score')
	plt.title('Beam Search Scores With Various K values')
	plt.legend()

	plt.figure()
	day_legend = []
	#for idx, day in enumerate(days):
	plt.plot(k, ops_mat[:,3])
	#day_legend += ['Days Planned: ' + str(day)]
	plt.xlabel('K value')
	plt.ylabel('Number of Operations')
	plt.title('Beam Search Operations With Various K values (4 day schedule)')
	plt.legend()


	plt.figure()
	day_legend = []
	plt.plot(days, ops_mat[3,:])
	plt.xlabel('Days Scheduled')
	plt.ylabel('Number of Operations')
	plt.title('Beam Search Operations Across Number of Days (K=50)')
	plt.legend()
	plt.show()


    # acts = load_activities('outbound_activity_info_forecasts.txt')
    # print(len(acts))
    #acts = load_activities('outbound_activity_info_forecasts.txt')
    #weights = load_weights('test2_weight_file.txt')
    #via_acts = get_viable_activities(acts, weights)

    #precompute_values('outbound_activity_info_forecasts.txt', 'final_weight_file.txt', 'final_precomputed_activities.txt', 'final_distance_matrix')

    # # returned_mat = load_distances('distance_matrix.npy')
    # # print(returned_mat.shape)
    # #sub_mat = get_distance_submatrix([1,5,7], returned_mat)
    # weights = naive_weights()
    # precompute_forecast_scores(acts, weights)

    # test_precompute_write = 'test_precompute.txt'
    # write_precomputed_activities(acts, test_precompute_write)

if __name__ == '__main__':
    main()