#!/usr/bin/env python3
"""
Process a parsed novel.

"""
import argparse
import nltk
import pickle
from collections import defaultdict
from functools import reduce

from structure import Character, Entity, Scene
from data import Data


def collect(tree, entities=None, words=None):
    """
    Collect all entities in a tree.

    """
    if entities is None:
        entities = defaultdict(int)
    if words is None:
        words = defaultdict(int)

    if tree.node != 'S':
        entity = Entity.get(tree)
        if entity.name not in ('Ser', 'Lord'):
            entities[entity] += 1
    elif not words:
        for word in tree.leaves():
            words[word[0].lower()] += 1

    subtrees = list(tree.subtrees())[1:]
    for subtree in subtrees:
        collect(subtree, entities, words)

    return entities, words


def marker(text):
    sentences = reduce(lambda a, b: a + b, [[]] + text[:3])
    return ' '.join([x[0] for x in sentences])[:32]


def process(input_file):
    """
    Go through a parsed novel. Chapter by chapter.

    """
    novel = pickle.load(open(input_file))
    scene = Scene()
    data = Data()
    for chapter, paragraphs in novel:
        for text, speech, speech_info in paragraphs:
            current_speaker = None
            for sentence in speech_info:
                tree = nltk.chunk.ne_chunk(sentence)
                entities, words = collect(tree)
                data.add(entities, words)
                if not current_speaker:
                    for entity in entities:
                        if isinstance(entity, Character):
                            current_speaker = entity
                            break

            for sentence in text:
                tree = nltk.chunk.ne_chunk(sentence)
                entities, words = collect(tree)
                data.add(entities, words)
                if not current_speaker:
                    for entity in entities:
                        if isinstance(entity, Character):
                            current_speaker = entity
                            break

            if speech:
                guessed = False
                if not current_speaker:
                    current_speaker = scene.get_speaker(-2)
                    guessed = True
                if not current_speaker:
                    print('not sure who is speaking', speech)
                else:
                    print(current_speaker,
                          'is speaking %s' %
                          (' (guessed) %s' % str(marker(speech)) if guessed else ''))

                scene.add_speaker(current_speaker)
            else:
                print('nobody is speaking')

            for sentence in speech:
                tree = nltk.chunk.ne_chunk(sentence)
                entities, words = collect(tree)
                data.add(entities, words, character=current_speaker)

        scene = Scene()

    top_words = sorted(data.overall.words.items(), key=lambda x: x[1],
                       reverse=True)[:100]
    for word, count in top_words:
        print(word, count)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a previously parsed novel.')
    parser.add_argument('input', type=str, help='input parsed novel file')
    args = parser.parse_args()

    process(args.input)
