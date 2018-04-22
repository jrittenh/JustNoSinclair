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
                if re.search(domains, submission.url, re.IGNORECASE):
                    print("SINCLAIR ", submission.title, " ", submission.url)
                    submission.reply("The domain this post links to is owned or operated by [Sinclair Broadcast Group](https://en.wikipedia.org/wiki/List_of_stations_owned_or_operated_by_Sinclair_Broadcast_Group). PBS NewsHour [has reported on Sinclair's \"partisan tilt on trusted local news\"](https://youtu.be/zNhUk5v3ohE).  John Oliver has [featured a segment on his show](https://youtu.be/GvtNyOzGogc), Last Week Tonight, on Sinclair. Most recently, Sinclair has had an instance of numerous news reports using the exact same script for a Sinclair-provided segment [cut together and published on YouTube](https://youtu.be/hWLjYJ4BzvI).\n\nI am a bot. Please report any issues to [my github repository](https://github.com/jrittenh/JustNoSinclair/issues).\n\n\If you would like me to stop posting to your subreddit, please file an issue on github or contact my creator, ThirdWorldThinkTank.")
                    posts_replied_to.append(submission.id)
                    with open("posts.replied_to", "a" as f:
                        f.write(post.id + "\n")
    except:
        with open("local_subreddits.removed") as f:
            f.write(sr + "\n")
        local_subreddits.remove(sr)
        print(sr, " removed from list of local subreddits")
        with open("local_subreddits", "w") as f:
            for lsr in local_subreddits:
                f.write(lsr + "\n")
    time.sleep(1)

with open("posts.replied_to", "w") as f:
    for post_id in posts_replied_to:
        f.write(post_id + "\n")
