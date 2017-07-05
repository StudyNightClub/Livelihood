# coding=utf-8

import re

_ADDRESS_REGEX = '(?:\d*)?(?:台灣)?(.*?市)((?:.*?區)?)((?:.*?(?:路|街|大道|橋)(?:[一二三四五六七八九十\d]*?段)?)?)(.*)'

_DESCRIPTION_REGEX = '，(\D*?)，'

address_pattern = re.compile(_ADDRESS_REGEX)
description_pattern = re.compile(_DESCRIPTION_REGEX)

""" Address of ROAD CONSTRUCTION """
def parse_road_address(address_name):    
    sub_address = address_pattern.search(address_name)
    if sub_address:
        return sub_address.groups()
    else:
        print('It does not match any groups in the regex parser of address of road event.')
        return (None, None, None, None)

""" Address of WATER OUTAGE """
def parse_water_address(address_name):
    sub_address = address_pattern.search(address_name)        
    if sub_address:
        return sub_address.groups()
    else:
        print('It does not match any groups in the regex parser of address of water event.')
        return (None, None, None, None)
    
def parse_water_description(description):    
    sub_description = description_pattern.search(description)
    if sub_description:
        return sub_description.groups()
    else:
        print('It does not match any groups in the regex parser of description of water event.')
        return None

