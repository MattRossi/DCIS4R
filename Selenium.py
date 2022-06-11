from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from lxml import html

class BrowserUtils:
    @staticmethod
    def create_browser():
        options = Options()
        options.add_argument('--headless')
        options.add_argument("--log-level=3")
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    @staticmethod
    def kill_browser(browser):
        if browser:
            print('Killing browser...')
            browser.quit()
            print('Killed browser!')

    @staticmethod
    def open_url(browser, url):
        print('Opening {}'.format(url))
        browser.get(url)
        source = browser.page_source
        return (BeautifulSoup(source, 'lxml'), html.fromstring(source))