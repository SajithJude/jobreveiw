import streamlit as st
import json
import httpx
import re


response = httpx.get(
    "https://www.glassdoor.com/",
    follow_redirects=True,
)
country_data = re.findall(r'"countryMenu\\":.+?(\[.+?\])', response.text)[0].replace('\\', '')
country_data = json.loads(country_data)


def find_companies(query: str):
    """find company Glassdoor ID and name by query. e.g. "ebay" will return "eBay" with ID 7853"""
    result = httpx.get(
        url=f"https://www.glassdoor.com/searchsuggest/typeahead?numSuggestions=8&source=GD_V2&version=NEW&rf=full&fallback=token&input={query}",
    )
    data = json.loads(result.content)
    return data[0]["suggestion"], data[0]["employerId"]

        
        
CompanyName = st.sidebar.text_input('Enter Company Name')
if CompanyName:
    comp_ID= find_companies(CompanyName)
    st.sidebar.write(comp_ID)
