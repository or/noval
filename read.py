#!/usr/bin/jython
"""

"""
import argparse
import re
import pickle


CHAPTER = re.compile(r'^[A-Z]+$')
QUOTES = re.compile(r'(?:")')
UNFINISHED = re.compile(r'.*([^".?!]|-)$')

NORMAL = 0
SPEECH = 1
SPEECH_INFO = 2


def paragraph_reader(input_filename):
    last_line = None
    for line in file(input_filename):
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
    from parser import load_stanford_postagger, get_tags
    tagger = load_stanford_postagger()
    chapter = None
    paragraphs = []
    novel = []
    for p in paragraph_reader(input_filename):
        if CHAPTER.match(p):
            if chapter:
                novel.append((chapter, paragraphs))
                paragraphs = []
            chapter = p
            continue

        chunks = QUOTES.split(p)
        paragraph = ['', '', '']
        flag = None
        last_flag = None
        for chunk in chunks:
            last_flag = flag
            flag = SPEECH if flag == NORMAL else NORMAL

            chunk = chunk.strip()
            if flag == SPEECH and chunk.endswith(','):
                chunk = chunk[:-1] + '.'

            if last_flag == SPEECH:
                paragraph[SPEECH_INFO] += ' ' + chunk
            else:
                paragraph[flag] += ' ' + chunk

        for i in range(3):
            paragraph[i] = paragraph[i].strip()
            if paragraph[i]:
                paragraph[i] = get_tags(tagger, paragraph[i])

        paragraphs.append(paragraph)

    novel.append((chapter, paragraphs))
    pickle.dump(novel, open(output, 'w'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse a novel and pickle the result.')
    parser.add_argument('input', type=str, help='input novel file')
    parser.add_argument('--output', dest='output', action='store',
                        default=None, help='output file')

    args = parser.parse_args()
    if not args.output:
        args.output = args.input + '.parsed'
    read(args.input, args.output)
