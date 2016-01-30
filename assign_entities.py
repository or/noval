#!/usr/bin/env python3
"""
Process a parsed novel.

"""
import argparse

from entities import EntityDatabase
from structure import Context, Novel

ENTITIES_FILENAME = 'entities.json'


def process(novel):
    edb = EntityDatabase()
    edb.load(ENTITIES_FILENAME)

    context = Context()

    def process_sentence(sentence):
        context.process_sentence(sentence, edb)

    novel.for_each_sentence(process_sentence)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='List all potential entities, namely proper nouns.')
    parser.add_argument('input', type=str, help='input tagged novel file')
    args = parser.parse_args()

    novel = Novel(args.input)
    print("novel loaded...")
    process(novel)
    novel.save(args.input + '.entities')
