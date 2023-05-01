import time
import re

from datetime import datetime
from itemloaders.processors import TakeFirst, MapCompose
from scrapy import Item, Field
from w3lib.html import remove_tags


def datetime_to_unix_converter(value):
    datetime_object = datetime.strptime(value, '%b,%d %Y %H:%M:%S')
    return time.mktime(datetime_object.timetuple())

def clear_text(value):
    value = re.sub('[&]','',value)
    return value.replace('amp', '').strip()

def clear_size(value):
    return value.replace('Size:','').strip()

def clear_color(value):
    return value.replace('Color:','').strip()


class ReviewItem(Item):
    product_id = Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    rating = Field(input_processor = MapCompose(remove_tags), output_processor = TakeFirst())
    timestamp = Field(input_processor = MapCompose(remove_tags, datetime_to_unix_converter), output_processor = TakeFirst())
    text = Field(input_processor = MapCompose(remove_tags, clear_text), output_processor = TakeFirst())
    size = Field(input_processor = MapCompose(remove_tags, clear_size), output_processor = TakeFirst())
    color = Field(input_processor = MapCompose(remove_tags, clear_color), output_processor = TakeFirst())
