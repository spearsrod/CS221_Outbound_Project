import numpy as np
import json
import collections

def haversine_distance(geo1, geo2):
    lat1 = geo1[0]
    lat2 = geo2[0]
    lon1 = geo1[1]
    lon2 = geo2[1]
    phi1 = np.deg2rad(lat1)
    phi2 = np.deg2rad(lat2)
    dphi = phi2 - phi1
    dlam = np.deg2rad(lon2 - lon1)
    R = 6371
    a = np.square(np.sin(dphi/2.0)) + np.multiply(np.cos(phi1), np.multiply(np.cos(phi2),np.square(dlam/2.0)))
    c = 2*np.arctan2(np.sqrt(a), np.sqrt(1-a))
    d = R*c
    return d

def precompute_distances(activity_info):
    n_activities = len(activity_info)
    distance_matrix = np.zeros((n_activities, n_activities))
    for idx1 in range(0, n_activities):
        if(np.mod(idx1,10)==0):
            print(idx1)
        loc1 = activity_info[idx1]['Location']
        for idx2 in range(idx1 + 1, n_activities):
            loc2 = activity_info[idx2]['Location']
            d = haversine_distance(loc1, loc2)
            distance_matrix[idx1, idx2] = d
            distance_matrix[idx2, idx1] = d
    return distance_matrix

def save_distances(matrix, filename):
    np.save(filename, matrix)

def load_distances(filename):
    distance_matrix = np.load(filename)
    return distance_matrix

def get_distance_submatrix(indicies, matrix):
    sub_mat = np.zeros((len(indicies), len(indicies)))
    for idx in range(0, len(indicies)):
        sub_mat[idx,:] = matrix[indicies[idx],indicies]
    return sub_mat


def load_activities(filename):
    data = []
    with open(filename) as json_file:
        data = json.load(json_file)
    return data

def combo_features(temp, rainfall, snowfall, vis, sky):
    combo_dict = {}
    temp_key = ''
    if(temp < 0):
        temp_key = 'Vortex'
    elif(temp < 15):
        temp_key = 'Icy'
    elif(temp < 32):
        temp_key = 'Freezing'
    elif(temp < 45):
        temp_key = 'Cold'
    elif(temp < 60):
        temp_key = 'Cool'
    elif(temp < 75):
        temp_key = 'Nice'
    elif(temp < 85):
        temp_key = 'Warm'
    elif(temp < 95):
        temp_key = 'Hot'
    else:
        temp_key = 'Burning'

    vis_key = ''
    if(vis <= 0.0):
        vis_key = 'No Vis'
    elif(vis <= 1.0):
        vis_key = 'Very Limited Vis'
    elif(vis <= 5.0):
        vis_key = 'Limited Vis'
    elif(vis <= 10.0):
        vis_key = 'Moderate Vis'
    elif(vis <= 15.0):
        vis_key = 'Good Vis'
    else:
        vis_key = 'Excellent Vis'

    combo_dict[temp_key] = 1
    if(rainfall > 0):
        temp_and_rain_key = temp_key + ' and Rain'
        combo_dict[temp_and_rain_key] = 1
    if(snowfall > 0):
        temp_and_snow_key = temp_key + ' and Snow'
        combo_dict[temp_and_snow_key] = 1
    temp_and_sky_key = temp_key + ' and Sky ' + str(sky)
    combo_dict[temp_and_sky_key] = 1

    combo_dict[vis_key] = 1
    vis_and_temp_key = temp_key + ' ' + vis_key
    combo_dict[vis_and_temp_key] = 1
    vis_and_sky_key = vis_key + ' and Sky ' + str(sky)
    combo_dict[vis_and_sky_key] = 1

    return combo_dict

def temp_features(temp):
    temp_dict = {}
    return temp_dict

def humidity_features(humidity):
    humidity_dict = {}
    if(humidity > 70):
        humidity_dict['hum_above_70'] = 1
    elif(humidity < 30):
        humidity_dict['hum_below_30'] = 1
    else:
        humidity_dict['hum_in_middle'] = 1
    #humidity_dict['humidity'] = humidity
    return humidity_dict

def precip_features(prec_prob, rainfall, snowfall):
    precip_dict = {}
    weighted_rainfall = prec_prob*rainfall*1.0/100
    weighted_snowfall = prec_prob*snowfall*1.0/100
    precip_dict['rainfall'] = weighted_rainfall
    precip_dict['snowfall'] = weighted_snowfall
    if(weighted_rainfall > 0):
        precip_dict['rainfall predicted'] = 1
    if(weighted_snowfall > 0):
        precip_dict['snowfall predicted'] = 1
    if(weighted_snowfall > 0 or weighted_rainfall > 0):
        precip_dict['precipitation predicted'] = 1
    if(rainfall > 0.5):
        precip_dict['heavy rain predicted'] = 1
    if(snowfall > 8):
        precip_dict['heavy snow predicted'] = 1
    return precip_dict

