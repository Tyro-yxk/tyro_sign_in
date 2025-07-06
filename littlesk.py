import os
import json
import time
import re
import requests
from requests.cookies import RequestsCookieJar

from notify import notify

# Configuration
BASE_URL = 'https://littleskin.cn/'
MAX_RETRY = 3
RETRY_DELAY = 10  # seconds


def load_credentials():
    """Load credentials from environment variable"""
    creds = os.getenv('USER_LITTLESK')
    if not creds:
        raise ValueError("USER_INFO environment variable not set")
    return json.loads(creds)


# def load_headers():
#     """Load headers from headers.json file"""
#     try:
#         with open('headers.json', 'r', encoding='utf-8') as f:
#             return json.load(f)
#     except FileNotFoundError:
#         raise FileNotFoundError("headers.json file not found")
#     except json.JSONDecodeError:
#         raise ValueError("Invalid JSON in headers.json")


def extract_csrf(page_text):
    """Extract CSRF token from HTML page"""
    match = re.search(r'<meta name="csrf-token" content="(\w+)">', page_text)
    if not match:
        raise ValueError("CSRF token not found in page")
    return match.group(1)


def build_url(path):
    """Build full URL from path"""
    return BASE_URL + path.lstrip('/')


def perform_login(session, credentials, headers):
    """Perform login to LittleSkin"""
    # Get login page to obtain CSRF token
    login_url = build_url('auth/login')
    home_page = session.get(login_url)
    home_page.raise_for_status()
    csrf = extract_csrf(home_page.text)

    time.sleep(0.5)

    # Perform login
    login_data = {
        'identification': credentials['handle'],
        'keep': False,
        'password': credentials['password']
    }
    login_headers = headers.copy()
    login_headers['X-CSRF-TOKEN'] = csrf

    login_response = session.post(login_url, data=login_data, headers=login_headers)
    login_response.raise_for_status()

    return csrf


def perform_sign(session, headers):
    """Perform daily sign"""
    # Get user page to obtain new CSRF token
    user_url = build_url('user')
    user_page = session.get(user_url)
    user_page.raise_for_status()
    csrf = extract_csrf(user_page.text)

    time.sleep(0.5)

    # Perform sign
    sign_url = build_url('user/sign')
    sign_headers = headers.copy()
    sign_headers['X-CSRF-TOKEN'] = csrf

    sign_response = session.post(sign_url, headers=sign_headers)
    sign_response.raise_for_status()

    return sign_response.json()


def run_task():
    """Main task to perform login and sign"""
    credentials = load_credentials()
    headers = {
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.7,zh-TW;q=0.5,zh-HK;q=0.3,en;q=0.2",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
    }

    session = requests.Session()
    session.cookies = RequestsCookieJar()
    session.headers.update(headers)

    csrf = perform_login(session, credentials, headers)
    time.sleep(0.2)

    result = perform_sign(session, headers)
    print(result)
    notify.send_success("LITTLESK皮肤站签到", f"签到成功，获得{result['message']} 积分")
    if result['code'] != 0:
        notify.send_failure("LITTLESK皮肤站签到", result['message'])
        raise Exception(result['message'])


def main():
    """Main function with retry logic"""
    for attempt in range(MAX_RETRY):
        try:
            run_task()
            break
        except Exception as err:
            print(f"Attempt {attempt + 1} failed: {err}")
            if attempt < MAX_RETRY - 1:
                time.sleep(RETRY_DELAY)
            else:
                raise Exception("签到失败")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)
