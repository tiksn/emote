import uuid
from uuid import UUID

from source import Character
import scrapy
from scrapy.crawler import CrawlerProcess
from knack.log import get_logger

logger = get_logger(__name__)

source_id = UUID('a3ab469a-a790-457e-9f03-d5d3936e80d6')
source_name = "The Life & Times of Tim"


class CharacterListSpider(scrapy.Spider):
    name = "CharacterListSpider"
    start_urls = ["https://thelifeandtimesoftim.fandom.com/wiki/Category:Characters"]

    def parse(self, response, **kwargs):
        for characterList in response.xpath('//*[@id="mw-content-text"]/div[3]'):
            for characterGroup in characterList.xpath('div'):
                for character in characterGroup.xpath("ul/li"):
                    yield {
                        "name": character.xpath('a/text()').get(),
                        "profile_url": response.urljoin(
                            character.xpath('a/@href').get()
                        ),
                        "profile_picture_url": response.urljoin(
                            character.xpath('div/a/img/@src').get()
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
            _id=uuid.uuid5(source_id, result["profile_url"]),
            first_name=result["name"],
            last_name='',
            full_name=result["name"],
            profile_url=result["profile_url"],
            profile_picture_url=result["profile_picture_url"])
