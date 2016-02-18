#!/usr/bin/env python3
import json
import sys

tags = set()
data = json.load(open(sys.argv[1]))
for chapter in data['chapters']:
    for paragraph in chapter['paragraphs']:
        for chunk in paragraph:
            for sentence in chunk['sentences']:
                for word in sentence['words']:
                    tags.add(word['tag'])

print(tags)
