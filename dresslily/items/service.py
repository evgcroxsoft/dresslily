import json
import re


def only_digits(value):
    return re.findall(r'\d+', value)

def convert_starts_to_rating(stars):
    return str(str(stars).count('width:100%'))

def product_info(info, description):
    info = [i.replace(':','') for i in info] 
    description = [(description[a]).replace('        \n    ', '') for a in range(1, len(description), 2)]
    common_string = json.dumps(dict(zip(info, description)))
    return common_string

