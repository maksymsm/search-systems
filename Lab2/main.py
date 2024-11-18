import os
import networkx as nx
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
import json
import base64
import matplotlib.pyplot as plt
import seaborn as sns



VIRUSTOTAL_API_KEY = 'fe76de746b9a1ca6b389f0c0c27ad9fa57f47f1a910d5ff422c68bc11093e370'
OPENPAGERANK_API_KEY = '4848csccso044goco4soso0w08o8s8kg44ssck8c'

if not VIRUSTOTAL_API_KEY:
    raise ValueError("VirusTotal API key not found. Please set the 'VIRUSTOTAL_API_KEY' environment variable.")


def scrape_links(url):
    """Scrape all links from the given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if href.startswith('/'):
            href = requests.compat.urljoin(url, href)
        links.append(href)
    return links


def filter_links(base_url, links):
    """Filter links into internal and external based on the base URL."""
    parsed_base = urlparse(base_url)
    internal = []
    external = []
    for link in links:
        parsed_link = urlparse(link)
        if parsed_link.netloc == '':
            internal.append(requests.compat.urljoin(base_url, link))
        elif parsed_link.netloc == parsed_base.netloc:
            internal.append(link)
        else:
            external.append(link)
    return internal, external


def check_link_status(url):
    """Check the HTTP status code of a URL."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        return response.status_code
    except requests.RequestException:
        return None


