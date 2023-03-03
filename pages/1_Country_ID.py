

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
    return reviews

# @st.cache
async def main():
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(60.0),
        cookies={"tldp": "1"},
        follow_redirects=True,
    ) as client:
        CompanyName = st.sidebar.text_input('Enter Company Name')
        if CompanyName:
            comp_ID=st.sidebar.write(find_companies(CompanyName))
        reviews = await scrape_reviews(CompanyName, comp_ID, client)
        jsonrev = list(reviews["ROOT_QUERY"].values())[7]["reviews"]
        # Extract the desired keys and create a list of dictionaries
        # data = []
        # for item in jsonrev:
        #     row = {
        #         "reviewDateTime": item.get("reviewDateTime", None),
        #         "pros": item.get("pros", None),
        #         "cons": item.get("cons", None),
        #     }
        #     data.append(row)

        # # Create a pandas DataFrame from the list of dictionaries
        # df = pd.DataFrame(data)
        # st.table(df)
        st.json(json.dumps(jsonrev, indent=2))
        # st.json(json.dumps(reviews, indent=2))
       
asyncio.run(main())