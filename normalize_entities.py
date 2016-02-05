#!/usr/bin/env python3
"""
Process a parsed novel.

"""
import argparse

from entities import EntityDatabase
from structure import Novel

ENTITIES_FILENAME = 'entities.json'


def process(novel):
    edb = EntityDatabase()
    edb.load(ENTITIES_FILENAME)

    def process_chapter_done(chapter):
        chapter.identify_speakers(edb)

    novel.for_each(chapter_done=process_chapter_done)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='List all potential entities, namely proper nouns.')
    parser.add_argument('input', type=str, help='input tagged novel file')
    args = parser.parse_args()

    novel = Novel(args.input)
    print("novel loaded...")
    process(novel)
    novel.save(args.input + '.normalized')
