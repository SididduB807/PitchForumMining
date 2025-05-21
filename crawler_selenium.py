import os, time, urllib.parse as urlparse
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import configparser
import sys

counter = 1
baseURL = "http://pitchprash4aqilfr7sbmuwve3pnkpylqwxjbj2q5o4szcfeea6d27yd.onion"

# Local Configuration Handling
config = configparser.ConfigParser()
config.read('../../setup.ini')

if not config.has_section('Project') or not config.has_option('Project', 'shared_folder'):
    raise ValueError("Missing 'shared_folder' option in [Project] section of setup.ini")

CURRENT_DATE = str("%02d" % datetime.today().month) + str("%02d" % datetime.today().day) + str("%04d" % datetime.today().year)

def startCrawling():
    forum_name = getForumName()
    driver = getAccess()

    if driver != 'down':
        try:
            crawlForum(driver)
        except Exception as e:
            print(driver.current_url, e)
        closeDriver(driver)

def getForumName():
    return "Pitch"

def closeDriver(driver):
    print('Closing Tor...')
    try:
        driver.quit()
    except:
        pass
    time.sleep(3)

def createFFDriver():
    options = webdriver.FirefoxOptions()
    options.set_preference("network.proxy.type", 1)
    options.set_preference("network.proxy.socks_version", 5)
    options.set_preference('network.proxy.socks', '127.0.0.1')
    options.set_preference('network.proxy.socks_port', 9150)
    options.set_preference('network.proxy.socks_remote_dns', True)
    options.set_preference("javascript.enabled", True)

    service = Service(config.get('TOR', 'geckodriver_path'))

    driver = webdriver.Firefox(options=options, service=service)
    driver.maximize_window()

    print("Firefox WebDriver Initialized with Tor Proxy and Fresh Temporary Profile")

    return driver

def getAccess():
    driver = createFFDriver()
    attempts = 0

    while attempts < 5:
        try:
            print(f"[Attempt {attempts + 1}] Connecting to Pitch...")
            driver.get(baseURL)
            time.sleep(10)

            if "You have been placed in our access queue" in driver.page_source:
                print("🔄 Waiting in queue...")
                queue_start = time.time()
                while "You have been placed in our access queue" in driver.page_source:
                    time.sleep(5)
                    driver.refresh()
                queue_end = time.time()
                print(f"Exited queue after {int(queue_end - queue_start)} seconds.")

            if "Unable to connect" not in driver.page_source:
                print("Successfully connected to the Pitch forum.")
                return driver
            else:
                print("Connection Failed - Retrying...")

        except WebDriverException as e:
            print(f"[Access Error - Attempt {attempts + 1}]: {e}")
            closeDriver(driver)
            driver = createFFDriver()

        attempts += 1

    print("[Final Error]: Unable to connect to Pitch after several attempts.")
    return 'down'

def crawlForum(driver):
    print("Crawling the Pitch Forum")

    links_to_crawl = [
        f"{baseURL}/t/OpSec",
        f"{baseURL}/t/Markets",
        f"{baseURL}/t/Hacking"
    ]

    for link in links_to_crawl:
        print(f"Crawling: {link}")
        driver.get(link)
        time.sleep(5)

        # Keep clicking the "More" button until it disappears
        while True:
            try:
                more_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "More")]'))
                )
                driver.execute_script("arguments[0].click();", more_button)
                time.sleep(2)
            except (TimeoutException, NoSuchElementException):
                break

        savePage(driver, driver.page_source, link)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        threads = [urlparse.urljoin(baseURL, a['href']) for a in soup.find_all('a', href=True) if '/threads/' in a['href']]

        for thread in threads:
            driver.get(thread)
            time.sleep(5)
            savePage(driver, driver.page_source, thread)

    print("Pitch crawling complete.")

def savePage(driver, page, url):
    file_path = getFullPathName(url)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(page)

def getFullPathName(url):
    base_dir = os.path.join(config.get('Project', 'shared_folder'), f"Forums/{getForumName()}/HTML_Pages", CURRENT_DATE)
    filename = getNameFromURL(url)
    if isDescriptionLink(url):
        return os.path.join(base_dir, "Description", f"{filename}.html")
    else:
        return os.path.join(base_dir, "Listing", f"{filename}.html")

def getNameFromURL(url):
    filename = ''.join(e if e.isalnum() else '_' for e in url)
    return filename if filename else "default"

def isDescriptionLink(url):
    return '/threads/' in url

def crawler():
    startCrawling()

if __name__ == "__main__":
    startCrawling()