def wind_features(wind_dir, wind_speed, beautfortscale):
    wind_dict = {}
    wind_dir_key = 'wind from ' + wind_dir
    wind_dict[wind_dir_key] = 1
    wind_dict['wind speed'] = wind_speed
    beau_key = 'beaufort ' + str(beautfortscale)
    wind_dict[beau_key] = 1
    return wind_dict

def misc_features(visibility, weather_icon, dayOfWeek, daySegment, skyInfo, comfort, airInfo):
    misc_dict = {}
    #misc_dict['visibility'] = visibility
    #vis_key = 'visibility bin ' + str(int(visibility)//5)
    #misc_dict[vis_key] = 1
    weather_icon_key = 'weather icon ' + str(weather_icon)
    misc_dict[weather_icon_key] = 1
    weekday_key = 'weekday ' + str(dayOfWeek)
    misc_dict[weekday_key] = 1
    day_segment_key = 'day segment ' + str(daySegment)
    misc_dict[day_segment_key] = 1
    skyInfo_key = 'sky Info ' + str(skyInfo)
    misc_dict[skyInfo_key] = 1
    #misc_dict['comfort'] = comfort

    rounded_comfort_key = 'comfort bin ' + str(int(comfort)//10)
    misc_dict[rounded_comfort_key] = 1

    if(airInfo != '*'):
        airInfo_key = 'air Info ' + str(airInfo)
        misc_dict[airInfo_key] = 1

    weekdays = [2,3,4,5,6]
    weeekends = [1,7]
    weeknights = [1,2,3,4,5]
    weekendnights = [6,7]
    if(dayOfWeek in weekdays):
        misc_dict['Weekday'] = 1
    else:
        misc_dict['Weekend'] = 1
    if(dayOfWeek in weeknights):
        misc_dict['Weeknight'] = 1
    else:
        misc_dict['Weekendnight'] = 1

    return misc_dict


def add_to_default(small_dict, large_dict):
    for k,v in small_dict.items():
        large_dict[k] = v
    return

def forecast_feature_vec(forecast):
    feature_vec = collections.defaultdict(float)



    temp = float(forecast['temperature'])
    temp_dict = temp_features(temp)
    add_to_default(temp_dict, feature_vec)
    humidity = float(forecast['humidity'])
    hum_dict = humidity_features(humidity)
    add_to_default(hum_dict, feature_vec)
    prec_prob = float(forecast['precipitationProbability'])
    rainfall = forecast['rainFall']
    if(rainfall == '*'):
        rainfall = 0
    else:
        rainfall = float(rainfall)
    snowfall = forecast['snowFall']
    if(snowfall == '*'):
        snowfall = 0
    else:
        snowfall = float(snowfall)
    precip_dict = precip_features(prec_prob, rainfall, snowfall)
    add_to_default(precip_dict, feature_vec)


    wind_dir = forecast['windDescShort']
    wind_speed = float(forecast['windSpeed'])
    beaufortscale = int(forecast['beaufortScale'])
    wind_dict = wind_features(wind_dir, wind_speed, beaufortscale)
    add_to_default(wind_dict, feature_vec)


    visibility = float(forecast['visibility'])
    weather_icon = int(forecast['icon'])
    dayOfWeek = int(forecast['dayOfWeek'])
    daySegment = forecast['daySegment']
    skyInfo = int(forecast['skyInfo'])
    comfort = float(forecast['comfort'])
    airInfo = forecast['airInfo']
    combo_dict = combo_features(temp, rainfall, snowfall, visibility, skyInfo)
    add_to_default(combo_dict, feature_vec)
    general_info = misc_features(visibility, weather_icon, dayOfWeek, daySegment, skyInfo, comfort, airInfo)
    add_to_default(general_info, feature_vec)

    feature_vec['Bias Term'] = 1
    return feature_vec

def compute_dot_product(def_dict1, def_dict2):
    score = 0
    for k, v1 in def_dict1.items():
        v2 = def_dict2[k]
        score += v2*v1
    return score

def naive_weights():
    activity_list = ['Backpacking', 'Bodysurfing', 'Camping', 'Chillin', 'Cycling', 'Diving', 'Fishing', 'Fitness', 'Hiking', 'Kayaking', 'Kiteboarding', 'Mountain Biking', 'Photography', 'Rafting', 'Rock Climbing', 'Running', 'Skiing', 'Snowboarding', 'Snowshoeing', 'Stand Up Paddle', 'Surfing', 'Survival', 'Swimming', 'Volunteering', 'Yoga']

    cold_activities = ['Skiing', 'Snowboarding', 'Snowshoeing', 'Survival']
    rain_activities = []
    snow_activities = ['Skiing', 'Snowboarding', 'Snowshoeing']
    hot_activities = ['Bodysurfing', 'Diving', 'Fishing', 'Kayaking', 'Kiteboarding', 'Rafting', 'Stand Up Paddle', 'Swimming']
    relaxed_activities = []
    strenous_activities = []

    weights = {}
    for act in activity_list:
        act_dict = collections.defaultdict(float)
        weights[act] = act_dict

        # for k,v in act_dict.items():
        #     act_dict[k] = v*1.0/10
    return weights




def precompute_forecast_scores(activities, weights):
    n_segments = 0
    for act in activities:
        cur_forecast = act['Forecast']
        afternoon_forecasts = [cast for cast in cur_forecast if cast['daySegment'] == 'Afternoon']
        n_segments = len(afternoon_forecasts)
        max_activities = []
        day_scores = []
        for day in afternoon_forecasts:
            cur_feature_vec = forecast_feature_vec(day)
            max_score = -1000
            max_activity = ''
            min_score = 1000
            min_acitivty = ''
            for act_type in act['Activities']:
                if(act_type not in weights.keys()):
                    continue
                cur_weight = weights[act_type]
                score = compute_dot_product(cur_feature_vec, cur_weight)
                if(score > max_score):
                    max_score = score
                    max_activity = act_type
                if(score < min_score):
                    min_score = score
                    min_acitivty = act_type
            day_scores += [max_score]
            max_activities += [max_activity]

        act['Precomputed Scores'] = day_scores
        act['Precomputed Activities'] = max_activities
    return activities

def write_precomputed_activities(act, filename):
    with open(filename, 'w') as fout:
        json.dump(act, fout)

def main():
    acts = load_activities('outbound_activity_info_forecasts.txt')
    print(len(acts))
    # distance_matrix = precompute_distances(acts)
    # save_distances(distance_matrix, 'distance_matrix')
    # returned_mat = load_distances('distance_matrix.npy')
    # print(returned_mat.shape)
    #sub_mat = get_distance_submatrix([1,5,7], returned_mat)
    weights = naive_weights()
    precompute_forecast_scores(acts, weights)

    test_precompute_write = 'test_precompute.txt'
    write_precomputed_activities(acts, test_precompute_write)

if __name__ == '__main__':
    main()




# def create_outbound_csp(activity_info, n_days, max_dist, arc=False):

#     # same domain for each variable
#     if(n_days > 7):
#         print('Max forecast 7 days')
#         n_days = 7

#     #TODO allow sub-activities to be different assignments
#     dom = []
#     for act in activity_info:
#         for day_n in range(0,n_days):
#             #print(act)
#             dom += [(str(act), day_n)]
#     test = json.dumps(dom)

#     # domain = activity_info
#     # name variables as x_1, x_2, ..., x_n
#     variables = ['day_%d'%i for i in range(1, n_days+1)]
#     csp = CSP()

#     # Problem 0c
#     # BEGIN_YOUR_CODE (our solution is 4 lines of code, but don't worry if you deviate from this)
#     print('Adding Variables')
#     for idx, var in enumerate(variables):
#         csp.add_variable(var, dom)
#     #print('hello2')
#     #print('hello')
#     #print(csp.values['day_1'][])

#     #add unary factors
#     print('Adding factors')
#     counter = 0
#     for idx, var in enumerate(variables):
#         counter += 1
#         #if(np.mod(counter,50) == 0):
#         print(counter)
#         csp.add_unary_factor(var, lambda x: util.get_activity_score(x[0], x[1]))
#         csp.add_unary_factor(var, lambda x: x[1] == idx)

#     print('hi?')
#     counter1 = 0
#     counter2 = 0
#     for idx in range(0, len(variables)):
#         counter1 += 1
#         print(counter1)
#         if(idx < len(variables) - 1):
#             var1 = variables[idx]
#             var2 = variables[idx + 1]
#             csp.add_binary_factor(var1, var2, lambda x, y: util.get_distance_score(x[0], y[0], max_dist))
#         for idx2 in range(idx + 1, len(variables)):
#             counter2 += 1
#             #print(counter2)
#             if(np.mod(counter,50) == 0):
#                 print(counter)
#             var1 = variables[idx]
#             var2 = variables[idx2]
#             csp.add_binary_factor(var1, var2, lambda x, y: util.dif_activity_score(x[0], y[0]))

#     # for idx in range(0, len(variables) - 1):

#     # counter = 0
#     # for idx in range(0, len(variables)):
#     #     for idx2 in range(idx + 1, len(variables)):
#     #         counter += 1
#     #         if(np.mod(counter,50) == 0):
#     #             print(counter)
#     #         var1 = variables[idx]
#     #         var2 = variables[idx2]
#     #         csp.add_binary_factor(var1, var2, lambda x, y: util.dif_activity_score(x[0], y[0]))



#     # print('hello3')

#     #print('hello')

#     return csp