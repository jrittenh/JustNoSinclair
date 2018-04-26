#!/usr/bin/env python

import praw
from prawcore import exceptions
import re
import os
import time
import pprint

with open('banned_reply_text', 'r') as f:
    banned_reply_text = f.read().rstrip()

with open('banned_with_note_reply_text', 'r') as f:
    banned_with_note_reply_text = f.read().rstrip()

reddit = praw.Reddit('JustNoSinclair')

for message in reddit.inbox.messages(limit=None):
    # ~ print(message.parent_id)
    try:
        banned_yn = re.search('banned', message.subject)
        if message.parent_id is None and not message.replies and banned_yn:
            if re.search('Note from the moderators', message.body):
                print("Thank you reply")
                message.reply(banned_with_note_reply_text)
            else:
                print("Question reply")
                message.reply(banned_reply_text)
        elif not message.replies and banned_yn:
            print(message.body)
    except Exception as e:
        print(type(e))
        print(e)
