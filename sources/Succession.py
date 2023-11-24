import uuid
from uuid import UUID

import scrapy
from knack.log import get_logger
from scrapy.crawler import CrawlerProcess

from source import Character, CharacterType, CharacterSource

logger = get_logger(__name__)


succession_source = CharacterSource(
    UUID('fbf22d6e-8430-4a1c-90d1-4184a79a5613'),
    "Succession",
    "Succession")

waystar_royco_source = CharacterSource(
    UUID('1ea46892-3343-41d7-b68c-7750a2fb863f'),
    "Waystar",
    "Waystar Royco")

pierce_global_media_source = CharacterSource(
    UUID('13157aed-a412-47b3-8a06-5c9c4c8f5d41'),
    "PGM",
    "Pierce Global Media")

furness_media_groups_source = CharacterSource(
    UUID('fec58333-7004-4466-8a46-b9f81df112aa'),
    "FMG",
    "Furness Media Groups")

maesbury_capital_source = CharacterSource(
    UUID('c691f4de-f23c-4911-a6e6-99f83aa482e4'),
    "Maesbury",
    "Maesbury Capital")


class CharacterListSpider(scrapy.Spider):
    name = "CharacterListSpider"
    start_urls = ["https://succession.fandom.com/wiki/Category:Characters"]

    def parse(self, response, **kwargs):
        for characterListSelector in ['//*[@id="mw-content-text"]/div[3]']:
            for characterList in response.xpath(characterListSelector):
                for characterGroup in characterList.xpath('div'):
                    for character in characterGroup.xpath("ul/li"):
                        href = character.xpath('a/@href').get()
                        name = character.xpath('a/text()').get()
                        if name.startswith("Category:"):
                            yield response.follow(href, self.parse, *kwargs)
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

    def parse_profile(self, response, profile: dict[str, str]):
        infobox = response.xpath('//*[@id="mw-content-text"]/div/p/aside')
        profile["title"] = response.xpath('//*[@id="firstHeading"]/span/text()').get()
        profile["name"] = infobox.xpath('h2/text()').get()
        profile["full_length_portrait_url"] = response.urljoin(
            infobox.xpath('figure/a/img/@src').get()
        )

        for information in infobox.xpath('section/div'):
            information_name = information.xpath('h3/text()').get()
            information_value = "".join(information.xpath("div//text()").extract())

            if information_name is not None and information_value is not None:
                information_name = information_name.lower().strip().replace(" ", "_")
                information_value = information_value.strip()

                if information_name == 'job_title':
                    profile["job_title"] = information_value
                elif information_name == 'gender':
                    profile["gender"] = information_value
                elif information_name == 'romances':
                    # Follow
                    pass
                elif information_name == 'family':
                    # Follow
                    pass


def has_portrait_url(x):
    if x is None:
        return False

    if x["profile"] is None:
        return False

    if x["profile"].get("full_length_portrait_url") is None:
        return False

    return True


def fetch_source():
    process = CrawlerProcess()
    results = []
    process.crawl(CharacterListSpider)

    def crawler_results(item, response, spider):
        results.append(item)

    for p in process.crawlers:
        p.signals.connect(crawler_results, signal=scrapy.signals.item_scraped)

    process.start()

    results = filter(has_portrait_url, results)
    characters = list(map(dict_to_character, results))

    characters = [item for sublist in characters for item in sublist]

    grouped_dict = {}
    for character in characters:
        character_source = grouped_dict.setdefault(character[0].ID, character[0])
        character_source.Characters.append(character[1])

    grouped_characters = list(grouped_dict.values())

    return grouped_characters


def convert_character_type(last_name, job_titles):
    if last_name.casefold() == 'Roy'.casefold():
        return CharacterType.PROTAGONIST

    for job_title in job_titles:
        is_former = 'former'.casefold() in job_title.casefold()
        is_CEO = 'CEO'.casefold() in job_title.casefold() or 'Chief Operating Officer'.casefold() in job_title.casefold()
        is_founder = 'founder'.casefold() in job_title.casefold()

        if not is_former:
            if is_CEO or is_founder:
                return CharacterType.PROTAGONIST

    return CharacterType.UNKNOWN


def get_company_source(profile_job_title):
    waystar_and_divisions = [
        "Waystar",
        "ATN", "NCN", "LNN",
        "North Star Publishing",
        "Brightstar Adventure Park", "Brightstar Cruise Lines", 'Brightstar Cruises', "Living+",
        "Waystar Studios", "Vaulter", "StarGo"]

    maesbury_and_divisions = [
        "Maesbury"]

    PGM_and_divisions = [
        "PGM"]

    FMG_and_divisions = [
        "FMG"]

    if profile_job_title is '':
        return None

    if any(element in profile_job_title for element in waystar_and_divisions):
        return waystar_royco_source

    if any(element in profile_job_title for element in PGM_and_divisions):
        return pierce_global_media_source

    if any(element in profile_job_title for element in FMG_and_divisions):
        return furness_media_groups_source

    if any(element in profile_job_title for element in maesbury_and_divisions):
        return maesbury_capital_source

    return None


def dict_to_character(result):
    name = result["name"].strip()
    profile = result["profile"]
    profile_name = profile.get("name", "")
    profile_title = profile.get("title", "")
    profile_job_title = profile.get('job_title', "")
    job_titles = profile_job_title.split(',')
    name_parts = name.split()

    first_name = name_parts[0]
    last_name = name_parts[-1]
    full_name = name

    if profile_job_title is "":
        job_titles = []

    company_source = get_company_source(profile_job_title)

    character_type = convert_character_type(last_name, job_titles)

    character = Character(
        _id=uuid.uuid5(succession_source.ID, result["profile_url"]),
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        _type=character_type,
        profile_url=result["profile_url"],
        profile_picture_url=profile["full_length_portrait_url"])

    characters = [(succession_source, character)]

    if company_source is not None:
        characters.append((company_source, Character(
            _id=uuid.uuid5(company_source.ID, result["profile_url"]),
            first_name=first_name,
            last_name=last_name,
            full_name=full_name,
            _type=character_type,
            profile_url=result["profile_url"],
            profile_picture_url=profile["full_length_portrait_url"])))

    return characters
