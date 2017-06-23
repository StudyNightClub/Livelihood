# coding=utf-8


# API name: Convert address to coordinate
# example:
#   import map_converter
#   coord = map_converter.convert_address_to_coordinate('台北市大安區羅斯福路四段1號')
#   print(coord)

import os
import urllib.parse
import requests
import sys

KEY = os.environ['GOOGLE_GEO_KEY']

def convert_address_to_coordinate(address_name):

    url_address = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + urllib.parse.quote(address_name) + '&sensor=false&language=zh-tw&key=' + KEY

    web_request_coordinate = requests.get(url_address)

    if web_request_coordinate.status_code != 200:
        print('Web (ADDRESS TO COORDINATE) request is NOT ok. Request status code = %s.'
            %(web_request_coordinate.status_code))

    json_coordinate = web_request_coordinate.json()

    latitude = json_coordinate['results'][0]['geometry']['location']['lat']
    longitude = json_coordinate['results'][0]['geometry']['location']['lng']

    return (latitude, longitude)


# API name: Convert coordinate to address
# example:
#   import map_converter
#   addr = map_converter.convert_coordinate_to_address(25.017153, 121.533904)
#   print(addr)

def convert_coordinate_to_address(latitude, longitude):

    url_coordinate = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=' + str(latitude) + ',' + str(longitude) + '&sensor=false&language=zh-tw&key=' + KEY

    web_request_address = requests.get(url_coordinate)

    if web_request_address.status_code != 200:
        print('Web (COORDINATE TO ADDRESS) request is NOT ok. Request status code = %s.'
            %(web_request_address.status_code))

    json_address = web_request_address.json()

    try:
        return json_address['results'][0]['formatted_address']
    except IndexError as e:
        unexpected_coordinate = "Unexpected coordinate: " + str(latitude) + ", " + str(longitude)
        print(unexpected_coordinate)
        return '市區路'


# API name: Convert TWD97 to WGS84 (latitude and longitude)
# example:
#   import map_converter
#   coord = map_converter.twd97_to_wgs84(298978.8217, 2774899.7146)
#   print(coord)

import math


def twd97_to_wgs84(x, y):
    a = 6378137.0
    b = 6356752.314245
    longitude_origin = 121 * math.pi / 180
    k0 = 0.9999
    dx = 250000

    dy = 0
    e = math.pow((1 - math.pow(b, 2) / math.pow(a, 2)), 0.5)
    x -= dx
    y -= dy
    M = y / k0
    mu = M / (a * (1.0 - math.pow(e, 2) / 4.0 - 3 * math.pow(e, 4) / 64.0 - 5 * math.pow(e, 6) / 256.0))
    e1 = (1.0 - math.pow((1.0 - math.pow(e, 2)), 0.5)) / (1.0 + math.pow((1.0 - math.pow(e, 2)), 0.5))
    J1 = (3 * e1 / 2 - 27 * math.pow(e1, 3) / 32.0)
    J2 = (21 * math.pow(e1, 2) / 16 - 55 * math.pow(e1, 4) / 32.0)
    J3 = (151 * math.pow(e1, 3) / 96.0)
    J4 = (1097 * math.pow(e1, 4) / 512.0)
    fp = mu + J1 * math.sin(2 * mu) + J2 * math.sin(4 * mu) + J3 * math.sin(6 * mu) + J4 * math.sin(8 * mu)
    e2 = math.pow((e * a / b), 2)
    C1 = math.pow(e2 * math.cos(fp), 2)
    T1 = math.pow(math.tan(fp), 2)
    R1 = a * (1 - math.pow(e, 2)) / math.pow((1 - math.pow(e, 2) * math.pow(math.sin(fp), 2)), (3.0 / 2.0))
    N1 = a / math.pow((1 - math.pow(e, 2) * math.pow(math.sin(fp), 2)), 0.5)

    D = x / (N1 * k0)
    Q1 = N1 * math.tan(fp) / R1
    Q2 = (math.pow(D, 2) / 2.0)
    Q3 = (5 + 3 * T1 + 10 * C1 - 4 * math.pow(C1, 2) - 9 * e2) * math.pow(D, 4) / 24.0
    Q4 = (61 + 90 * T1 + 298 * C1 + 45 * math.pow(T1, 2) - 3 * math.pow(C1, 2) - 252 * e2) * math.pow(D, 6) / 720.0
    latitude = fp - Q1 * (Q2 - Q3 + Q4)
    Q5 = D
    Q6 = (1 + 2 * T1 + C1) * math.pow(D, 3) / 6
    Q7 = (5 - 2 * C1 + 28 * T1 - 3 * math.pow(C1, 2) + 8 * e2 + 24 * math.pow(T1, 2)) * math.pow(D, 5) / 120.0
    longitude = longitude_origin + (Q5 - Q6 + Q7) / math.cos(fp)
    latitude = (latitude * 180) / math.pi
    longitude = (longitude * 180) / math.pi

    return (latitude, longitude)



