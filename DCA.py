from Formatter import PostFormatter
from Selenium import BrowserUtils

class DCAUtils:
    class Show:
        def __init__(self, name, date, timezone, url, image):
            self.name = name
            self.location = name
            self.date = date
            self.url = url
            self.timezone = timezone
            self.streaming = ''
            self.image = image
            self.start_time = ''
            self.end_time = ''
            self.lineup = ['']
        def __str__(self):
            return 'Show[name={}, location={}, date={}, url={}, timezone={}, streaming={}, start_time={}, end_time={}, lineup=[{}]]'.format(self.name, self.location, self.date, self.url, self.timezone, self.streaming, self.start_time, self.end_time, ','.join([str(x) for x in self.lineup]))
        def add_start_time(self, start_time):
            self.start_time = start_time
        def add_end_time(self, end_time):
            self.end_time = end_time
        def add_lineup(self, lineup):
            self.lineup = lineup

    def schedule_url_generator(today):
        today_formatted = today.strftime('%Y-%m-%d')
        schedule_url = 'https://dcacorps.org/events/' + today_formatted
        print(schedule_url)
        return schedule_url

    def full_schedule_parser(tup):
        soup, root = tup
        if len(root.xpath("//li[contains(text(), 'No events scheduled')]")) > 0:
            print("Found 'No events scheduled' text on DCA page!")
            return []
        items = soup.select(selector="[class*='tribe-events-calendar-day'] article")
        shows = []
        if items: print('--------------------------------------------')
        for item in items:
            name = item.select(selector="div div[class*='details'] header h3 a")[0].getText().strip()
            date = item.select(selector="div div[class*='details'] header div time")[0].get('datetime')
            timezone = item.select(selector="div div[class*='details'] header div time span[class*='timezone']")[0].getText().strip()
            url = item.select(selector="div div[class*='details'] header h3 a")[0].get('href')
            image = item.select(selector="img[class*='featured-image']")[0].get('src')
            show = DCAUtils.Show(name, date, timezone, url, image)
            print('Show Name: ' + show.name)
            print('Main Date: ' + show.date)
            print('Timezone: ' + show.timezone)
            print('Show URL: ' + show.url)
            print('Show Image: ' + show.image)
            print('--------------------------------------------')
            shows.append(show)
        return shows

    def show_page_parser(browser, shows):
        parsed_shows = []
        for show in shows:
            print('Parsing ' + show.name)
            soup, root = BrowserUtils.open_url(browser, show.url)
            show.add_start_time(soup.select(selector="[class*='tribe-events-schedule__datetime'] span[class*='time--start']")[0].getText().strip())
            show.add_end_time(soup.select(selector="[class*='tribe-events-schedule__datetime'] span[class*='time--end']")[0].getText().strip())
            groups = soup.select(selector="[class*='tribe-events-schedule'] + div li")
            lineup = []
            for corps in groups:
                lineup.append(corps.getText().strip())
            show.add_lineup(lineup)
            parsed_shows.append(show)
        return parsed_shows

class DCAPostFormatter:
    def create_table(show, body):
        columns = ['**Lineup & Times**', '**All times {} and subject to change**'.format(show.timezone)]
        table = ''
        table = table + '|{}|{}|\n'.format(columns[0], columns[1])
        table = table + '|:-|:-|\n'
        for p in show.lineup:
            table = table + '|X|{}|\n'.format(p)
        body = body + table
        return body
    
    def create_show_block(show):
        body = PostFormatter.create_header(show, 'DCA')
        body = DCAPostFormatter.create_table(show, body)
        return body