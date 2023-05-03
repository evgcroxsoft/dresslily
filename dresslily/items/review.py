import time

from datetime import datetime
from itemloaders.processors import MapCompose
from scrapy import Item, Field
from w3lib.html import remove_tags


def datetime_to_unix_converter(value):
    datetime_object = datetime.strptime(value, '%b,%d %Y %H:%M:%S')
    value = str(time.mktime(datetime_object.timetuple()))
    return value

class ReviewItem(Item):
    product_id = Field(input_processor = MapCompose(remove_tags))
    rating = Field(input_processor = MapCompose(remove_tags))
    timestamp = Field(input_processor = MapCompose(remove_tags, datetime_to_unix_converter))
    text = Field(input_processor = MapCompose(remove_tags))
    size = Field(input_processor = MapCompose(remove_tags))
    color = Field(input_processor = MapCompose(remove_tags))
