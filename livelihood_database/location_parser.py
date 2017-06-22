# coding=utf-8

import re


_ADDRESS_REGEX = '(?:\d*)?(?:台灣)?(.*?市)(.*?區)((?:.*?(?:路|街|大道|橋)(?:.*段)?)?)?(.*)'


### Address of POWER OUTAGE ###
def parse_power_address(address_name):

    sub_address = re.search(_ADDRESS_REGEX, address_name)

    return sub_address.groups()

### Address of ROAD CONSTRUCTION ###
def parse_road_address(address_name):

    sub_address = re.search(_ADDRESS_REGEX, address_name)

    return sub_address.groups()

### Address of WATER OUTAGE ###
def parse_water_address(address_name):
    sub_address = re.search(_ADDRESS_REGEX, address_name)
    return sub_address.groups()
