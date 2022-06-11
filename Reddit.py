import praw
import configparser

class RedditUtils:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.properties')
        self.reddit = praw.Reddit(
            client_id=config['REDDIT']['CLIENT_ID'],
            client_secret=config['REDDIT']['CLIENT_SECRET'],
            password=config['REDDIT']['PASSWORD'],
            user_agent=config['REDDIT']['USER_AGENT'],
            username=config['REDDIT']['USERNAME'],
        )
        self.subreddit = self.reddit.subreddit(config['REDDIT']['SUBREDDIT'])

    class RedditPost:
        def __init__(self, title, body):
            self.title = title
            self.body = body

    def submit_post(self, post):
        choices = self.subreddit.flair.link_templates
        template = next(x for x in choices if x['text'] == 'Show Thread')['id']
        #submission = self.subreddit.submit(title=post.title, flair_id=template, selftext=post.body)
        #submission.mod.distinguish(sticky=True)