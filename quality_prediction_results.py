import numpy as np
import collections
import json
from save_training_samples import ForecastDataset
from preprocessing import forecast_feature_vec, compute_dot_product
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

def calculate_errors(dataloader, activity, weights):
	n_data = dataloader.get_act_length(activity)
	error_list = np.zeros(n_data)
	send_error_list = np.zeros(n_data)
	send_error_correct = np.zeros(n_data)
	pretty_forecasts = []
	truth = np.zeros(n_data)
	predicted = np.zeros(n_data)
	for idx in range(n_data):
		cur_item = dataloader.get_item(activity,idx)
		cur_forecast = cur_item[0]
		cur_y = cur_item[1]
		#pretty_cast = prettify_forecast(cur_forecast)
		pretty_forecasts += [cur_forecast]
		feature_vec = forecast_feature_vec(cur_forecast)

		score = compute_dot_product(feature_vec, weights)
		error = (score - cur_y)**2
		error_list[idx] = error
		#bin_error = send_it_error(score, cur_y)
		send_error_list[idx] = error
		dif = score - cur_y
		# if(bin_error == 0):
		# 	send_error_correct[idx] = 1
		bin_size = 2
		if(abs(dif) < bin_size):
			send_error_correct[idx] = 1
		truth[idx] = cur_y
		predicted[idx] = score

	return error_list, truth, predicted, pretty_forecasts, send_error_list, send_error_correct


def main():
	weight_file = 'final_weight_file.txt'
	weights = load_weights(weight_file)

	dat_types = ['train', 'validate', 'test']
	mean_act_dicts = []
	std_act_dicts = []

	for act in weights.keys():
		if(act == 'Backpacking' or act =='Cycling'):
			continue
		mean_act_dict = {}
		mean_act_dict['Activity'] = act
		std_act_dict = {}
		std_act_dict['Activity'] = act
		act_weights = weights[act]
		for dat_type in dat_types:
			data_file = dat_type + '_data.txt'
			dataloader = ForecastDataset(data_file)
			error_list, truth, predicted, pretty_forecasts, send_error, correct_bin = calculate_errors(dataloader, act, act_weights)
			mean_error = np.mean(error_list)
			std_error = np.std(error_list)
			mean_act_dict[dat_type] = np.sqrt(mean_error)*5
			std_act_dict[dat_type] = np.sqrt(std_error)*5
		mean_act_dicts += [mean_act_dict]
		std_act_dicts += [std_act_dict]

	activities = []
	train_means = []
	val_means = []
	test_means = []
	train_errors = []
	val_errors = []
	test_errors = []
	for idx, act in enumerate(mean_act_dicts):
		activities += [act['Activity']]
		train_means += [act['train']]
		val_means += [act['validate']]
		test_means += [act['test']]
		train_errors += [std_act_dicts[idx]['train']]
		val_errors += [std_act_dicts[idx]['validate']]
		test_errors += [std_act_dicts[idx]['test']]

	barwidth = 0.2
	placement = list(range(len(train_means)))
	placement2 = [place + barwidth for place in placement]
	placement3 = [place - barwidth for place in placement]

	plt.figure()
	plt.bar(placement, val_means, width=barwidth, label='Validation')
	plt.bar(placement2, test_means, width=barwidth, label='Test')
	plt.bar(placement3, train_means, width=barwidth, label='Train')
	plt.legend()
	plt.title('Mean Prediction Error Rates for Several Activities')
	plt.ylabel('Percent Error')
	plt.xlabel('Activity')
	plt.xticks([x for x in range(len(train_means))], activities)
	plt.show()
	return

if __name__ == '__main__':
	main()