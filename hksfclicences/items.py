import scrapy

class StaffItem(scrapy.Item):
    name = scrapy.Field()
    role = scrapy.Field()
    activity = scrapy.Field()
    effectiveperiod = scrapy.Field()
    principal = scrapy.Field()
    ceref = scrapy.Field()

class StaffJsonItem(scrapy.Item):
    name = scrapy.Field()
    ceref = scrapy.Field()
    jsoninfo = scrapy.Field()
