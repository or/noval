#!/usr/bin/env python3
"""
Process a parsed novel.

"""
import argparse
import json

from progressbar import ETA, Bar, Percentage, ProgressBar

from entities import EntityDatabase

ENTITIES_FILENAME = 'entities.json'


def process(novel):
    entities = EntityDatabase()
    entities.load(ENTITIES_FILENAME)
    entities.clear_unknown()
    # entities.clear_aliases()

    chapters = novel['chapters']
    total_number_paragraphs = \
        sum([len(chunk['sentences'])
             for c in chapters
             for p in c['paragraphs'] for chunk in p])

    widgets = [Percentage(), Bar(), ETA()]
    pbar = ProgressBar(widgets=widgets, maxval=total_number_paragraphs).start()
    num_sentences = 0
    for chapter in chapters:
        for paragraph in chapter['paragraphs']:
            for chunk in paragraph:
                for sentence in chunk['sentences']:
                    pbar.update(num_sentences)
                    num_sentences += 1

                    for entity in entities.enumerate_entities(sentence['words']):
                        entities.add(entity)

    pbar.finish()

    entities.save("generated." + ENTITIES_FILENAME)

    print(entities.get_stats())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='List all potential entities, namely proper nouns.')
    parser.add_argument('input', type=str, help='input tagged novel file')
    args = parser.parse_args()

    novel = json.load(open(args.input))
    print("novel loaded...")
    process(novel)
