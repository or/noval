#!/usr/bin/env python3
"""
Generate stats

"""
import argparse
import re

from data import Data
from entities import EntityDatabase
from structure import Novel

ENTITIES_FILENAME = 'entities.json'
WORD_SPLIT = re.compile(r'[ ,.!?]')
DIALOGUE_SEPARATOR_LENGTH = 3


def get_surrounding_speakers(index, dialogue_stats):
    current = dialogue_stats[index][0]
    before = None
    after = None

    i = index - 1
    count_narrator = 0
    while i >= 0 and count_narrator < DIALOGUE_SEPARATOR_LENGTH:
        speaker = dialogue_stats[i][0]
        if speaker == Data.NARRATOR:
            count_narrator += 1
        elif speaker == current:
            count_narrator = 0
        else:
            before = speaker
            break

        i -= 1

    count_narrator = 0
    i = index + 1
    while i < len(dialogue_stats) and count_narrator < DIALOGUE_SEPARATOR_LENGTH:
        speaker = dialogue_stats[i][0]
        if speaker == Data.NARRATOR:
            count_narrator += 1
        elif speaker == current:
            count_narrator = 0
        else:
            after = speaker
            break

        i += 1

    return before, after


def process(novel):
    edb = EntityDatabase()
    edb.load(ENTITIES_FILENAME)

    data = Data()
    dialogue_stats = []

    def process_chapter(chapter):
        global dialogue_stats
        dialogue_stats = []

    def process_chapter_done(chapter):
        global dialogue_stats

        for i, (speaker, words) in enumerate(dialogue_stats):
            if speaker == data.NARRATOR:
                continue

            before, after = get_surrounding_speakers(i, dialogue_stats)
            score = len(words)
            if before and after and before != after:
                # with different persons before and after this speech
                # assume half of it was meant for the last person, half
                # of it for the next
                score //= 2

            if before:
                data.add_talked_to(speaker, before, score)

            if after:
                data.add_talked_to(speaker, after, score)

    def process_chunk(chunk):
        global dialogue_stats

        if chunk.is_direct():
            if not chunk.speaker:
                # print("unknowns speaker: {}".format(chunk.data['data']))
                pass

            speaker = chunk.speaker or Data.UNKNOWN

        else:
            speaker = Data.NARRATOR

        words = []
        for word in WORD_SPLIT.split(chunk.get_data()):
            word = word.lower().strip()
            if not word:
                continue

            words.append(word)
            data.add_word(word, speaker)

        dialogue_stats.append((speaker, words))

    novel.for_each(chapter=process_chapter, chapter_done=process_chapter_done,
                   chunk=process_chunk)

    data.save(args.input + '.stats')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Grab all statistics from a tagged and entity-annotated novel.')
    parser.add_argument('input', type=str, help='input tagged, annotated novel file')
    args = parser.parse_args()

    novel = Novel(args.input)
    print("novel loaded...")
    process(novel)
