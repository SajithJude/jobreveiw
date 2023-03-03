

import streamlit as st
import asyncio
import re
import json
from typing import Tuple, List, Dict
import httpx
import pandas as pd


def extract_apollo_state(html):
    """Extract apollo graphql state data from HTML source"""
    data = re.findall('apolloState":\s*({.+})};', html)[0]
    data = json.loads(str(data))
    # st.write(data)
    return data


def parse_reviews(html) -> Tuple[List[Dict], int]:
    """parse jobs page for job data and total amount of jobs"""
    reviews = extract_apollo_state(html)
    # xhr_cache = cache
    
    return reviews


async def scrape_reviews(employer: str, employer_id: str, session: httpx.AsyncClient):
    """Scrape job listings"""
    # scrape first page of jobs:
    first_page = await session.get(
        url=f"https://www.glassdoor.com/Reviews/{employer}-Reviews-E{employer_id}_P1.htm",
    )
    reviews = parse_reviews(first_page.text)
    
    # find total amount of pages and scrape remaining pages concurrently
    # total_pages = reviews["numberOfPages"]
    # print(f"scraped first page of reviews, scraping remaining {total_pages - 1} pages")
    # other_pages = [
    #     session.get(
    #         url=str(first_page.url).replace("_P1.htm", f"_P{page}.htm"),
    #     )
    #     for page in range(2, total_pages + 1)
    # ]
    # for page in await asyncio.gather(*other_pages):
    #     page_reviews = parse_reviews(page.text)
    #     reviews["reviews"].extend(page_reviews["reviews"])
    return reviews

# @st.cache
async def main():
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(60.0),
        cookies={"tldp": "1"},
        follow_redirects=True,
    ) as client:
        reviews = await scrape_reviews("eBay", "7853", client)
        jsonrev = list(reviews["ROOT_QUERY"].values())[10]

    # if "reviews" in jsonrev:
    #     reviews_array = jsonrev[7]
    #     st.write(reviews_array)
    # else:
    #     st.write("No reviews found")
        # emp_reviews = reviews["employerReviews"]
        # list_reviews = reviews["reviews"]

        # st.write(emp_reviews)
        # st.write(list_reviews)

        # df =  pd.json_normalize(reviews)
        # df = pd.DataFrame(json.dumps(reviews, indent=2))
        st.json(json.dumps(jsonrev, indent=2))
        # st.json(json.dumps(reviews, indent=2))
       
asyncio.run(main())