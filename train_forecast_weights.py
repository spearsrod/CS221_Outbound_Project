import numpy as np
from save_training_samples import ForecastDataset
import random
from preprocessing import forecast_feature_vec, naive_weights, compute_dot_product
import matplotlib.pyplot as plt
import json
import collections

def write_weights(weights, filename):
	with open(filename, 'w') as fout:
	    json.dump(weights, fout)

def l2_reg(w, eta, lam):
	return constant_multiply_default_dict(w,-2*eta*lam)

def l1_reg(w, eta, lam):
	l1_grad_w = collections.defaultdict(float)
	for k,v in w.items():
		if(v < 0):
			l1_grad_w[k] = 1
		elif(v > 0):
			l1_grad_w[k] = -1
	return constant_multiply_default_dict(l1_grad_w, -eta*lam)

def constant_multiply_default_dict(defdict, c):
	new_dict = collections.defaultdict(float)
	for k,v in defdict.items():
		new_dict[k] = v*c
	return new_dict

def add_default_dicts(dict1, dict2):
	mutual_keys = [key for key in dict1.keys() if key in dict2.keys()]
	dict1_keys = [key for key in dict1.keys() if key not in dict2.keys()]
	dict2_keys = [key for key in dict2.keys() if key not in dict1.keys()]
	sum_dict = collections.defaultdict(float)
	for key in mutual_keys:
		sum_dict[key] = dict1[key] + dict2[key]
	for key in dict1_keys:
		sum_dict[key] = dict1[key]
	for key in dict2_keys:
		sum_dict[key] = dict2[key]
	return sum_dict


def L_margin(w, phi, y):
	return y - compute_dot_product(phi, w)

def update_weight_l1(w, eta, phi, y, lam):
	margin = L_margin(w, phi, y)
	step = constant_multiply_default_dict(phi, 2*eta*margin)
	regularization_term = l1_reg(w, eta, lam)
	new_weight = add_default_dicts(w, add_default_dicts(step, regularization_term))
	return new_weight

def update_weight_l2(w, eta, phi, y, lam):
	margin = L_margin(w, phi, y)
	step = constant_multiply_default_dict(phi, 2*eta*margin)
	regularization_term = l2_reg(w, eta, lam)
	new_weight = add_default_dicts(w, add_default_dicts(step, regularization_term))
	return new_weight

def run_epoch(dataloader, activity, cur_weight, eta, lam, reg=1):
	n_data = dataloader.get_act_length(activity)
	indicies = list(range(0,n_data))
	random.shuffle(indicies)
	error_list = np.zeros(n_data)
	for idx2, cur_idx in enumerate(indicies):
		# if(np.mod(idx2,10) == 0):
		# 	print(idx2)
		cur_item = dataloader.get_item(activity,cur_idx)
		cur_forecast = cur_item[0]
		cur_y = cur_item[1]
		feature_vec = forecast_feature_vec(cur_forecast)

		score = compute_dot_product(feature_vec, cur_weight)
		error = (score - cur_y)**2
		error_list[idx2] = error
		if(reg == 1):
			new_weight = update_weight_l1(cur_weight, eta, feature_vec, cur_y, lam)
		elif(reg == 2):
			new_weight = update_weight_l2(cur_weight, eta, feature_vec, cur_y, lam)
		cur_weight = new_weight

	return new_weight, error_list

def train_forecast_weights(dataloader, activity, cur_weight, n_epochs, eta, lam, reg):
	epoch_error_list = np.zeros(n_epochs)
	epoch_std_list = np.zeros(n_epochs)
	n_data = dataloader.get_act_length(activity)
	for idx in range(n_epochs):
		t = np.asarray(list(range(0,n_data)))
		new_weight, error_list = run_epoch(dataloader, activity, cur_weight, eta, lam, reg)
		cur_weight = new_weight
		mean_error = np.mean(error_list)
		std_error = np.std(error_list)
		epoch_error_list[idx] = mean_error
		epoch_std_list[idx] = std_error
	return cur_weight, epoch_error_list, epoch_std_list


def explore_hyperparams(dataloader, activity, n_epochs):
	n_data = dataloader.get_act_length(activity)
	reg_range = [1,2]
	lam_range = np.logspace(-4, -1, 5)
	eta_range = np.logspace(-4, -1, 5)
	for idx5, reg in enumerate(reg_range):
		for idx3, lam in enumerate(lam_range):
			print('lam idx')
			print(idx3)
			for idx4, eta in enumerate(eta_range):
				print('eta idx')
				print(idx4)
				weights = naive_weights()
				t = np.asarray(list(range(0,n_epochs)))
				cur_weight = weights[activity]
				new_weight, epoch_errors, epoch_error_std = train_forecast_weights(dataloader, activity, cur_weight, n_epochs, eta, lam, reg)
				
				plt.figure()
				cur_title = 'lambda = ' + str(lam) + ' eta = ' + str(eta) + 'reg = ' + str(reg)
				plt.title(cur_title)
				plt.plot(t,epoch_errors)

	plt.show()

def train_activity(activity, dataloader, lam, eta, reg):
	weights = naive_weights
	cur_weight = weights[activity]
	n_epochs = 50
	new_weights, epoch_errors, epoch_std = train_forecast_weights(dataloader, activity, cur_weight, n_epochs, eta, lam, reg)
	return new_weights, epoch_errors, epoch_std

