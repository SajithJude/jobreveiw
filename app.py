import asyncio
import json
import math
from collections import defaultdict
from typing import Dict, List

import httpx
from parsel import Selector

session = httpx.AsyncClient(
    timeout=httpx.Timeout(30.0),
    cookies={"tldp": "1"},
    follow_redirects=True,
)


def find_json_objects(text: str, decoder=json.JSONDecoder()):
    """Find JSON objects in text, and generate decoded JSON data and it's ID"""
    pos = 0
    while True:
        match = text.find("{", pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            # backtrack to find the key/identifier for this json object:
            key_end = text.rfind('"', 0, match)
            key_start = text.rfind('"', 0, key_end)
            key = text[key_start + 1 : key_end]
            yield key, result
            pos = match + index
        except ValueError:
            pos = match + 1


def extract_apollo_cache(html):
    """Extract apollo graphql cache data from HTML source"""
    selector = Selector(text=html)
    script_with_cache = selector.xpath("//script[contains(.,'window.appCache')]/text()").get()
    cache = defaultdict(list)
    for key, data in find_json_objects(script_with_cache):
        cache[key].append(data)
    return cache


def parse_jobs(html) -> List[Dict]:
    """parse jobs page for job data and total amount of jobs"""
    cache = extract_apollo_cache(html)
    return [v["jobview"] for v in cache["JobListingSearchResult"]]


def parse_job_page_count(html) -> int:
    """parse job page count from pagination details in Glassdoor jobs page"""
    _total_results = Selector(html).css(".paginationFooter::text").get()
    if not _total_results:
        return 1
    _total_results = int(_total_results.split()[-1])
    _total_pages = math.ceil(_total_results / 40)
    return _total_pages


async def scrape_jobs(employer_name: str, employer_id: str):
    """Scrape job listings"""
    # scrape first page of jobs:
    first_page = await session.get(
        url=f"https://www.glassdoor.com/Jobs/{employer_name}-Jobs-E{employer_id}_P1.htm?filter.countryId={session.cookies.get('tldp') or 0}",
    )
    jobs = parse_jobs(first_page.text)
    total_pages = parse_job_page_count(first_page.text)

    print(f"scraped first page of jobs, scraping remaining {total_pages - 1} pages")
    other_pages = [
        session.get(
            url=str(first_page.url).replace(".htm", f"_P{page}.htm"),
        )
        for page in range(2, total_pages + 1)
    ]
    for page in await asyncio.gather(*other_pages):
        jobs.extend(parse_jobs(page.text))
    return jobs


async def main():
    jobs = await scrape_jobs("eBay", "7853")
    print(json.dumps(jobs, indent=2))


asyncio.run(main())
