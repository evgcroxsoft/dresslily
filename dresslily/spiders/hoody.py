import scrapy
from scrapy.loader import ItemLoader

from dresslily.items.hoody import HoodyItem
from dresslily.items.service import product_info


class HoodySpider(scrapy.Spider):
    name = "hoody"
    allowed_domains = ["www.dresslily.com"]
    start_urls = ["https://www.dresslily.com/hoodies-c-181.html"]
    custom_settings = {
        'FEEDS': { 'products_data.csv': { 'format': 'csv', 'overwrite': True}},
        'FEED_EXPORT_FIELDS': ['product_id','product_url','name', 'discount', 'discounted_price', 
                               'original_price', 'total_reviews', 'product_info', 'availability']
        }    

    def parse(self, response):

        links = response.css('a.js-picture.js_logsss_click_delegate_ps.twoimgtip.category-good-picture-link::attr(href)').getall()
        for link in links:
            yield scrapy.Request(url=link, callback=self.parse_hoody, dont_filter=True, 
                                meta={'splash': {'args': {'wait': 2.5,},'endpoint': 'render.html'}})        

        next_page = response.xpath("//a[contains(.//text(), '>')]").attrib['href']
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)


    def parse_hoody(self, response):
        info = response.css('div.xxkkk20 strong').getall()   
        description = response.css('div.xxkkk20::text').getall()
        discount = response.css('span.off.js-dl-cutoff span::text').get()
     
        l = ItemLoader(item = HoodyItem(), response=response)

        l.add_css('product_id', 'em.sku-show')
        l.add_value('product_url', response.url)
        l.add_css('name', 'span.goodtitle')
        l.add_value('discount', discount)
        l.add_css('total_reviews', 'span.review-all-count.js-goreview')
        l.add_value('product_info', product_info(info, description))
        l.add_css('availability', 'div.numinfo')

        if discount is None:
            l.add_css('original_price', 'div.goodprice-line-start span')
            l.add_value('discounted_price', '0')
        else:
            l.add_css('discounted_price', 'div.goodprice-line-start span')
            l.add_xpath('original_price', '//span[@class="js-dl-marketPrice1 marketPrice my-shop-price dl-has-rrp-tag"]/span[@class="dl-price"]')
            
        yield l.load_item()
