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
comment = ""
with open('comment_text', 'r') as f:
    comment = f.read()
try:
    subreddits = (reddit.subreddit(sr) for sr in local_subreddits)
    for subreddit in subreddits:
        for submission in subreddit.hot(limit=50):
            submission_timely = time.time() - submission.created < 86400
            if submission.id not in posts_replied_to \
                and re.search("|".join(domains), submission.url, re.IGNORECASE) \
                and submission_timely:
                    print("SINCLAIR" + submission.title + submission.url)
                    submission.reply(comment)
                    posts_replied_to.append(submission.id)
                    with open("posts_replied_to", "a") as f:
                        f.write(submission.id + "\n")
except exceptions.Forbidden:
    remove_subreddit(local_subreddits, sr, "private")
except exceptions.NotFound:
    remove_subreddit(local_subreddits, sr, "invalid")
except exceptions.Redirect:
    remove_subreddit(local_subreddits, sr, "not found")
except Exception as e:
    print(type(e))
    print(e)
