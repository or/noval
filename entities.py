import json
from collections import defaultdict


def _set2list(entities, path):
    obj = entities
    for chunk in path[:-1]:
        obj = entities[chunk]

    last = path[-1]
    if last == '*':
        for k, v in obj.items():
            obj[k] = list(sorted(v))

    else:
        obj[last] = list(sorted(obj.get(last, set())))


def _list2set(entities, path):
    obj = entities
    for chunk in path[:-1]:
        obj = entities[chunk]

    last = path[-1]
    if last == '*':
        for k, v in obj.items():
            obj[k] = set(v)

    else:
        obj[last] = set(obj.get(last, []))


class EntityDatabase(object):
    SET_PATHS = (
        ['gender', '*'],
        ['title', '*'],
        ['person', '*'],
        ['organization', '*'],
        ['place', '*'],
        ['ignore'],
        ['unknown'],
    )

    def __init__(self):
        self.entities = self._get_empty_entities()
        self.known = self.get_all_known_entities()

    @classmethod
    def _get_empty_entities(cls):
        return {
            'person': {},
            'organization': {},
            'place': {},
            'unknown': set(),
            'title': {
                'person': [],
                'organization': [],
                'place': [],
            },
            'gender': {
                'male': set(),
                'female': set(),
                'neuter': set(),
            },
            'ignore': set(),
        }

    def _ensure_sets(self):
        for path in EntityDatabase.SET_PATHS:
            _list2set(self.entities, path)

    def _ensure_lists(self):
        for path in EntityDatabase.SET_PATHS:
            _set2list(self.entities, path)

    def load(self, filename):
        self.entities = EntityDatabase._get_empty_entities()
        read_entities = json.load(open(filename))
        self.entities.update(read_entities)
        self._ensure_sets()

        self.known = self.get_all_known_entities()

    def save(self, filename):
        self._ensure_lists()
        json.dump(self.entities, open(filename, 'w'), indent=4)
        self._ensure_sets()

    def get_all_known_entities(self):
        known = set()
        for kind in ('person', 'organization', 'place'):
            for word in self.entities['title'][kind]:
                known.add(word)

            for word in self.entities[kind]:
                known.add(word)
                for w in self.entities[kind][word]:
                    known.add(w)

        for word in self.entities['ignore']:
            known.add(word)

        return known

    def compact(self):
        """
        Remove unknown single words that occur in already known entities.
        These will be first names, last names, parts of the place name and so on.
        """
        single_words = defaultdict(list)
        full = set()

        for kind in ('person', 'organization', 'place'):
            for entity in self.entities[kind]:
                full.add(entity)
                for word in entity.split():
                    single_words[word].append([kind, entity])

                for alias in self.entities[kind][entity]:
                    full.add(alias)
                    for word in alias.split():
                        single_words[word].append([kind, entity])

        # using a copied list here, allows mutating the set inside the loop
        for x in list(self.entities['unknown']):
            if x in single_words or x in full:
                self.entities['unknown'].remove(x)
                for path in single_words[x]:
                    self.entities[path[0]][path[1]].add(x)

            elif x.endswith('s'):
                singular = x[:-1]
                if singular in single_words:
                    self.entities['unknown'].remove(x)
                    for path in single_words[singular]:
                        if path[0] == 'organization':
                            self.entities[path[0]][path[1]].add(x)

        for word in single_words:
            for path in single_words[word]:
                self.entities[path[0]][path[1]].add(word)

        self.known = self.get_all_known_entities()

    def enumerate_entities(self, tagged_words):
        def assemble(words):
            return ' '.join(x['word'] for x in words)

        last_words = []
        for word in tagged_words:
            if word['tag'] != 'NNP' or word['word'] in self.entities['ignore']:
                if last_words:
                    entity = assemble(last_words)
                    if entity not in self.entities['ignore']:
                        yield entity

                    last_words = []

                continue

            last_words.append(word)

        if last_words:
            yield assemble(last_words)

    def add(self, entity):
        if not entity:
            return

        for kind in ('person', 'organization'):
            for title in self.entities['title'][kind]:
                if entity == title:
                    return

                if not entity.startswith(title + ' '):
                    continue

                raw_entity = entity[len(title) + 1:]
                aliases = self.entities[kind].get(raw_entity, set())
                if raw_entity != entity:
                    aliases.add(entity)

                aliases.add(title)
                self.entities[kind][raw_entity] = aliases

                return

        self.entities['unknown'].add(entity)
        self.known.add(entity)

    def get_stats(self):
        stats = {'num_' + k: len(v) for k, v in self.entities.items()}

        return stats
