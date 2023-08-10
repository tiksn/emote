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
                    profile_url = response.urljoin(
                        character.xpath('a/@href').get()
                    )
                    profile = dict()
                    yield scrapy.Request(profile_url, self.parse_profile, cb_kwargs={"profile": profile})
                    yield {
                        "name": character.xpath('a/text()').get(),
                        "profile": profile,
                        "profile_url": profile_url,
                        "thumbnail_url": response.urljoin(
                            character.xpath('div/a/img/@src').get()
                        ),
                    }

    def parse_profile(self, response, profile: dict[str, str]):
        infobox = response.xpath('//*[@id="mw-content-text"]/div/table/tbody')
        profile["title"] = response.xpath('//*[@id="firstHeading"]/span/text()').get()
        profile["name"] = infobox.xpath('tr[1]/th/text()').get()
        profile["full_length_portrait_url"] = response.urljoin(
            infobox.xpath('tr[2]/td/a/img/@src').get()
        )

        for information in infobox.xpath('tr'):
            information_name = information.xpath('td[1]/b/text()').get()
            information_value = information.xpath('td[2]/text()').get()

            if information_name is not None and information_value is not None:
                information_name = information_name.lower().strip()
                information_value = information_value.strip()

                if information_name == 'species':
                    profile["species"] = information_value
                elif information_name == 'gender':
                    profile["gender"] = information_value


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


def dict_to_character(result):
    name = result["name"].strip()
    profile_name = result["profile"]["name"].strip()
    profile_title = result["profile"]["title"].strip()

    return Character(
            _id=uuid.uuid5(source_id, result["profile_url"]),
            first_name=name,
            last_name='',
            full_name=name,
            profile_url=result["profile_url"],
            profile_picture_url=result["profile"]["full_length_portrait_url"])
