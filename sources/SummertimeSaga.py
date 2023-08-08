from uuid import UUID

from source import Character
import scrapy
from scrapy.crawler import CrawlerProcess
from knack.log import get_logger

logger = get_logger(__name__)

source_id = UUID('185356be-38ed-4beb-9af1-5f19057526a3')
source_name = "Summertime Saga"


class CharacterListSpider(scrapy.Spider):
    name = "CharacterListSpider"
    start_urls = ["https://wiki.summertimesaga.com/Characters"]

    def parse(self, response, **kwargs):
        for characterGroup in response.xpath('//*[@id="mw-content-text"]/div/ul'):
            for character in characterGroup.xpath("li/div"):
                yield {
                    "name": character.xpath(
                        'div[@class="gallerytext"]/p/a/text()'
                    ).get(),
                    "profile_url": response.urljoin(
                        character.xpath('div[@class="gallerytext"]/p/a/@href').get()
                    ),
                    "profile_picture_url": response.urljoin(
                        character.xpath('div[@class="thumb"]/div/a/img/@src').get()
                    ),
                }


def fetch_source():
    process = CrawlerProcess()
    results = []
    process.crawl(CharacterListSpider)

    def crawler_results(item, response, spider):
        results.append(item)

    for p in process.crawlers:
        p.signals.connect(crawler_results, signal=scrapy.signals.item_scraped)

    process.start()

    return list(map(dict_to_character, results))


def dict_to_character(result: dict[str, str]):
    return Character(
            first_name=result["name"],
            last_name='',
            full_name=result["name"],
            profile_url=result["profile_url"],
            profile_picture_url=result["profile_picture_url"])
