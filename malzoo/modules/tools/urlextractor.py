#!/usr/bin/python

import re

def get_urls(text):
    try:
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@~.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        if len(urls) == 0:
            urls = None
    except Exception as e:
        print "URL extractor:", e
        urls = None
    finally:
        return urls
