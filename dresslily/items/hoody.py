import re
from itemloaders.processors import TakeFirst, MapCompose
from scrapy import Item, Field
from w3lib.html import remove_tags

from .service import only_digits


def add_percentage(value):
    value = value + '%'
    return value

def check_total_reviews(value):
    if value:
        return only_digits(value)
    
def clean_product_info(value):
    value = re.sub("[{}]","",value)
    return value

def clean_availability(value):
    if value.__contains__('In Stock'):
        return 'In Stock'
    if value.__contains__('Out of Stock'):
        return 'Out of Stock'
    else:
        return only_digits(value)


class HoodyItem(Item):
    product_id = Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    product_url = Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    name = Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    discount = Field(input_processor = MapCompose(remove_tags, add_percentage), output_processor = TakeFirst())
    discounted_price = Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    original_price = Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    total_reviews = Field(input_processor = MapCompose(remove_tags, check_total_reviews), output_processor = TakeFirst())
    product_info = Field(input_processor = MapCompose(remove_tags, clean_product_info), output_processor = TakeFirst())
    availability = Field(input_processor = MapCompose(remove_tags, clean_availability), output_processor = TakeFirst())
