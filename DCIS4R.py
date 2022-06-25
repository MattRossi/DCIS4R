from datetime import datetime
from Selenium import BrowserUtils
from Formatter import PostFormatter
from Reddit import RedditUtils
from Organization import Orgs

today = datetime.now()
#today = datetime(2022, 7, 16)

should_we_post = True
#should_we_post = False

def generate_post(parsed_shows, org):
    print('\n'.join([str(x) for x in parsed_shows]))
    final_body = ''
    for show in parsed_shows:
        final_body = final_body + org.formatter.create_show_block(show)
        final_body = final_body + '\n\n'
    final_body = PostFormatter.create_post_footer(final_body)
    print('Printing final body')
    print(final_body)
    post_title = PostFormatter.create_title(parsed_shows, org, today)
    print(post_title)
    post = RedditUtils.RedditPost(post_title, final_body)
    RedditUtils().submit_post(post, org, should_we_post)

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