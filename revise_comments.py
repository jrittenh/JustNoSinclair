#!/usr/bin/env python

import praw
from prawcore import exceptions
import re
import os
import time

account = 'JustNoSinclair'

comment_text = ""
with open('comment_text', 'r') as f:
    comment_text = f.read().rstrip()

reddit = praw.Reddit(account)

for comment in reddit.redditor(account).comments.new(limit=None):
    if comment.body != comment_text:
        comment.edit(comment_text)
        print(comment + " edited (post" + comment.submission.id + ")")
