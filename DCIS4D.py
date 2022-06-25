from datetime import datetime
from Selenium import BrowserUtils
from Organization import Orgs
import requests
from Webhook import Webhook
import json
import time
import configparser

today = datetime.now()
#today = datetime(2022, 6, 24)

config = configparser.ConfigParser()
config.read('config.properties')

def generate_post(parsed_shows, org):
    print('\n'.join([str(x) for x in parsed_shows]))
    for show in parsed_shows:
        print('Posting {}'.format(show.name))
        response = requests.post(
            url=config['DISCORD']['WEBHOOK'],
            data=json.dumps(Webhook.embedBuilder(show, org)),
            headers={'Content-Type': 'application/json'}
        )
        print('Response Code: {} | Response Content: {}'.format(response.status_code, response.content))
        time.sleep(5)

try:
    BROWSER = BrowserUtils.create_browser()
    for org in Orgs:
        shows = org.utils.full_schedule_parser(BrowserUtils.open_url(BROWSER, org.utils.schedule_url_generator(today)))
        print('{} Shows: '.format(org.name) + '\n'.join([str(x) for x in shows]))
        if shows:
            parsed_shows = org.utils.show_page_parser(BROWSER, shows)
            generate_post(parsed_shows, org)
        else:
            print('No {} shows found for {}'.format(org.name, today.strftime('%m/%d/%Y')))
finally:
    BrowserUtils.kill_browser(BROWSER)