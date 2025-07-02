import os
import requests
import tempfile
from bs4 import BeautifulSoup
from urllib.parse import urljoin

PDF_LIST_URL = "https://www.gov.uk/government/publications/ufo-reports-in-the-uk"


def fetch_pdfs_node(state):
    temp_dir = tempfile.gettempdir()
    pdf_dir = os.path.join(temp_dir, "ufo_pdfs")
    os.makedirs(pdf_dir, exist_ok=True)
    print(f"Fetching PDF links from {PDF_LIST_URL} ...")
    response = requests.get(PDF_LIST_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    pdf_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            full_url = urljoin(PDF_LIST_URL, href)
            pdf_links.append(full_url)
    print(f"Found {len(pdf_links)} PDF links.")

    # Deduplicate links
    pdf_links = list(dict.fromkeys(pdf_links))

    downloaded_files = []
    for url in pdf_links:
        filename = os.path.join(pdf_dir, os.path.basename(url))
        print(f"Downloading {url} to {filename} ...")
        r = requests.get(url)
        with open(filename, "wb") as f:
            f.write(r.content)
        downloaded_files.append(filename)

    # Deduplicate downloaded files (in case different URLs have the same filename)
    downloaded_files = list(dict.fromkeys(downloaded_files))

    return {
        **state,
        "pdf_files": downloaded_files,
        "pdf_path": downloaded_files[0] if downloaded_files else None,
    }
