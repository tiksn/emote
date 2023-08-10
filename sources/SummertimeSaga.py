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
        name = infobox.xpath('tr[1]/th/span/text()').get()
        if name is None:
            name = infobox.xpath('tr[1]/th/text()').get()
        profile["name"] = name
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


def dict_to_character(result):
    name = result["name"]
    profile_name = result["profile"]["name"]
    profile_title = result["profile"]["title"]
    longest_name = max([name, profile_name, profile_title], key=len)
    longest_name_parts = longest_name.split()

    ignore_name_parts = ['Coach', 'Sister', 'Chef', 'Mayor', 'Master', 'Admiral', 'Captain', 'Nurse', '(character)']
    sanitized_name_parts = [x.strip('(').strip(')') for x in longest_name_parts if x not in ignore_name_parts]
    sanitized_full_name = " ".join(sanitized_name_parts)

    first_name = None
    last_name = None
    full_name = None

    if longest_name == "Main character":
        first_name = name
        last_name = ""
        full_name = name
    elif len(sanitized_name_parts) == 1:
        first_name = sanitized_name_parts[0]
        last_name = ""
        full_name = sanitized_full_name
    elif len(sanitized_name_parts) == 2:
        first_name = sanitized_name_parts[0]
        last_name = sanitized_name_parts[1]
        full_name = sanitized_full_name
    elif len(sanitized_name_parts) == 3:
        if sanitized_name_parts[0] == "Dr.":
            first_name = sanitized_name_parts[1]
            last_name = sanitized_name_parts[2]
        else:
            first_name = sanitized_name_parts[0]
            last_name = sanitized_name_parts[2]
        full_name = sanitized_full_name
    else:
        first_name = sanitized_name_parts[0]
        last_name = sanitized_name_parts[-1]
        full_name = sanitized_full_name

    return Character(
        _id=uuid.uuid5(source_id, result["profile_url"]),
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        profile_url=result["profile_url"],
        profile_picture_url=result["thumbnail_url"],
    )
