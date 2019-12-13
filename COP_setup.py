from Course_CSP import CSP
import numpy as np

def generate_adventure_dict(activity_list):
    adventure_dict = {}
    for act in activity_list:
        key = act['Title']
        scores = act['Precomputed Scores']
        activities = act['Precomputed Activities']
        index = act['Index']
        val_list = [scores, activities, index]
        adventure_dict[key] = val_list
    return adventure_dict

def generate_ordered_domain(activity_list, day):
    day_scores = np.zeros(len(activity_list))
    adventure_list = []
    for idx, act in enumerate(activity_list):
        adventure_list += [act['Title']]
        cur_score = act['Precomputed Scores'][day]
        day_scores[idx] = cur_score
    sort_idx = np.argsort(-1*day_scores)
    sorted_scores = day_scores[sort_idx]
    sorted_adventures = [adventure_list[idx] for idx in sort_idx]
    return sorted_adventures, sorted_scores

def create_final_cop(activity_info, n_days, max_dist, dist_matrix):
    if(n_days > 6):
        print('Max forecast 6 days')
        n_days = 6

    #TODO allow sub-activities to be different assignments
    dom = list(range(0,n_days + 1))

    csp = CSP()

    adventure_dict = generate_adventure_dict(activity_info)

    print('Adding Variables and Factors')
    variables = []
    for idx in range(0,n_days):
        variables += [idx]
        domain, domain_scores = generate_ordered_domain(activity_info, idx)
        csp.add_variable(idx, domain)

        csp.add_unary_factor(idx, lambda x: adventure_dict[x][0][idx])

    return csp, adventure_dict


