# coding=utf-8

import re


_ADDRESS_REGEX = '(?:台灣)?(.*?市)(.*?區)((?:.*?(?:路|街|大道|橋)(?:.*段)?)?)?(.*)'
_DESCRIPTION_REGEX = '(?:.*時|.*分)(?:，)(.*)(?:，)'


### Address of POWER OUTAGE ###
def parse_power_address(address_name):
        
    sub_address = re.search(_ADDRESS_REGEX, address_name)
    
    return sub_address.groups()

### Address of ROAD CONSTRUCTION ###
def parse_road_address(address_name):
    
    sub_address = re.search(_ADDRESS_REGEX, address_name)
    
    return sub_address.groups()

### Address of WATER OUTAGE ###
def parse_water_address(address_name, field_name):
    
    if field_name == 'description':
                
        sub_address = re.search(_DESCRIPTION_REGEX, address_name)
        
        return sub_address.groups()
    
    elif field_name == 'location':
        
        sub_address = re.search(_ADDRESS_REGEX, address_name)
        
        return sub_address.groups()
    
    else:
        print('Wrong field name')
    


