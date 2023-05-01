import scrapy
from scrapy.loader import ItemLoader

from dresslily.items.review import ReviewItem
from dresslily.items.service import convert_starts_to_rating


lua_script = """
function main(splash, args)
    assert(splash:go(args.url))

    local element = splash:select('a.site-pager-next')
    element:click()

    splash:wait(splash.args.wait)
    return splash:html()
end
"""


class ReviewSpider(scrapy.Spider):
    name = "review"
    allowed_domains = ["www.dresslily.com"]
    start_urls = ["https://www.dresslily.com/hoodies-c-181.html"]
    custom_settings = {
        'FEEDS': { 'reviews_data.csv': { 'format': 'csv', 'overwrite': True}},
        'FEED_EXPORT_FIELDS': ['product_id','rating','timestamp', 'text', 'size', 'color']
        }

    def parse(self, response):

        links = response.css('a.js-picture.js_logsss_click_delegate_ps.twoimgtip.category-good-picture-link::attr(href)').getall()
        for link in links:
            yield scrapy.Request(url=link, callback=self.parse_hoody, 
                                meta={'splash': {'args': {'wait': 2.5,},'endpoint': 'render.html'}})         

        next_page = response.xpath("//a[contains(.//text(), '>')]").attrib['href']
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_hoody(self, response):
        reviews = response.css('div.reviewinfo.table')
        for review in reviews:
            product_id = response.css('em.sku-show').get()
            stars = response.css('span.review-star i::attr(style)').getall()
            
            l = ItemLoader(item = ReviewItem(), selector=review)

            l.add_value('product_id', product_id)
            l.add_value('rating', convert_starts_to_rating(stars))
            l.add_css('timestamp', 'span.review-time')
            l.add_css('text', 'div.review-content-text')
            l.add_xpath('size', "//span[@class='review-good-size'][contains(text(), 'Size:')]")
            l.add_xpath('color', "//span[@class='review-good-size'][contains(text(), 'Color:')]")

            yield l.load_item()

        next_page = response.css('a.site-pager-next::attr(href)').get()

        if next_page is not None:
            yield scrapy.Request(url=response.url, callback=self.parse_hoody,
                                meta={'splash': {'endpoint': 'execute', 'args': {'wait': 1, 'lua_source':lua_script, 'url':response.url},}})