def check_links_concurrently(urls):
    """Check statuses of multiple URLs concurrently."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        statuses = list(executor.map(check_link_status, urls))
    return statuses


def get_pagerank(urls, base_url, internal_links):
    """Calculate PageRank for the given URLs."""
    G = nx.DiGraph()
    G.add_node(base_url)
    for link in internal_links:
        G.add_node(link)
        G.add_edge(base_url, link)

    for url in urls:
        G.add_node(url)

    pagerank_scores = nx.pagerank(G, alpha=0.85)

    df_pagerank = pd.DataFrame(list(pagerank_scores.items()), columns=['URL', 'PageRank'])
    return df_pagerank


def check_virus_total(url):
    """Check if a URL is flagged by VirusTotal."""
    endpoint = 'https://www.virustotal.com/api/v3/urls'
    headers = {
        'x-apikey': VIRUSTOTAL_API_KEY,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    payload = {'url': url}
    try:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip('=')
        analysis_url = f"{endpoint}/{url_id}"

        analysis_response = requests.get(analysis_url, headers=headers)
        if analysis_response.status_code == 200:
            analysis_data = analysis_response.json()
            stats = analysis_data.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
            malicious = stats.get('malicious', 0)
            suspicious = stats.get('suspicious', 0)
            return malicious > 0 or suspicious > 0
        elif analysis_response.status_code == 404:
            submit_response = requests.post(endpoint, data=payload, headers=headers)
            if submit_response.status_code in [200, 202]:
                return False
        else:
            print(f"Unexpected status code {analysis_response.status_code} for URL {url}")
            return False
    except requests.RequestException as e:
        print(f"Error checking VirusTotal for {url}: {e}")
        return False


def check_virus_total_concurrently(urls):
    """Check multiple URLs against VirusTotal concurrently."""
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(check_virus_total, urls))
    return results


def calculate_metrics(df):
    """Calculate average PageRank."""
    df = df.dropna(subset=['PageRank'])
    avg_pagerank = df['PageRank'].astype(float).mean()
    return avg_pagerank


def get_main_domain_opr_info(domain):
    """Fetch and display Open PageRank information for the main domain."""
    headers = {'API-OPR': OPENPAGERANK_API_KEY}
    url = f'https://openpagerank.com/api/v1.0/getPageRank?domains%5B0%5D={domain}'

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data['status_code'] == 200 and data['response']:
            rank_data = data['response'][0]
            opr_score = rank_data.get('page_rank_decimal', 'N/A')
            rank = rank_data.get('rank', 'N/A')
            formatted_info = (
                f"Open PageRank Data for {domain}:\n"
                f"  - PageRank Score (Decimal): {opr_score}\n"
                f"  - Global Rank: {rank}\n"
                f"  - Domain: {rank_data.get('domain', 'N/A')}\n"
                f"  - Status Code: {rank_data.get('status_code', 'N/A')}"
            )
            print(formatted_info)
        else:
            print(f"No PageRank data available for {domain}.")
    except requests.RequestException as e:
        print(f"Error fetching Open PageRank for {domain}: {e}")

def main():
    url = 'https://www.ukr.net/'
    domain = urlparse(url).netloc

    print(f"Fetching Open PageRank for the main domain: {domain}")
    get_main_domain_opr_info(domain)

    print(f"Scraping links from {url}...")
    links = scrape_links(url)
    print(f"Total Links Found: {len(links)}")

    internal_links, external_links = filter_links(url, links)
    print(f"Internal Links: {len(internal_links)}")
    print(f"External Links: {len(external_links)}")

    print("Checking link statuses...")
    statuses = check_links_concurrently(external_links)
    df_links = pd.DataFrame({'URL': external_links, 'Status': statuses})

    broken_links = df_links[df_links['Status'] == 404]
    print(f"Broken Links: {len(broken_links)}")

    print("Calculating PageRank...")
    df_pagerank = get_pagerank(external_links, url, internal_links)
    print(df_pagerank.head())

    print("Calculating Average PageRank...")
    average_pagerank = calculate_metrics(df_pagerank)
    print(f"Average PageRank: {average_pagerank}")

    print("Checking VirusTotal Safe Browsing...")
    df_links['Is_Safe'] = check_virus_total_concurrently(df_links['URL'])
    safe_links = df_links[df_links['Is_Safe'] == False]
    print(f"Unsafe Links: {len(safe_links)}")

    df_merged = pd.merge(df_links, df_pagerank, on='URL', how='left')
    df_merged['PageRank'] = df_merged['PageRank'].fillna(0)

    image_files = []

    plt.figure(figsize=(10, 6))
    sns.histplot(df_pagerank['PageRank'].dropna(), bins=20, kde=True, color='skyblue')
    plt.title('Розподіл PageRank')
    plt.xlabel('PageRank')
    plt.ylabel('Частота')
    plt.tight_layout()
    image_path = 'pagerank_distribution.png'
    plt.savefig(image_path)
    image_files.append(image_path)
    plt.show()
    plt.close()

    plt.figure(figsize=(10, 6))
    status_counts = df_links['Status'].value_counts().reset_index(name='Count')
    status_counts.columns = ['Status', 'Count']
    sns.barplot(x='Status', y='Count', data=status_counts, palette='viridis')
    plt.title('Статуси Посилань')
    plt.xlabel('Статус HTTP')
    plt.ylabel('Кількість')
    plt.tight_layout()
    image_path = 'status_counts.png'
    plt.savefig(image_path)
    image_files.append(image_path)
    plt.show()
    plt.close()

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='PageRank', y='Is_Safe', data=df_merged, hue='Is_Safe', palette='viridis')
    plt.title('Відношення PageRank до Безпеки Посилань')
    plt.xlabel('PageRank')
    plt.ylabel('Is Safe')
    plt.tight_layout()
    image_path = 'pagerank_vs_safety.png'
    plt.savefig(image_path)
    image_files.append(image_path)
    plt.show()
    plt.close()

    plt.figure(figsize=(8, 8))
    labels = ['Unsafe Links', 'Broken Links']
    sizes = [len(safe_links), len(broken_links)]
    colors = ['#66b3ff', '#ff9999']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    plt.title('Розподіл Безпечних та Битих Посилань')
    plt.axis('equal')
    plt.tight_layout()
    image_path = 'link_safety_distribution.png'
    plt.savefig(image_path)
    image_files.append(image_path)
    plt.show()
    plt.close()


    with pd.ExcelWriter('link_analysis_report.xlsx', engine='xlsxwriter') as writer:
        df_links.to_excel(writer, sheet_name='Links', index=False)
        df_pagerank.to_excel(writer, sheet_name='PageRank', index=False)
        safe_links.to_excel(writer, sheet_name='Unsafe_Links', index=False)
        broken_links.to_excel(writer, sheet_name='Broken_Links', index=False)

        workbook = writer.book
        worksheet = workbook.add_worksheet("Charts")


        for idx, image_file in enumerate(image_files):
            worksheet.insert_image(f'A{1 + idx * 20}', image_file)

    print("Report generated: link_analysis_report.xlsx")




if __name__ == "__main__":
    main()
