import json

from collections import defaultdict


class Vocabulary(object):
    def __init__(self):
        # frequencies of entities
        self.entities = defaultdict(int)
        # frequencies of words
        self.words = defaultdict(int)

    def add(self, entities, words):
        for entity, value in entities.items():
            self.entities[entity] += value

        for word, value in words.items():
            self.words[word] += value

    def add_word(self, word):
        self.words[word] += 1

    def to_dict(self):
        return {
            'entities': dict(self.entities),
            'words': dict(self.words),
        }


class Data(object):
    NARRATOR = "<narrator>"
    UNKNOWN = "<unknown>"

    def __init__(self):
        self.overall = Vocabulary()
        self.characters = defaultdict(Vocabulary)

    def add(self, entities, words, character):
        self.overall.add(entities, words)
        self.characters[character].add(entities, words)

    def add_word(self, word, character):
        self.overall.add_word(word)
        self.characters[character].add_word(word)

    def save(self, filename):
        json.dump(self.to_dict(), open(filename, 'w'), indent=4)

    def to_dict(self):
        return {
            'overall': self.overall.to_dict(),
            'characters': {k: v.to_dict() for k, v in self.characters.items()},
        }
