import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re

# Function to fetch the content of a URL
def fetch_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        st.error(f"Error fetching URL: {e}")
        return None

# Function to find sitemaps from robots.txt
def find_sitemaps_from_robots(robots_txt_url):
    content = fetch_url(robots_txt_url)
    if content:
        # Enhanced regex to find sitemap URLs
        sitemap_urls = re.findall(r'Sitemap:\s*(https?://[^\s]+)', content, re.IGNORECASE)
        return sitemap_urls
    return []

# Function to find sitemaps from sitemap.xml
def find_sitemaps_from_sitemap(sitemap_url):
    content = fetch_url(sitemap_url)
    if content:
        soup = BeautifulSoup(content, 'xml')
        sitemap_urls = [loc.text for loc in soup.find_all('sitemap')]
        return sitemap_urls
    return []

# Function to fetch and parse the sitemap
def fetch_sitemap(url):
    content = fetch_url(url)
    if content:
        soup = BeautifulSoup(content, 'xml')
        urls = [loc.text for loc in soup.find_all('loc')]
        return urls
    return []

# Main function to run the Streamlit app
def main():
    st.title("Sitemap Checker")

    # Use a form to enable Enter key press
    with st.form(key='sitemap_form'):
        website_url = st.text_input("Enter Website URL", "https://example.com")
        submit_button = st.form_submit_button("Check Sitemap")

    if submit_button:
        if website_url:
            parsed_url = urlparse(website_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                st.error("Invalid URL. Please enter a valid website URL.")
            else:
                # Fetch the robots.txt file
                robots_txt_url = urljoin(website_url, '/robots.txt')
                st.write(f"Fetching robots.txt from {robots_txt_url}...")
                sitemap_urls = find_sitemaps_from_robots(robots_txt_url)

                # Try common sitemap locations if no sitemaps are found
                if not sitemap_urls:
                    common_sitemap_urls = [
                        '/sitemap.xml',
                        '/sitemap_index.xml',
                        '/sitemap/sitemap.xml',
                        '/sitemap1.xml',
                        '/sitemap2.xml'
                    ]
                    for path in common_sitemap_urls:
                        sitemap_xml_url = urljoin(website_url, path)
                        st.write(f"Fetching possible sitemap from {sitemap_xml_url}...")
                        sitemap_urls = find_sitemaps_from_sitemap(sitemap_xml_url)
                        if sitemap_urls:
                            break

                if sitemap_urls:
                    st.write(f"Found {len(sitemap_urls)} sitemap(s):")
                    all_urls = set()  # Use a set to avoid duplicates
                    for sitemap_url in sitemap_urls:
                        full_sitemap_url = urljoin(website_url, sitemap_url)
                        st.write(f"Fetching sitemap: {full_sitemap_url}...")
                        urls = fetch_sitemap(full_sitemap_url)
                        all_urls.update(urls)
                    
                    if all_urls:
                        st.write(f"Found {len(all_urls)} URLs:")
                        for url in all_urls:
                            st.write(url)
                    else:
                        st.write("No URLs found or unable to fetch sitemaps.")
                else:
                    st.write("No sitemaps found in robots.txt or common locations. Ensure that the sitemap URLs are listed correctly.")
        else:
            st.error("Please enter a URL.")

if __name__ == "__main__":
    main()
