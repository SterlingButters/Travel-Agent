# r = requests.get('https://www.tesla.com/en_CA/findus#/bounds/70,-50,42,-142,d?search=supercharger,&name=Canada')
# r_copy = copy.deepcopy(r.text)
#
# supercharger_locations = {}
# params_for_locations = ['latitude":"', 'longitude":"']
# location_param = 'location_id":"'
#
# Parse Tesla Locations
# while True:
#     # add address line to the dictionary
#     index = r_copy.find(location_param)
#     if index == -1:
#         break
#     index += len(location_param)
#
#     index_end = index
#     while r_copy[index_end] != '"':
#         index_end += 1
#     address_line_1 = r_copy[index:index_end]
#     address_line_1 = str(address_line_1)
#     supercharger_locations[address_line_1] = {}
#
#     for param in params_for_locations:
#         index = r_copy.find(param)
#         if index == -1:
#             break
#         index += len(param)
#
#         index_end = index
#         while r_copy[index_end] != '"':
#             index_end += 1
#         supercharger_locations[address_line_1][param[0:-3]] = r_copy[index:index_end]
#
#     r_copy = r_copy[index_end:len(r.text)]  # slice off the traversed code
#
# all_keys = supercharger_locations.keys()
#
# # Table of Locations
# data_matrix = [['Location ID', 'Latitude', 'Longitude']]
# first_ten_keys = supercharger_locations.keys()[0:10]
#
# for key in first_ten_keys:
#     row = [key,
#            supercharger_locations[key]['latitude'],
#            supercharger_locations[key]['longitude']]
#     data_matrix.append(row)
#
# table = ff.create_table(data_matrix)
# py.iplot(table, filename='supercharger-locations-sample')


# address_start = supercharger_locations.keys()[0]
# address_end = supercharger_locations.keys()[501]
