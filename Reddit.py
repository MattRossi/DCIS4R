from Organization import Orgs
import configparser
import praw

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

    def handle_stickies(self):
        print('Unsticking any sticky posts')
        try:
            secondSticky = self.subreddit.sticky(2)
            print('Unsticking https://reddit.com' + secondSticky.permalink)
            secondSticky.mod.sticky(state=False)
        except:
            print('There are one or less sticky posts!')
        try:
            firstSticky = self.subreddit.sticky(1)
            print('Unsticking https://reddit.com' + firstSticky.permalink)
            firstSticky.mod.sticky(state=False)
        except:
            print('No sticky posts found!')

    def submit_post(self, post, org, should_we_post):
        if should_we_post:
            self.handle_stickies()
            print('Posting to Reddit!')
            choices = self.subreddit.flair.link_templates
            template = next(x for x in choices if x['text'] == 'Show Thread')['id']
            submission = self.subreddit.submit(title=post.title, flair_id=template, selftext=post.body)
            print('Created https://reddit.com' + submission.permalink)
            submission.mod.distinguish(sticky=True)
            submission.mod.sticky(bottom=True if org == Orgs.DCA else False)
            collections = self.subreddit.collections
            for coll in collections:
                print(coll.title + ' | ' + coll.collection_id)
            collection = next(x for x in collections if x.title == '2022 Drum Corps Season').collection_id
            if collection:
                self.subreddit.collections(collection).mod.add_post(submission=submission)
            else:
                print('Collection not found!')
        else:
            print('Not posting to Reddit!')