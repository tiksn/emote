import uuid
from uuid import UUID

from source import Character
import scrapy
from scrapy.crawler import CrawlerProcess
from knack.log import get_logger

logger = get_logger(__name__)

source_id = UUID('a3ab469a-a790-457e-9f03-d5d3936e80d6')
source_name = "The Life & Times of Tim"
