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
                    ).get()
                }

        for next_page in response.css("a.next-posts-link"):
            yield response.follow(next_page, self.parse)


def fetch_source():
    process = CrawlerProcess()
    process.crawl(CharacterListSpider)
    result = process.start()
    return '"Summertime Saga" not implemented'