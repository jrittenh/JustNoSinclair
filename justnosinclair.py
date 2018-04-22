#!/usr/bin/env python

import praw
import re
import os
import time

reddit = praw.Reddit('JustNoSinclair')

if not os.path.isfile("posts_replied_to"):
    posts_replied_to = []
else:
    with open("posts_replied_to", "r") as f:
        posts_replied_to = f.read()
        posts_replied_to = posts_replied_to.split("\n")
        posts_replied_to = list(filter(None, posts_replied_to))

if not os.path.isfile("sinclair_domains"):
    sinclair_domains = []
else:
    with open("sinclair_domains", "r") as f:
        sinclair_domains = f.read()
        sinclair_domains = sinclair_domains.split("\n")
        sinclair_domains = list(filter(None, sinclair_domains))
        domains = "|".join(sinclair_domains)

if not os.path.isfile("local_subreddits"):
    local_subreddits = ["politics"]
else:
    with open("local_subreddits", "r") as f:
        local_subreddits = f.read()
        local_subreddits = local_subreddits.split("\n")
        local_subreddits = list(filter(None, local_subreddits))

for sr in local_subreddits:
    subreddit = reddit.subreddit(sr)
    try:
        for submission in subreddit.top(time_filter="hour", limit=50):
            if submission.id not in posts_replied_to:
                print(submission.url)
                if re.search(domains, submission.url, re.IGNORECASE):
                    print("SINCLAIR ", submission.title)
                    posts_replied_to.append(submission.id)
    except:
        print(sr)
    time.sleep(1)

with open("posts.replied_to", "w") as f:
    for post_id in posts_replied_to:
        f.write(post_id + "\n")
