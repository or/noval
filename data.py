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


class Data(object):
    def __init__(self):
        self.overall = Vocabulary()
        self.characters = defaultdict(Vocabulary)

    def add(self, entities, words, character=None):
        self.overall.add(entities, words)
        self.characters[character].add(entities, words)
