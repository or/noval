#!/usr/bin/env python3
"""

"""
import argparse
import re
import json


CHAPTER = re.compile(r'^[A-Z]+$')
QUOTES = re.compile(r'(?:")')
UNFINISHED = re.compile(r'.*([^".?!]|-)$')

NARRATION = 'narration'
SPEECH = 'speech'
SPEECH_INFO = 'speech_info'


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
        paragraph = {
            NARRATION: '',
            SPEECH: '',
            SPEECH_INFO: '',
        }
        flag = None
        last_flag = None
        for chunk in chunks:
            last_flag = flag
            flag = SPEECH if flag == NARRATION else NARRATION

            chunk = chunk.strip()
            if flag == SPEECH and chunk.endswith(','):
                chunk = chunk[:-1] + '.'

            if last_flag == SPEECH:
                paragraph[SPEECH_INFO] += ' ' + chunk
            else:
                paragraph[flag] += ' ' + chunk

        paragraph = {k: v.strip() for k, v in paragraph.items() if v.strip()}

        chapter['paragraphs'].append(paragraph)

    novel['chapters'].append(chapter)
    json.dump(novel, open(output + '.json', 'w'), indent=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse a novel and pickle the result.')
    parser.add_argument('input', type=str, help='input novel file')
    parser.add_argument('--output', dest='output', action='store',
                        default=None, help='output file')

    args = parser.parse_args()
    if not args.output:
        args.output = args.input + '.parsed'
    read(args.input, args.output)
