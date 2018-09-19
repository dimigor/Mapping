import urllib
import requests
import folium
import json
import datetime
import pandas
import random


def time_func(func):
    def wrapper(*args, **kwargs):
        start = datetime.time()
        result = func(*args, **kwargs)
        end = datetime.time()
        print('Elapsed time: {}'.format(end - start))
        return result
    return wrapper


def parse_json(offset=0):
    url = 'https://data.danimist.org.ua/api/action/datastore_search?offset={}&resource_id=b291187f-fe99-4057-bf13-f819d2923163'.format(offset)
    fileobj = urllib.request.urlopen(url)
    js = fileobj.read()
    json_obj = json.loads(js)

    return json_obj['result']


def iterb(json_obj):
    last_shape = 0
    list_koor = []

    for j in range(0, len(json_obj['records'])):
        if (int(json_obj['records'][j]['shape_pt_sequence']) < last_shape):
            poly = folium.PolyLine(locations=list_koor)
            map.add_child(poly)
            list_koor = []

        list_koor.append((float(json_obj['records'][j]['shape_pt_lat']), float(json_obj['records'][j]['shape_pt_lon'])))
        last_shape = int(json_obj['records'][j]['shape_pt_sequence'])


def write_from_file(name='shapes.txt'):
    list_i = []
    data = pandas.read_csv(name)
    lat = list(data['shape_pt_lat'])
    lon = list(data['shape_pt_lon'])
    dist = list(data['shape_dist_traveled'])

    fg = folium.FeatureGroup(name="MyMap")

    for lt, ln, dist in zip(lat, lon, dist):
        if (dist > 0):
            list_i.append((lt, ln))
        else:
            r_color = rand_color()
            poly = folium.PolyLine(locations=list_i, color='#' + str(r_color))
            fg.add_child(poly)
            map.add_child(fg)
            list_i = []
            list_i.append((lt, ln))


def rand_color():
    return random.randint(100000, 999999)


if __name__ == '__main__':
    map = folium.Map(location=(49.869580, 24.018340))

    # API
    # for i in range(0, 86000, 100):
    #     print(i)
    #     iterb(parse_json(i))
    write_from_file()
    map.save('index.html')
