import streamlit as st
# import asyncio
# import json
# import math
# from collections import defaultdict
# from typing import Dict, List
# import re
# import httpx
# from parsel import Selector

# session = httpx.AsyncClient(
#     timeout=httpx.Timeout(30.0),
#     cookies={"tldp": "1"},
#     follow_redirects=True,
# )


# def find_json_objects(text: str, decoder=json.JSONDecoder()):
#     """Find JSON objects in text, and generate decoded JSON data and it's ID"""
#     pos = 0
#     while True:
#         match = text.find("{", pos)
#         if match == -1:
#             break
#         try:
#             result, index = decoder.raw_decode(text[match:])
#             # backtrack to find the key/identifier for this json object:
#             key_end = text.rfind('"', 0, match)
#             key_start = text.rfind('"', 0, key_end)
#             key = text[key_start + 1 : key_end]
#             yield key, result
#             pos = match + index
#         except ValueError:
#             pos = match + 1


# def extract_apollo_cache(html):
#     """Extract apollo graphql cache data from HTML source"""
#     selector = Selector(text=html)
#     script_with_cache = selector.xpath("//script[contains(.,'window.appCache')]/text()").get()
#     cache = defaultdict(list)
#     for key, data in find_json_objects(script_with_cache):
#         cache[key].append(data)
#     return cache


# def parse_jobs(html) -> List[Dict]:
#     """parse jobs page for job data and total amount of jobs"""
#     cache = extract_apollo_cache(html)
#     return [v["jobview"] for v in cache["JobListingSearchResult"]]


# def parse_job_page_count(html) -> int:
#     """parse job page count from pagination details in Glassdoor jobs page"""
#     _total_results = Selector(html).css(".paginationFooter::text").get()
#     if not _total_results:
#         return 1
#     _total_results = int(_total_results.split()[-1])
#     _total_pages = math.ceil(_total_results / 40)
#     return _total_pages

# def find_companies(query: str):
#     """find company Glassdoor ID and name by query. e.g. "ebay" will return "eBay" with ID 7853"""
#     result = httpx.get(
#         url=f"https://www.glassdoor.com/searchsuggest/typeahead?numSuggestions=8&source=GD_V2&version=NEW&rf=full&fallback=token&input={query}",
#     )
#     data = json.loads(result.content)
#     return data[0]["suggestion"], data[0]["employerId"]

# def extract_apollo_state(html):
#     """Extract apollo graphql state data from HTML source"""
#     data = re.findall('apolloState":\s*({.+})};', html)[0]
#     return json.loads(data)


# def scrape_overview(company_name: str, company_id: int) -> dict:
#     url = f"https://www.glassdoor.com/Overview/Worksgr-at-{company_name}-EI_IE{company_id}.htm"
#     response = httpx.get(url, cookies={"tldp": "1"}, follow_redirects=True) 
#     apollo_state = extract_apollo_state(response.text)
#     return next(v for k, v in apollo_state.items() if k.startswith("Employer:"))


# # print(json.dumps(scrape_overview("7853"), indent=2))


# async def scrape_jobs(employer_name: str, employer_id: str):
#     """Scrape job listings"""
#     # scrape first page of jobs:
#     first_page = await session.get(
#         url=f"https://www.glassdoor.com/Jobs/{employer_name}-Jobs-E{employer_id}_P1.htm?filter.countryId={session.cookies.get('tldp') or 0}",
#     )
#     jobs = parse_jobs(first_page.text)
#     total_pages = parse_job_page_count(first_page.text)

#     st.write(f"scraped first page of jobs, scraping remaining {total_pages - 1} pages")
#     other_pages = [
#         session.get(
#             url=str(first_page.url).replace(".htm", f"_P{page}.htm"),
#         )
#         for page in range(2, total_pages + 1)
#     ]
#     for page in await asyncio.gather(*other_pages):
#         jobs.extend(parse_jobs(page.text))
#     return jobs




# # async def scrape_reviews(employer: str, employer_id: str, session: httpx.AsyncClient):
# #     """Scrape job listings"""
# #     # scrape first page of jobs:
# #     first_page = await session.get(
# #         url=f"https://www.glassdoor.com/Reviews/{employer}-Reviews-E{employer_id}_P1.htm",
# #     )
# #     reviews = parse_reviews(first_page.text)
# #     # find total amount of pages and scrape remaining pages concurrently
# #     total_pages = reviews["numberOfPages"]
# #     print(f"scraped first page of reviews, scraping remaining {total_pages - 1} pages")
# #     other_pages = [
# #         session.get(
# #             url=str(first_page.url).replace("_P1.htm", f"_P{page}.htm"),
# #         )
# #         for page in range(2, total_pages + 1)
# #     ]
# #     for page in await asyncio.gather(*other_pages):
# #         page_reviews = parse_reviews(page.text)
# #         reviews["reviews"].extend(page_reviews["reviews"])
# #     return reviews


# async def main():
#     company_name = st.text_input('Enter Company name')
#     if company_name:
#         x= find_companies(company_name)
#         st.write("company ID :",x[1])
#         st.subheader("Job Listing")
#         jobs = await scrape_jobs(x[0], x[1])     
#         st.json(json.dumps(jobs, indent=2,sort_keys=True))   
#     # st.sub_header("Company Overview")
#     # st.write(json.dumps(scrape_overview(x[1]), indent=2))
#     # st.subheader("Company Reviews")
    
#     # region_name = st.text_input('Enter region name')
#     # Job_name = st.text_input('Enter Job name')

#     # st.subheader("Job Listing")
#     # jobs = await scrape_jobs(x[0], x[1])
#     # st.write(json.dumps(jobs, indent=2,sort_keys=True))


# asyncio.run(main())



import asyncio
import re
import json
from typing import Tuple, List, Dict
import httpx


def extract_apollo_state(html):
    """Extract apollo graphql state data from HTML source"""
    data = re.findall('apolloState":\s*({.+})};', html)
    data = json.loads(data[0])
    return data


def parse_reviews(html) -> Tuple[List[Dict], int]:
    """parse jobs page for job data and total amount of jobs"""
    cache = extract_apollo_state(html)
    xhr_cache = cache["ROOT_QUERY"]
    reviews = next(v for k, v in xhr_cache.items() if k.startswith("employerReviews") and v.get("reviews"))
    return reviews


async def scrape_reviews(employer: str, employer_id: str, session: httpx.AsyncClient):
    """Scrape job listings"""
    # scrape first page of jobs:
    first_page = await session.get(
        url=f"https://www.glassdoor.com/Reviews/{employer}-Reviews-E{employer_id}_P1.htm",
    )
    reviews = parse_reviews(first_page.text)
    # find total amount of pages and scrape remaining pages concurrently
    total_pages = reviews["numberOfPages"]
    print(f"scraped first page of reviews, scraping remaining {total_pages - 1} pages")
    other_pages = [
        session.get(
            url=str(first_page.url).replace("_P1.htm", f"_P{page}.htm"),
        )
        for page in range(2, total_pages + 1)
    ]
    for page in await asyncio.gather(*other_pages):
        page_reviews = parse_reviews(page.text)
        reviews["reviews"].extend(page_reviews["reviews"])
    return reviews


async def main():
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        cookies={"tldp": "1"},
        follow_redirects=True,
    ) as client:
        reviews = await scrape_reviews("eBay", "7853", client)
        st.json(json.dumps(reviews, indent=2))


asyncio.run(main())