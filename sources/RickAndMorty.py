import uuid
from uuid import UUID

import scrapy
from knack.log import get_logger
from scrapy.crawler import CrawlerProcess

from source import Character, CharacterType

logger = get_logger(__name__)

source_id = UUID('6dc09d97-4a8a-47c8-9606-8fefec2c0dc6')
source_name = "Rick and Morty"


class CharacterListSpider(scrapy.Spider):
    name = "CharacterListSpider"
    start_urls = ["https://rickandmorty.fandom.com/wiki/Category:Characters"]

    def parse(self, response, **kwargs):
        for characterListSelector in ['//*[@id="mw-content-text"]/div[3]', '//*[@id="mw-content-text"]/div[2]']:
            for characterList in response.xpath(characterListSelector):
                for characterGroup in characterList.xpath('div'):
                    for character in characterGroup.xpath("ul/li"):
                        href = character.xpath('a/@href').get()
                        name = character.xpath('a/text()').get()
                        if name.startswith("Category:"):
                            # yield response.follow(href, self.parse, *kwargs)
                            pass
                        else:
                            profile_url = response.urljoin(
                                href
                            )
                            profile = dict()
                            yield scrapy.Request(profile_url, self.parse_profile, cb_kwargs={"profile": profile})
                            yield {
                                "name": name,
                                "profile": profile,
                                "profile_url": profile_url,
                                "thumbnail_url": response.urljoin(
                                    character.xpath('div/a/img/@src').get()
                                ),
                            }

        next_page = response.xpath(
            '//*[@id="mw-content-text"]/div[4]/a[contains(@class, "category-page__pagination-next")]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

        next_page = response.xpath(
            '//*[@id="mw-content-text"]/div[3]/a[contains(@class, "category-page__pagination-next")]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def parse_profile(self, response, profile: dict[str, str]):
        infobox = response.xpath('//*[@id="mw-content-text"]/div/p/aside')
        profile["title"] = response.xpath('//*[@id="firstHeading"]/span/text()').get()
        profile["name"] = infobox.xpath('h2/text()').get()
        profile["full_length_portrait_url"] = response.urljoin(
            infobox.xpath('figure/a/img/@src').get()
        )

        for information in infobox.xpath('section/div'):
            information_name = information.xpath('h3/text()').get()
            information_value = information.xpath('div/text()').get()

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


def convert_character_type(full_name):
    main_characters = [
        'Rick Sanchez',
        'Morty Smith',
        'Summer Smith',
        'Beth Smith',
        'Jerry Smith',
    ]

    for _, main_character in enumerate(main_characters):
        if full_name.casefold() == main_character.casefold():
            return CharacterType.PROTAGONIST

    return CharacterType.UNKNOWN


def dict_to_character(result):
    name = result["name"].strip()
    profile = result["profile"]
    profile_name = profile.get("name", "")
    profile_title = profile.get("title", "")

    name_parts = name.split()

    first_name = name_parts[0]
    last_name = name_parts[-1]
    full_name = name

    character_type = convert_character_type(full_name)

    return Character(
        _id=uuid.uuid5(source_id, result["profile_url"]),
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        _type=character_type,
        profile_url=result["profile_url"],
        profile_picture_url=profile["full_length_portrait_url"])