# def explore_activity(activity, dataloader):

# 	reg_items = 
# 	explore_hyperparams(dataloader, activity, n_epochs, 1)

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
	    # for k,v in data.items():
	    # 	# print(k)
	    # 	# print(v)
	    # 	v_def_dict = collections.defaultdict(float,v)
	    # 	weight_dict[k] = v_def_dict
	#return weight_dict

def load_backpacking(filename):
	back_def_dict = collections.defaultdict(float)
	with open(filename) as json_file:
	    data = json.load(json_file)
	    for k,v in data.items():
	    	back_def_dict[k] = v
	    #print(back_def_dict)
	return back_def_dict

def add_backpacking_to_weights():
	backpacking_weights = 'backpacking_trained.txt'
	other_weights = 'test_weight_file.txt'
	#o_weights = load_weights(other_weights)
	backpacking_weights2 = load_backpacking(backpacking_weights)
	weight_dict = load_weights(other_weights)
	weight_dict['Backpacking'] = backpacking_weights2

	new_weight_list = [weight_dict]
	test_weights = 'test2_weight_file.txt'
	write_weights(new_weight_list, test_weights)

def add_hiking_to_weights():
	hike_weights = 'test_weight_file2.txt'
	hike_dict = load_weights(hike_weights)
	other_weights = 'test2_weight_file.txt'
	other_dict = load_weights(other_weights)
	other_dict['Hiking'] = hike_dict['Hiking']
	write_weights([other_dict], 'final_weight_file.txt')

def combine_weight_dicts():
	originals = 'final_weight_file.txt'
	news = 'test_weight_file4.txt'
	prev_final_weights = load_weights(originals)
	new_final_weights = load_weights(news)
	print(prev_final_weights.keys())
	for k in new_final_weights.keys():
		print(k)
		prev_final_weights[k] = new_final_weights[k]
	print(prev_final_weights.keys())
	#other_dict['Hiking'] = hike_dict['Hiking']
	write_weights([prev_final_weights], 'final_weight_file.txt')
	#print(o_weights)

def main():
	n_epochs = 50
	#activity = 'Backpacking'
	data_file = 'train_data.txt'
	dataloader = ForecastDataset(data_file)

	#explore_hyperparams(dataloader, activity, n_epochs, 1)
	cur_data_acts = ['Cycling', 'Running', 'Fishing']
	# for act in cur_data_acts:
	# 	if(act == 'Skiing'):
	# 		continue
	# 	explore_hyperparams(dataloader, act, n_epochs)

	new_weight_dict= {}
	all_errors = np.zeros((len(cur_data_acts),n_epochs))
	all_std = np.zeros((len(cur_data_acts),n_epochs))
	for idx, act in enumerate(cur_data_acts):
		weights = naive_weights()
		cur_weight = weights[act]

		eta = 0.001
		lam = 0.01
		t = np.asarray(list(range(0,n_epochs)))
		new_weights, epoch_errors, epoch_std = train_forecast_weights(dataloader, act, cur_weight, n_epochs, eta, lam, 2)
		print(new_weights)
		all_errors[idx,:] = epoch_errors
		all_std[idx,:] = epoch_std

		new_weight_dict[act] = new_weights

	plt.figure()
	#cur_title = 'lambda = ' + str(lam) + ' eta = ' + str(eta) + 'reg = ' + str(1)
	cur_title = 'Forecast Weight Training Error: Lambda =' + str(lam) + ' Eta = ' + str(eta) + ' L2 Norm'
	plt.title(cur_title)
	plt.plot(t,all_errors[0,:])
	plt.plot(t,all_errors[1,:])
	plt.plot(t,all_errors[2,:])
	plt.legend(['Cycling', 'Running', 'Fishing'])
	plt.xlabel('Epoch')
	plt.ylabel('Error (MSE)')


	new_weight_list = [new_weight_dict]
	test_weights = 'test_weight_file4.txt'
	write_weights(new_weight_list, test_weights)
	plt.show()
	# lam1 = 0.01
	# lam2 = 0.0001
	# eta1 = 0.001
	# eta2 = 0.001
	# weights = naive_weights()
	# cur_weight = weights['Backpacking']
	# t = np.asarray(list(range(0,n_epochs)))
	# weights_1, epoch_errors1, epoch_std1 = train_forecast_weights(dataloader, activity, cur_weight, n_epochs, eta1, lam1, 1)
	# #weights_2, epoch_errors2, epoch_std2 = train_forecast_weights(dataloader, activity, cur_weight, n_epochs, eta1, lam1, 2)
	# weights_2, epoch_errors2, epoch_std2 = train_forecast_weights(dataloader, activity, cur_weight, n_epochs, eta2, lam2, 1)


	#weight_file = 'backpacking_trained.txt'
	# write_weights(weights_1, weight_file)
	# plt.figure()
	# plt.plot(t, epoch_errors1)
	# plt.plot(t, epoch_errors2)
	# plt.legend(['lam = 0.01', 'lam = 0.001'])
	# plt.show()
	# return

if __name__ == '__main__':
	main()