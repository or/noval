#!/usr/bin/env python3
"""
Process a parsed novel.

"""
import argparse
import re

from data import Data
from entities import EntityDatabase
from structure import Novel

ENTITIES_FILENAME = 'entities.json'
WORD_SPLIT = re.compile(r'[ ,.!?]')


def process(novel):
    edb = EntityDatabase()
    edb.load(ENTITIES_FILENAME)

    data = Data()

    def process_chapter(chapter):
        pass

    def process_chunk(chunk):
        if chunk.is_direct():
            if not chunk.speaker:
                # print("unknowns speaker: {}".format(chunk.data['data']))
                pass

            speaker = chunk.speaker or Data.UNKNOWN

        else:
            speaker = Data.NARRATOR

        for word in WORD_SPLIT.split(chunk.get_data()):
            word = word.lower().strip()
            if not word:
                continue

            data.add_word(word, speaker)

    def process_sentence(sentence):
        pass

    novel.for_each(chapter=process_chapter, chunk=process_chunk, sentence=process_sentence)

    for c, ws in sorted(data.characters.items(), key=lambda x: sum(x[1].words.values())):
        print(c, len(ws.words), sum(ws.words.values()))

    data.save(args.input + '.stats')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Grab all statistics from a tagged and entity-annotated novel.')
    parser.add_argument('input', type=str, help='input tagged, annotated novel file')
    args = parser.parse_args()

    novel = Novel(args.input)
    print("novel loaded...")
    process(novel)
