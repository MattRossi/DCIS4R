# import praw
# import configparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from bs4 import BeautifulSoup, Comment
from lxml import html

# config = configparser.ConfigParser()
# config.read('config.properties')
# REDDIT_CLIENT_ID = config['REDDIT']['CLIENT_ID']
# REDDIT_CLIENT_SECRET = config['REDDIT']['CLIENT_SECRET']
# REDDIT_USERNAME = config['REDDIT']['USERNAME']
# REDDIT_PASSWORD = config['REDDIT']['PASSWORD']
# REDDIT_USER_AGENT = config['REDDIT']['USER_AGENT']
# REDDIT_SUBREDDIT = config['REDDIT']['SUBREDDIT']

# reddit = praw.Reddit(
#     client_id=REDDIT_CLIENT_ID,
#     client_secret=REDDIT_CLIENT_SECRET,
#     password=REDDIT_PASSWORD,
#     user_agent=REDDIT_USER_AGENT,
#     username=REDDIT_USERNAME,
# )
# subreddit = reddit.subreddit(REDDIT_SUBREDDIT)

########################################
############### SELENIUM ###############
########################################

def createBrowser():
    options = Options()
    options.add_argument('--headless')
    return webdriver.Chrome('C:/Users/mattr/.cache/selenium/chromedriver/chromedriver.exe', options=options)

def killBrowser(browser):
    if browser:
        print('Killing browser...')
        browser.quit()
        print('Killed browser!')

def openUrl(browser, url):
    print('Opening {}'.format(url))
    browser.get(url)
    source = browser.page_source
    return (BeautifulSoup(source, 'lxml'), html.fromstring(source))

#######################################
################# DCI #################
#######################################

class Show:
    def __init__(self, name, date, url):
        self.name = name
        self.location = ''
        self.date = date
        self.url = url
        self.timezone = ''
        self.flo = ''
        self.lineup = ['']
    def __str__(self):
        return 'Show[name={}, location={}, date={}, url={}, timezone={}, flo={}, lineup=[{}]]'.format(self.name, self.location, self.date, self.url, self.timezone, self.flo, ','.join([str(x) for x in self.lineup]))
    def add_location(self, location):
        self.location = location
    def add_timezone(self, timezone):
        self.timezone = timezone
    def add_flo(self, flo):
        self.flo = flo
    def add_lineup(self, lineup):
        self.lineup = lineup

class LineupSlot:
    def __init__(self, corps, time, location):
        self.corps = corps
        self.time = time
        self.location = location
    def __str__(self):
        return 'Slot[corps={0}, time={1}, location={2}]'.format(self.corps, self.time, self.location)

def scheduleUrlGenerator():
    #today = datetime.now().strftime('%Y-%m-%d')
    today = datetime(2022, 6, 24).strftime('%Y-%m-%d')
    schedUrl = 'https://www.dci.org/events?startDate=' + today + '&toDate=' + today + '&limit=10&viewMode=list&sort=startDate'
    print(schedUrl)
    return schedUrl

def fullScheduleParser(tup):
    soup, root = tup
    items = soup.select(selector="[class='events-items'] [class='item']")
    shows = []
    print('--------------------------------------------')
    for item in items:
        name = item.select(selector="h3 a")[0].getText()
        date = item.select(selector="[class='print-date']")[0].getText()
        url = 'https://dci.org' + item.select(selector="h3 a")[0].get('href')
        show = Show(name, date, url)
        print('Show Name: ' + show.name)
        print('Main Date: ' + show.date)
        print('Show URL: ' + show.url)
        print('--------------------------------------------')
        shows.append(show)
    return shows

def grabFloLink(show, soup):
    buttons = soup.select(selector="[class='buttons']")[0]
    for element in buttons(text=lambda text: isinstance(text, Comment)):
        element.extract()
    if len(buttons) == 1:
        print('No FloMarching link for {}!'.format(show.name))
    else:
        rawLink = buttons.select(selector="*:first-child")[0].get('href')
        show.add_flo(rawLink.split('?')[0])

def showPageParser(browser, shows):
    parsedShows = []
    for show in shows:
        print('Parsing: ' + show.name)
        soup, root = openUrl(browser, show.url)
        show.add_location(soup.select(selector="[class='location']")[0].getText().strip())
        show.add_timezone(root.xpath("//p[contains(., 'and subject')]//span")[0].text)
        grabFloLink(show, soup)
        slots = soup.select(selector="[class='time-table'] > div")
        lineup = []
        for slot in slots:
            time = slot.select(selector="*:first-child")[0].getText()
            corpsAndLocation = slot.select(selector="*:nth-child(2)")[0]
            for element in corpsAndLocation(text=lambda text: isinstance(text, Comment)):
                element.extract()
            corps = corpsAndLocation.select(selector="*:first-child")[0].getText()
            if len(corpsAndLocation) != 1:
                location = corpsAndLocation.select(selector="*:nth-child(2)")[0].getText().replace(' - ', '')
            else:
                location = ''
            newLineup = LineupSlot(corps, time, location)
            lineup.append(newLineup)
        show.add_lineup(lineup)
        parsedShows.append(show)
    return parsedShows

########################################
################ FORMAT ################
########################################

def createHeader(show):
    body = ''
    body = body + '[**{} DCI Page**]({})'.format(show.name, show.url)
    body = body + '\n\n'
    return body

def createTable(show, body):
    columns = ['**Lineup & Times**', '**All times {} and subject to change**'.format(show.timezone)]
    table = ''
    table = table + '|{}|{}|\n'.format(columns[0], columns[1])
    table = table + '|:-|:-|\n'
    for p in show.lineup:
        table = table + '|{}|{}|\n'.format(p.time, (p.corps + ((' - ' + p.location) if p.location else '')))
    body = body + table
    return body

def createFooter(show, body):
    if show.flo:
        body = body + '\n^(Watch live on) [^(FloMarching)]({})'.format(show.flo)
    body = body + '\n\n## Join our [Discord server](https://discord.gg/drumcorps) for real-time discussion with other drum corps fans and marching members!'
    return body

def createBody(show):
    return createFooter(show, createTable(show, createHeader(show)))


########################################
################ REDDIT ################
########################################

# TODO post to reddit

########################################
################ SCRIPT ################
########################################

try:
    BROWSER = createBrowser()

    shows = fullScheduleParser(openUrl(BROWSER, scheduleUrlGenerator()))
    # print('\n'.join([str(x) for x in shows]))
    parsedShows = showPageParser(BROWSER, shows)
    # print('\n'.join([str(x) for x in parsedShows]))

    for show in parsedShows:
        body = createBody(show)
        print(body)
finally:
    killBrowser(BROWSER)