from bs4 import Comment
from Formatter import PostFormatter
from Selenium import BrowserUtils

class DCIUtils:
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

    def schedule_url_generator(today):
        today_formatted = today.strftime('%Y-%m-%d')
        schedule_url = 'https://www.dci.org/events?startDate=' + today_formatted + '&toDate=' + today_formatted + '&limit=10&viewMode=list&sort=startDate'
        print(schedule_url)
        return schedule_url

    def full_schedule_parser(tup):
        soup, root = tup
        items = soup.select(selector="[class='events-items'] [class='item']")
        shows = []
        if items: print('--------------------------------------------')
        for item in items:
            name = item.select(selector="h3 a")[0].getText()
            date = item.select(selector="[class='print-date']")[0].getText()
            url = 'https://dci.org' + item.select(selector="h3 a")[0].get('href')
            show = DCIUtils.Show(name, date, url)
            print('Show Name: ' + show.name)
            print('Main Date: ' + show.date)
            print('Show URL: ' + show.url)
            print('--------------------------------------------')
            shows.append(show)
        return shows

    def grab_flo_link(show, soup):
        buttons = soup.select(selector="[class='buttons']")[0]
        for element in buttons(text=lambda text: isinstance(text, Comment)):
            element.extract()
        if len(buttons) <= 1:
            print('No FloMarching link for {}!'.format(show.name))
        else:
            rawLink = buttons.select(selector="*:first-child")[0].get('href')
            show.add_flo(rawLink.split('?')[0])

    def show_page_parser(browser, shows):
        parsedShows = []
        for show in shows:
            print('Parsing: ' + show.name)
            soup, root = BrowserUtils.open_url(browser, show.url)
            show.add_location(soup.select(selector="[class='location']")[0].getText().strip())
            show.add_timezone(root.xpath("//p[contains(., 'and subject')]//span")[0].text)
            DCIUtils.grab_flo_link(show, soup)
            slots = soup.select(selector="[class='time-table'] > div")
            lineup = []
            for slot in slots:
                time = slot.select(selector="*:first-child")[0].getText()
                corps_and_location = slot.select(selector="*:nth-child(2)")[0]
                for element in corps_and_location(text=lambda text: isinstance(text, Comment)):
                    element.extract()
                corps = corps_and_location.select(selector="*:first-child")[0].getText()
                if len(corps_and_location) != 1:
                    location = corps_and_location.select(selector="*:nth-child(2)")[0].getText().replace(' - ', '')
                else:
                    location = ''
                lineup.append(DCIUtils.LineupSlot(corps, time, location))
            show.add_lineup(lineup)
            parsedShows.append(show)
        return parsedShows

class DCIPostFormatter:
    def create_table(show, body):
        columns = ['**Lineup & Times**', '**All times {} and subject to change**'.format(show.timezone)]
        table = ''
        table = table + '|{}|{}|\n'.format(columns[0], columns[1])
        table = table + '|:-|:-|\n'
        for p in show.lineup:
            table = table + '|{}|{}|\n'.format(p.time, (p.corps + ((' - ' + p.location) if p.location else '')))
        body = body + table
        return body

    def create_show_block(show):
        body = PostFormatter.create_header(show, 'DCI')
        body = DCIPostFormatter.create_table(show, body)
        if show.flo:
            body = body + '\n^(Watch live on) [^(FloMarching)]({})'.format(show.flo)
        return body