import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from riksbank.items import Article


class RiksbankSpider(scrapy.Spider):
    name = 'riksbank'
    start_urls = ['https://www.riksbank.se/sv/press-och-publicerat/nyheter-och-pressmeddelanden/?Nyhetskategorier=20']

    def parse(self, response):
        links = response.xpath('//div[@class="listing-block__body"]//li/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="pagination-arrow pagination-arrow--right"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="meta-bar__date"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="page-base__main__body"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
