# coding=utf-8

import re


### Address of POWER OUTAGE ###
def parse_power_address(address_name):
    regex = '(.*?市)(.*?區)((?:.*?路|.*?街|.*?大道|.*?橋)?(?:.*段)?)?(.*)?'
    
    sub_address = re.search(regex, address_name)
    
    #print(sub_address.groups()[0],sub_address.groups()[1], sub_address.groups()[2], sub_address.groups()[3])
    
    # sub_address.group(0) is address_name
    #print(sub_address.group(1), sub_address.group(2), sub_address.group(3), sub_address.group(4))
    
    return sub_address.groups()

### Address of ROAD CONSTRUCTION ###
def parse_road_address(address_name):
    regex = '(.{2}?市)(.*?區)((?:.*?路|.*?街|.*?大道|.*?橋)?(?:.*段)?)?(.*)?'
    
    sub_address = re.search(regex, address_name)
    
    #print(sub_address.groups())
    
    return sub_address.groups()

### Address of WATER OUTAGE ###
def parse_water_address(address_name, field_name):
    
    if field_name == 'description':
        regex = '(?:.*時|.*分)(?:，)(.*)(?:，)'
        
        sub_address = re.search(regex, address_name)
        
        print(sub_address.groups())
        
        return sub_address.groups()
    
    elif field_name == 'location':
        regex = '(.{2}?市)(.*?區)((?:.*?路|.*?街|.*?大道|.*?橋)?(?:.*段)?)?(.*)?'
        
        sub_address = re.search(regex, address_name)
        
        print(sub_address.groups())
        
        return sub_address.groups()
    
    else:
        print('Wrong field name')
    


