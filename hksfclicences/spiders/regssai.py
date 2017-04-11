import re
import scrapy
from hksfclicences.items import StaffItem

class HksfclicencesSpider(scrapy.Spider):
    name = "hksfclicences"
    allowed_domains = ["hkma.gov.hk"]
    start_urls = (
            'http://apps.hkma.gov.hk/cgi-bin/hkma/eng/ereg.pl',
    )

    def parse(self, response):
        institutions = response.css("#RegisteredInstitution option::attr(value)").extract()
        for institution in institutions:
            self.logger.info("Processing institution: %s", institution)
            form_data = {
                'compname': institution,
                'eo_type': '0',
                'ereg_act1': '1',
                'ereg_act2': '2',
                'ereg_act3': '4',
                'ereg_act4': '5',
                'ereg_act5': '6',
                'ereg_act6': '7',
                'ereg_act7': '9',
                'ereg_act8': '10'
            }
            yield scrapy.FormRequest.from_response(
                response,
                formname="form2",
                formdata=form_data,
                callback=self.parse_institution
            )

    def parse_institution(self, response):
        indlinks = response.css(".ChiInfoContent p a::attr(href)").extract()
        for indlink in indlinks:
            yield scrapy.Request(url='http://apps.hkma.gov.hk/cgi-bin/hkma/eng/%s' % indlink,
                       callback=self.parse_securitiesstaff)
        if 'Next' in response.css(".InfoContent a::text").extract():
            nextlink = response.css(".InfoContent:nth-child(2) a::attr(href)").extract_first()
            nextlinkparams = re.search(",(.*?),(.*?)\\)", nextlink).groups()
            yield scrapy.FormRequest.from_response(
                response,
                formname="nextform",
                formdata={'form_backward': nextlinkparams[0], 'page': nextlinkparams[1]},
                callback=self.parse_institution
            )

    def parse_securitiesstaff(self, response):
        yield scrapy.Request(
            url=re.sub("new_read_az.pl", "view_ereg_record.pl", response.url),
            callback=self.parse_securitiesstaffrecord
        )

    def parse_securitiesstaffrecord(self, response):
        records = response.css('.InfoContent tr')[1:]
        for tr in records:
            item = StaffItem()

            item['name'] = response.css("h2::text").extract_first()

            tdinfo = tr.css("td::text").extract()

            item['instname'] = tdinfo[0]
            item['acttype'] = tdinfo[1]
            item['role'] = tdinfo[3]

            eff_dates = re.findall("\d\d/\d\d/\d\d\d\d", tdinfo[2])
            item['startdate'] = eff_dates[0]
            if len(eff_dates) > 1:
                item['enddate'] = eff_dates[1]

            yield item
