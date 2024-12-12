import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Function to check validity of the URL
def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

# Function to scrape links from website
def extract_links(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    links = set()
    for anchor in soup.find_all('a', href=True):
        href = anchor['href']
        links.add(requests.compat.urljoin(url, href))
    return list(links)


# Function to obtain full texts from links using BeautifulSoup
def scrape_links_full_text(links):
    """
    Takes a list of links and scrapes the complete text content using BeautifulSoup.

    Args:
    - links (list): A list of URLs to scrape.

    Returns:
    - dict: A dictionary containing the URL and scraped text content.
    """
    scraped_data = {}

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    links = [link for link in links if is_valid_url(link)]

    for link in links:
        try:
            # Request the content of the URL
            response = requests.get(link, headers=headers)
            response.raise_for_status()  # Raise an HTTPError for bad responses

            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract the full text content of the page
            full_text = soup.get_text(separator='\n', strip=True)

            # Store scraped information in dictionary
            scraped_data[link] = {
                "full_text": full_text
            }

        except requests.exceptions.RequestException as e:
            # Handle request exceptions (e.g., network issues, page not found)
            scraped_data[link] = {
                "error": f"Failed to retrieve page: {str(e)}"
            }

    return scraped_data