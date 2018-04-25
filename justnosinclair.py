#!/usr/bin/env python

import praw
from prawcore import exceptions
import re
import os
import time

reddit = praw.Reddit('JustNoSinclair')

def read_text_set(filename):
    result = {}
    try:
        with open(filename) as f:
            result = {_.strip() for _ in f if _}
    except FileNotFoundError:
        pass
    return result

def remove_subreddit(sr_list, sr, error):
    fn = error
    fn.replace(" ", "_")
    with open("local_subreddits/" + fn, "a") as f:
        f.write(sr + "\n")
    sr_list.remove(sr)
    with open("local_subreddits/active", "w") as f:
        for lsr in sr_list:
            f.write(lsr + "\n")
    print(sr + " is " + error + ", removed from list of local subreddits")


posts_replied_to = read_text_set("posts_replied_to")
domains = {_.lower() for _ in read_text_set("sinclair_domains")}
local_subreddits = read_text_set("local_subreddits/active") or {"politics"}
try:
    subreddits = (reddit.subreddit(sr) for sr in local_subreddits)
    for subreddit in subreddits:
        for submission in subreddit.hot(limit=50):
            submission_url = submission.url.lower()
            submission_timely = time.time() - submission.created < 86400
            if submission.id not in posts_replied_to \
                and submission_url in domains \
                and submission_timely:
                    print("SINCLAIR {submission.title} {submission.url}")
                    submission.reply("The domain this post links to is owned or operated by [Sinclair Broadcast Group]"
                    "(https://en.wikipedia.org/wiki/List_of_stations_owned_or_operated_by_Sinclair_Broadcast_Group).\n\n"
                    "Rolling Stone just recently published an article titled [\"Sinclair Broadcasting's Hostile Takeover\"]"
                    "(https://www.rollingstone.com/culture/features/sinclair-broadcast-group-hostile-takeover-trump-w519331).  "
                    "PBS NewsHour [has reported on Sinclair's \"partisan tilt on trusted local news\"](https://youtu.be/zNhUk5v3ohE).  "
                    "John Oliver has [featured a segment on his show](https://youtu.be/GvtNyOzGogc), Last Week Tonight, on Sinclair.  "
                    "Most recently, Sinclair has had an instance of numerous news reports using the exact same script for a Sinclair-"
                    "provided segment [cut together and published on YouTube](https://youtu.be/hWLjYJ4BzvI).\n\n"
                    "I am a bot.  Please report any issues or requests to have your subreddit removed from my list to "
                    "[my github repository](https://github.com/jrittenh/JustNoSinclair/issues).")
                    posts_replied_to.append(submission.id)
                    with open("posts_replied_to", "a") as f:
                        f.write(post.id + "\n")
except exceptions.Forbidden:
    remove_subreddit(local_subreddits, sr, "private")
except exceptions.NotFound:
    remove_subreddit(local_subreddits, sr, "invalid")
except exceptions.Redirect:
    remove_subreddit(local_subreddits, sr, "not found")
except Exception as e:
    print(type(e))
    print(e)
# ~ time.sleep(1)

with open("posts_replied_to", "w") as f:
    for post_id in posts_replied_to:
        f.write(post_id + "\n")
