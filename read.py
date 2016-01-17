#!/usr/bin/env python3
"""

"""
import argparse
import re
import json


CHAPTER = re.compile(r'^[A-Z]+$')
QUOTES = re.compile(r'(?:")')
UNFINISHED = re.compile(r'.*([^".?!]|-)$')
INQUIT_KEYWORDS = re.compile(r'.*\W(said|asked|answered|shouted)\W.*')

INDIRECT = 'indirect'
DIRECT = 'direct'
INQUIT = 'inquit'


def paragraph_reader(input_filename):
    last_line = None
    for line in open(input_filename):
        line = line.strip()
        if not line:
            continue

        if last_line:
            if last_line.endswith('-'):
                if line.startswith('-'):
                    yield last_line + '"'
                    line = '"' + line
                else:
                    line = last_line[:-1] + line
            elif line.startswith('"'):
                yield last_line
            else:
                line = last_line + ' ' + line

            last_line = None

        if UNFINISHED.match(line):
            last_line = line
            continue

        yield line

    if last_line:
        yield last_line


def looks_like_inquit(chunk, previous_chunk):
    chunk = chunk.strip()
    previous_chunk = previous_chunk.strip()
    if not chunk:
        return False

    if previous_chunk.endswith(','):
        return True

    if chunk[0] == chunk[0].lower():
        return True

    if INQUIT_KEYWORDS.match(chunk):
        return True

    return False


def read(input_filename, output):
    """
    Read and parse novel, pickle to output file.

    """
    novel = {'chapters': []}
    chapter = {}
    for p in paragraph_reader(input_filename):
        if CHAPTER.match(p):
            if chapter:
                novel['chapters'].append(chapter)

            chapter = {
                'name': p,
                'paragraphs': [],
            }
            continue

        chunks = QUOTES.split(p)
        paragraph = []
        flag = None
        last_chunk = ''
        for chunk in chunks:
            flag = DIRECT if flag == INDIRECT else INDIRECT

            chunk = chunk.strip()

            if flag == INDIRECT and looks_like_inquit(chunk, last_chunk):
                paragraph.append(dict(type='inquit', data=chunk))
            else:
                paragraph.append(dict(type=flag, data=chunk))

            last_chunk = chunk

        paragraph = [x for x in paragraph if x['data']]

        chapter['paragraphs'].append(paragraph)

    novel['chapters'].append(chapter)
    json.dump(novel, open(output, 'w'), indent=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse a novel and pickle the result.')
    parser.add_argument('input', type=str, help='input novel file')
    parser.add_argument('--output', dest='output', action='store',
                        default=None, help='output file')

    args = parser.parse_args()
    if not args.output:
        args.output = args.input + '.read'
    read(args.input, args.output)
