import requests
from bs4 import BeautifulSoup
import streamlit as st

# Define Glassdoor URL and user agent
url = "https://www.glassdoor.com/Job/jobs.htm"
headers = {"User-Agent": "Mozilla/5.0"}

# Define Streamlit app
st.title("Glassdoor Job Scraper")

# Define form inputs
search_term = st.text_input("Enter a job title")
location = st.text_input("Enter a location")

# Define data dictionary to store scraped data
data = {"Job Title": [], "Company Name": [], "Location": [], "Job Link": []}

# Check if form is submitted
if st.button("Search"):
    # Define query parameters
    params = {
        "keyword": search_term,
        "location": location,
        "fromAge": "30d",
        "jobType": "fulltime",
    }
    
    # Make GET request to Glassdoor URL with query parameters and user agent
    response = requests.get(url, params=params, headers=headers)
    st.write(response)
    # Parse HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find all job listings on page
    job_listings = soup.find_all("li", class_="react-job-listing")
    
    # Loop through job listings and extract data
    for job in job_listings:
        # Extract job title
        job_title = job.find("a", class_="jobLink").text
        data["Job Title"].append(job_title)
        
        # Extract company name
        company_name = job.find("div", class_="jobHeader").find("span").text
        data["Company Name"].append(company_name)
        
        # Extract job location
        job_location = job.find("div", class_="jobInfoItem jobLocation").text
        data["Location"].append(job_location)
        
        # Extract job link
        job_link = "https://www.glassdoor.com" + job.find("a", class_="jobLink")["href"]
        data["Job Link"].append(job_link)
        
    # Display scraped data in Streamlit table
    st.table(data)
