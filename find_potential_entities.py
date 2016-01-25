#!/usr/bin/env python3
"""
Process a parsed novel.

"""
import argparse

from entities import EntityDatabase
from structure import Novel

ENTITIES_FILENAME = 'entities.json'


def process(novel):
    entities = EntityDatabase()
    entities.load(ENTITIES_FILENAME)
    entities.clear_unknown()
    # entities.clear_aliases()

    def process_sentence(sentence):
        for entity in entities.enumerate_entities(sentence.get_words()):
            entities.add(entity)

    novel.for_each_sentence(process_sentence)

    entities.save("generated." + ENTITIES_FILENAME)

    print(entities.get_stats())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='List all potential entities, namely proper nouns.')
    parser.add_argument('input', type=str, help='input tagged novel file')
    args = parser.parse_args()

    novel = Novel(args.input)
    print("novel loaded...")
    process(novel)
