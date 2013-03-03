#!/usr/bin/env python
"""
Process a parsed novel.

"""
import argparse
import nltk
import pickle
from collections import defaultdict
from pprint import pprint


def update_dict(dict1, dict2):
    for key, value in dict2.items():
        dict1[key] |= value


def collect_entities(tree):
    entities = defaultdict(set)
    if tree.node != 'S':
        entities[tree.node].add(tuple(tree.leaves()))

    subtrees = list(tree.subtrees())[1:]
    for subtree in subtrees:
        update_dict(entities, collect_entities(subtree))

    return entities


def process(input_file):
    novel = pickle.load(open(input_file))
    all_entities = defaultdict(set)
    for chapter, paragraphs in novel:
        for text, speech, speech_info in paragraphs:
            for sentence in text:
                tree = nltk.chunk.ne_chunk(sentence)
                entities = collect_entities(tree)
                update_dict(all_entities, entities)

    for key, value in all_entities.items():
        print key
        for x in value:
            print '    ', ' '.join([y[0] for y in x])

        print


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a previously parsed novel.')
    parser.add_argument('input', type=str, help='input parsed novel file')
    args = parser.parse_args()

    process(args.input)
