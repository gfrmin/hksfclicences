import re
import scrapy
from hksfclicences.items import StaffJsonItem
import string
import json

class HksfclicencesSpider(scrapy.Spider):
    name = "hksfclicences2"
    allowed_domains = ["sfc.hk"]
    start_urls = (
            'http://www.sfc.hk/publicregWeb/searchByRa',
    )

    def parse(self, response):
        for licencenumber in range(1, 11):
            for letter in string.ascii_uppercase:
                yield scrapy.FormRequest(
                    "http://www.sfc.hk/publicregWeb/searchByRaJson",
                    formdata={
                        'licstatus': 'all',
                        'ratype': str(licencenumber),
                        'roleType': 'individual',
                        'nameStartLetter': letter,
                        'page': '1',
                        'start': '0',
                        'limit': '20000'
                    },
                    callback=self.parse_json
                )

    def parse_json(self, response):
        for ceref in [item['ceref'] for item in json.loads(response.body)['items']]:
            yield scrapy.Request(
                'http://www.sfc.hk/publicregWeb/indi/' +
                ceref +
                '/licenceRecord',
                callback=self.parse_indi,
                meta={'ceref': ceref}
            )

    def parse_indi(self, response):
        if response.css(".post:nth-child(2) p::text").extract_first() == u'\r\n\t No record found. \r\n':
            yield scrapy.Request(
                'http://www.sfc.hk/publicregWeb/eo/' +
                response.meta['ceref'] +
                '/details', 
                callback=self.parse_eo,
                meta={'ceref': response.meta['ceref']}
            )
            return
        item = StaffJsonItem()
        item['name'] = response.css(":nth-child(3) p::text").extract()[2][2:]
        item['ceref'] = response.meta['ceref']
        js = response.css("script::text")[-2].extract()
        item['jsoninfo'] = json.loads(re.search(r"var licRecordData = (.*?}]}]);", js).group(1))
        yield item

    def parse_eo(self, response):
        item = StaffJsonItem()
        item['name'] = response.css(":nth-child(3) p::text").extract()[2][2:]
        item['ceref'] = response.meta['ceref']
        js = response.css("script::text")[-2].extract()
        item['jsoninfo'] = json.loads(re.search(r"var eoDetailData = (.*?}]);", js).group(1))
        yield item
