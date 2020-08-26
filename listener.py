import praw, sys, asyncio, random, pytz, statistics, time
from decimal import Decimal
from datetime import datetime, timezone
from dotenv import load_dotenv
from os import environ
load_dotenv('.env')

class SubredditReport:

    def __init__(self, subr):
        self.subr = subr
        self.comments = []

    def __str__(self):
        return(self.subr.display_name)

    def add_comment(self, comment):
        self.comments.append(comment)

    def karma_high(self):
        karma = []
        for comment in self.comments:
            karma.append(comment.score)
        return(max(karma))

    def karma_low(self):
        karma = []
        for comment in self.comments:
            karma.append(comment.score)
        return(min(karma))

    def karma_avg(self):
        karma = []
        for comment in self.comments:
            karma.append(comment.score)
        return(round(statistics.mean(karma),1))

    def first_post(self):
#        sorted_comments = sorted(self.comments, key=lambda comment: comment.created_utc)
        return(self.comments[-1])

    def most_recent_post(self):
#        sorted_comments = sorted(self.comments, key=lambda comment: comment.created_utc)
        return(self.comments[0])

    def posts_in_timeperiod(self,period):
        if period not in ['hour','day','week','month','year']:
            raise ValueError('Please use hour, day, week, month, year as options')
        now = time.time()
        counter = 0
        if period == 'hour':
            cutoff = now - (60*60)
        elif period == 'day':
            cutoff = now - (60*60*24)
        elif period == 'week':
            cutoff = now - (60*60*24*7)
        elif period == 'month':
            cutoff = now - (60*60*24*30)
        elif period == 'year':
            cutoff = now - (60*60*24*365)
        for comment in self.comments:
            if comment.created_utc > cutoff:
                counter += 1
        return(counter)

    def posts_older_than(self,period):
        if period not in ['hour','day','week','month','year']:
            raise ValueError('Please use hour, day, week, month, year as options')
        now = time.time()
        counter = 0
        if period == 'hour':
            cutoff = now - (60*60)
        elif period == 'day':
            cutoff = now - (60*60*24)
        elif period == 'week':
            cutoff = now - (60*60*24*7)
        elif period == 'month':
            cutoff = now - (60*60*24*30)
        elif period == 'year':
            cutoff = now - (60*60*24*365)
        for comment in self.comments:
            if comment.created_utc < cutoff:
                counter += 1
        return(counter)

def reddit_send():
    r = praw.Reddit(client_id = environ.get('CLIENT_ID'),
                    client_secret = environ.get('CLIENT_SECRET'),
                    redirect_uri = environ.get('REDIRECT_URI'),
                    user_agent = environ.get('USER_AGENT'),
                    refresh_token = environ.get('REFRESH_TOKEN'))
    return(r)

def reddit_read():
    r = praw.Reddit(client_id = environ.get('CLIENT_ID'),
                    client_secret = environ.get('CLIENT_SECRET'),
                    user_agent = environ.get('USER_AGENT'))
    return(r)

def comment_level(comment):
    if comment.is_root:
        return(True)
    elif comment.parent().is_root:
        return(True)
    else:
        return(False)

def msg_reply():
    pass

async def listener():
    target_sub = 'wisconsin'
    r = reddit_read()
    for comment in r.subreddit(target_sub).stream.comments():
        if comment_level(comment):
            subs = await auth_report(comment.author)
            try:
                day_old = subs[target_sub].posts_older_than('day')
                week_old = subs[target_sub].posts_older_than('week')
                if (day_old == 0):
                    print("Day Old: ", comment.is_root, comment.author.name, comment.permalink)
                elif (week_old == 0):
                    print("Week Old: ", comment.is_root, comment.author.name, comment.permalink)
            except:
                print(comment.permalink)
#        print(comment.body)

async def get_refresh():
    r = reddit_connect()
#    print(r.auth.scopes())
#    state = str(random.randint(0, 65000))
#    url = r.auth.url(["*"], state, "permanent")
#    print(url)
#    print(r.auth.authorize('0avQEiNqrNaX2Pi7wb-t7KcAD14'))

async def auth_report(author):
    r_read = reddit_read()
    central_timezone = pytz.timezone("US/Central")
    subs = {}
    for comment in author.comments.new(limit=1000):
        if comment.subreddit.display_name not in subs:
            subs[comment.subreddit.display_name] = SubredditReport(r_read.subreddit(comment.subreddit.display_name))
#        creation_time = datetime.fromtimestamp(comment.created_utc).astimezone(central_timezone)
        subs[comment.subreddit.display_name].add_comment(comment)
    return(subs)


if __name__ == "__main__":
    asyncio.run(listener())
