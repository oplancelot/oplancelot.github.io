#!/usr/bin/env python

'''
tag_generator.py

Copyright 2017 Long Qian
Contact: lqian8@jhu.edu

This script creates tags for your Jekyll blog hosted by Github page.
No plugins required.
'''

import glob
import os
import io
import re
import datetime
post_dir = '_posts/'
tag_dir = 'tag/'

filenames = glob.glob(post_dir + '*.md')

total_tags = []
for filename in filenames:
    
    f = open(filename, 'r')
    crawl = False
    for line in f:
        if crawl:
            current_tags = line.strip().split()
            if current_tags[0] == 'tags:':
                total_tags.extend(current_tags[1:])
                crawl = False
                break
        if line.strip() == '---':
            if not crawl:
                crawl = True
            else:
                crawl = False
                break
    f.close()
    
    dirname, filetemp = os.path.split(filename)     
    if re.match('^\d{4}-\d{1,2}-\d{1,2}', filetemp, flags=0) == None:
        # new_file=os.path.join(dirname, "6.jpg")
        date = datetime.date.today()
        strDate = str(date)
        newFileName = os.path.join(dirname, strDate + '-' +filetemp)
        print "now rename file: " + filetemp + " to: " + newFileName
        os.rename(filename, newFileName)
       

total_tags = set(total_tags)

old_tags = glob.glob(tag_dir + '*.md')
for tag in old_tags:
    os.remove(tag)
    
if not os.path.exists(tag_dir):
    os.makedirs(tag_dir)


for tag in total_tags:
    tag_filename = tag_dir + tag + '.md'
    f = open(tag_filename, 'a')
    write_str = '---\nlayout: tag\ntitle: \"Tag: ' + tag + '\"\ntag: ' + tag + '\nrobots: noindex\n---\n'
    f.write(write_str)
    f.close()
print("Tags generated, count", total_tags.__len__())


