import urllib
import requests
import folium
import json
import time
import pandas
import random

# decorator calculate working time


def time_func(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print('Function - {}, Elapsed time: {}'.format(func, end - start))
        return result
    return wrapper


# func works with API danimist.org.ua
def parse_json(offset=0):
    url = 'https://data.danimist.org.ua/api/action/datastore_search?offset={}&resource_id=b291187f-fe99-4057-bf13-f819d2923163'.format(offset)
    fileobj = urllib.request.urlopen(url)
    js = fileobj.read()
    json_obj = json.loads(js)

    return json_obj['result']


#itereable in records
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


@time_func
def set_routes(name='shapes.txt'):
    list_i = []
    data = pandas.read_csv(name)
    lat = list(data['shape_pt_lat'])
    lon = list(data['shape_pt_lon'])
    dist = list(data['shape_dist_traveled'])

    fr = folium.FeatureGroup(name="Bus directions in Lviv")

    for lt, ln, dist in zip(lat, lon, dist):
        if (dist > 0):
            list_i.append((lt, ln))
        else:
            r_color = rand_color()
            poly = folium.PolyLine(locations=list_i, color='#' + str(r_color))
            fr.add_child(poly)
            map.add_child(fr)
            list_i = []
            list_i.append((lt, ln))


def rand_color():
    return random.randint(100000, 999999)

# func calculate difference between center in Lviv and Bus stop


def make_color(lon, lat):
    lon_center = 49.843636
    lat_center = 24.026424

    lon_diff = lon_center - lon
    lat_diff = lat_center - lat
    diff = abs(lon_diff * 100) + abs(lat_diff * 100)

    if ((30 < diff) or (diff < -30)):
        return 'red'

    elif ((10 <= diff <= 30) or (-10 >= diff >= -30)):

        return 'orange'
    else:
        return 'green'


@time_func
def set_stops(name='stops.txt'):
    data = pandas.read_csv(name)
    lat = list(data['stop_lat'])
    lon = list(data['stop_lon'])
    stop_name = list(data['stop_name'])

    fs = folium.FeatureGroup(name="Bus stops in Lviv")

    for lt, ln, stop in zip(lat, lon, stop_name):
        poly = folium.CircleMarker(
            location=(lt, ln),
            radius=5,
            fill_color=make_color(lt, ln),
            color='#d3d7d8',
            popup=stop,
            fill_opacity=0.6)

        fs.add_child(poly)
        map.add_child(fs)


@time_func
def geo_json(layer_name, properties, num1, num2, file_name='world.json'):
    fg = folium.FeatureGroup(name=layer_name)

    fg.add_child(folium.GeoJson(open(
        file_name,
        encoding="utf-8-sig").read(),
        style_function=lambda x: {
        'fillColor': 'green'
        if x['properties'][properties] < num1
        else 'orange' if num1 <= x['properties'][properties] < num2
        else 'red'}))

    map.add_child(fg)


def set_border():
    geo_json(layer_name='Area', properties='AREA', num1=19000, num2=250000)
    geo_json(layer_name='Population', properties='POP2005', num1=5000000, num2=45000000)


if __name__ == '__main__':
    # create instance
    map = folium.Map(location=(49.869580, 24.018340), zoom_start=7, tiles='Mapbox Bright')

    set_routes()
    set_stops()
    set_border()

    map.add_child(folium.LayerControl())
    map.save('index.html')
