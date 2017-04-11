import scrapy

class StaffItem(scrapy.Item):
    name = scrapy.Field()
    instname = scrapy.Field()
    acttype = scrapy.Field()
    startdate = scrapy.Field()
    enddate = scrapy.Field()
    role = scrapy.Field()
