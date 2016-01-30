#!/usr/bin/env python3
"""

"""
import argparse
import json
import re

from structure import ParagraphChunk

CHAPTER = re.compile(r'^[A-Z ]+$')
QUOTES = re.compile(r'(?:")')
UNFINISHED = re.compile(r'.*([^".?!]|-)$')
INQUIT_KEYWORDS = re.compile(r'.*\W(said|asked|answered|shouted|observed)\W.*')
QUOTED_TEXT = re.compile(r'^[A-Za-z0-9 ]+$')

RUN_ON_DIRECT = "<run-on-direct>"


def paragraph_reader(input_filename):
    last_line = None
    for line in open(input_filename):
        line = line.strip()
        if not line:
            continue

        if CHAPTER.match(line):
            if last_line:
                yield last_line

            yield line
            last_line = None
            continue

        if last_line:
            if last_line.endswith('-'):
                if line.startswith('-'):
                    # todo: unsure what this was suppsoed to do
                    raise Exception("ugh?")
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


def split_direct_indirect(paragraph):
    chunks = QUOTES.split(paragraph)
    result = []
    i = 0
    while i < len(chunks):
        if (i > 0 and chunks[i - 1].strip() and
           chunks[i - 1].strip()[-1].isalpha() and
           chunks[i] and QUOTED_TEXT.match(chunks[i])):
            result[-1] += '"{}"{}'.format(chunks[i], chunks[i + 1])
            i += 2

        else:
            result.append(chunks[i])
            i += 1

    if len(result) % 2 == 0 and not paragraph.strip().endswith('"'):
        result.append(RUN_ON_DIRECT)

    return result


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

        paragraph = []
        flag = None
        last_chunk = ''
        for chunk in split_direct_indirect(p):
            flag = (ParagraphChunk.DIRECT
                    if flag == ParagraphChunk.INDIRECT
                    else ParagraphChunk.INDIRECT)

            chunk = chunk.strip()

            if flag == ParagraphChunk.INDIRECT and looks_like_inquit(chunk, last_chunk):
                paragraph.append(dict(type='inquit', data=chunk))
            else:
                paragraph.append(dict(type=flag, data=chunk))

            last_chunk = chunk

        paragraph = [x for x in paragraph if x['data']]

        last_paragraph = chapter['paragraphs'][-1] if chapter['paragraphs'] else None
        if (last_paragraph and
           len(last_paragraph) > 1 and
           last_paragraph[-2]['type'] == ParagraphChunk.DIRECT and
           last_paragraph[-1]['data'] == RUN_ON_DIRECT and
           paragraph[0]['type'] == ParagraphChunk.DIRECT):
            last_paragraph.pop(-1)
            last_paragraph[-1]['data'] += " " + paragraph[0]['data']
            last_paragraph += paragraph[1:]
        else:
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
