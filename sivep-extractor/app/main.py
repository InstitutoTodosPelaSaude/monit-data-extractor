import requests
from bs4 import BeautifulSoup

def fetch_html(url):
    """
    Makes a request to fetch the HTML content of a page.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # Checks for request errors
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the page's HTML: {e}")
        return None

def extract_csv_public_links(html):
    """
    Extracts all links (href attributes) from the provided HTML content.
    :param html: String containing the HTML content.
    :return: List of strings with the values of href attributes.
    """
    soup = BeautifulSoup(html, 'html.parser')
    hrefs = [a.get('href') for a in soup.find_all('a', href=True, class_="dropdown-item resource-url-analytics")]
    hrefs = [ href for href in hrefs if href.endswith('.csv') ]
    return hrefs

# Example usage
url = 'https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024'  # Replace with the desired URL

# Fetch the HTML
html_content = fetch_html(url)
if html_content:
    # Extract the links
    links = extract_csv_public_links(html_content)
    print("Links found:")
    for link in links:
        print(link)
