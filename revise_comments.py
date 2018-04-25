#!/usr/bin/env python

import praw
from prawcore import exceptions
import re
import os
import time

comment_text = ""
with open('comment_text', 'r') as f:
    comment_text = f.read().rstrip()

reddit = praw.Reddit('JustNoSinclair')

for comment in reddit.redditor('JustNoSinclair').comments.new(limit=None):
    if comment.body != comment_text:
        comment.edit(comment_text)
        print(comment)
