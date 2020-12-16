import scrapy
from scrapy.crawler import CrawlerProcess


class CharacterListSpider(scrapy.Spider):
    name = "CharacterListSpider"
    start_urls = ["https://wiki.summertimesaga.com/Characters"]

    def parse(self, response):
        for characterGroup in response.xpath('//*[@id="mw-content-text"]/div/ul'):
            for character in characterGroup.xpath("li/div"):
                yield {
                    "Name": character.xpath(
                        'div[@class="gallerytext"]/p/a/text()'
                    ).get(),
                    "Profile": response.urljoin(
                        character.xpath('div[@class="gallerytext"]/p/a/@href').get()
                    ),
                    "Thumbnail": response.urljoin(
                        character.xpath('div[@class="thumb"]/div/a/img/@src').get()
                    ),
                }


def fetch_source():
    process = CrawlerProcess()
    process.crawl(CharacterListSpider)
    result = process.start()
    return '"Summertime Saga" not implemented'