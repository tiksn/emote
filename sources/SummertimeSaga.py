import uuid
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
                profile_url = response.urljoin(
                    character.xpath('div[@class="gallerytext"]/p/a/@href').get()
                )
                profile = dict()
                yield scrapy.Request(profile_url, self.parse_profile, cb_kwargs={"profile": profile})
                yield {
                    "name": character.xpath(
                        'div[@class="gallerytext"]/p/a/text()'
                    ).get(),
                    "profile": profile,
                    "profile_url": profile_url,
                    "thumbnail_url": response.urljoin(
                        character.xpath('div[@class="thumb"]/div/a/img/@src').get()
                    ),
                }

    def parse_profile(self, response, profile: dict[str, str]):
        infobox = response.xpath('//*[@id="mw-content-text"]/div/table/tbody')
        profile["title"] = response.xpath('//*[@id="firstHeading"]/text()').get()
        profile["name"] = infobox.xpath('tr[1]/th/span/text()').get()
        profile["full_length_portrait_url"] = response.urljoin(
                infobox.xpath('tr[2]/td/a/img/@src').get()
            )
        profile["gender"] = infobox.xpath('tr[4]/td/text()').get()


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
        profile_picture_url=result["thumbnail_url"])
