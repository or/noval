import json
import re
from collections import defaultdict

ENTITY = re.compile(r'P(s?(p?[NP]s?)*(a|ia|oa|o)?(p?[NP]s?)*(p?[NP]))*')


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
        ['force'],
    )

    def __init__(self):
        self.entities = self._get_empty_entities()
        self.build_reverse_map()

    @staticmethod
    def _get_empty_entities():
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
            'force': set(),
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

        self.build_reverse_map()

    def save(self, filename):
        self._ensure_lists()
        json.dump(self.entities, open(filename, 'w'), indent=4)
        self._ensure_sets()

    def build_reverse_map(self):
        self.reverse_map = defaultdict(set)
        for kind in ('person', 'organization', 'place'):
            for entity, aliases in self.entities[kind].items():
                self.reverse_map[entity].add(tuple([kind, entity]))
                for alias in aliases:
                    self.reverse_map[alias].add(tuple([kind, entity]))

            for title in self.entities['title'][kind]:
                self.reverse_map[title].add(tuple(['title', kind]))

        for entity in self.entities['ignore']:
            self.reverse_map[entity].add(tuple(['ignore']))

    def enumerate_entities(self, tagged_words):
        def assemble(words):
            s = ' '.join(x['word'] for x in words)
            return s.replace(" 's", "'s")

        def represent(tagged_word, is_first_in_sentence=False):
            tag = tagged_word['tag']
            word = tagged_word['word']

            if not is_first_in_sentence and word != "I" and \
               word[0].isalpha() and word[0].upper() == word[0]:
                return 'P'

            elif word in self.entities['force']:
                return 'P'

            elif word in self.entities['ignore'] or word.lower() in self.entities['ignore']:
                return 'x'

            elif tag in ('NNP', 'NNPS'):
                return 'P'

            elif tag == 'NN' and word[0] == word[0].upper():
                return 'N'

            elif word.lower() == 'in':
                return 'i'

            elif word.lower() == 'of':
                return 'o'

            elif tag == 'DT':
                return 'a'

            elif tag == 'POS':
                return 's'

            elif tag == 'PRP$':
                return 'p'

            return 'x'

        tag_string = ''.join(represent(x, i == 0) for i, x in enumerate(tagged_words))
        for mo in ENTITY.finditer(tag_string):
            entity = assemble(tagged_words[mo.start():mo.end()])
            yield entity

    def add(self, entity):
        if not entity:
            return

        if entity in self.entities['ignore']:
            return

        if entity in self.reverse_map:
            return

        entities_without_title = set([entity])
        added = False
        for kind in ('person', 'organization', 'place'):
            for title in self.entities['title'][kind]:
                if entity == title:
                    continue

                if not entity.startswith(title + ' '):
                    continue

                real_entity = entity[len(title) + 1:]
                if real_entity[0] != real_entity[0].upper():
                    # these will be titles, like "Warden of the North",
                    # we only auto classify entities that start with an
                    # uppercase letter after the title
                    continue

                entities_without_title.add(real_entity)

        real_entity = list(sorted(entities_without_title, key=lambda x: len(x)))[0]
        real_title = entity[:-len(real_entity)].strip()
        real_kind = None
        real_gender = None
        if real_title:
            for kind in ('person', 'organization', 'place'):
                if real_title in self.entities['title'][kind]:
                    real_kind = kind
                    break

            for gender, titles in self.entities['gender'].items():
                if real_title in titles:
                    real_gender = gender
                    break

        # "added" is used to track whether it was added at least once,
        # but it could be added multiple times, so there is no break
        # after "added" is set to True

        # only do this matching for persons
        for kind in ('person',):
            if real_kind and kind != real_kind:
                continue

            for known_entity in self.entities[kind]:
                if not (' ' + real_entity + ' ' in ' ' + known_entity + ' ' or
                        ' ' + known_entity + ' ' in ' ' + real_entity + ' '):
                    continue

                if real_title:
                    known_genders = set()
                    for alias in self.entities[kind][known_entity]:
                        for gender, titles in self.entities['gender'].items():
                            if alias in titles:
                                known_genders.add(gender)

                    if known_genders and real_gender not in known_genders:
                        continue

                self.entities[kind][known_entity].add(entity)

                self.reverse_map[entity].add(tuple([kind, known_entity]))
                if real_title:
                    self.reverse_map[real_title].add(tuple([kind, known_entity]))

                added = True

        if not added and real_kind:
            if real_entity not in self.entities[real_kind]:
                self.entities[real_kind][real_entity] = set()

            self.entities[real_kind][real_entity].add(real_title)
            self.reverse_map[real_entity].add(tuple([real_kind, real_entity]))
            if real_title:
                self.reverse_map[real_title].add(tuple([real_kind, real_entity]))

            if real_entity != entity:
                self.entities[real_kind][real_entity].add(entity)
                self.reverse_map[entity].add(tuple([real_kind, real_entity]))

            added = True

        if not added:
            self.entities['unknown'].add(entity)

    def get_stats(self):
        stats = {'num_' + k: len(v) for k, v in self.entities.items()}

        return stats

    def clear_unknown(self):
        self.entities['unknown'] = set()

    def clear_aliases(self):
        for kind in ('person', 'organization', 'place'):
            for key in self.entities[kind]:
                self.entities[kind][key] = set()

        self.build_reverse_map()

    def look_up(self, entity, normalize=False):
        if entity not in self.reverse_map:
            return None

        if entity in self.entities['ignore']:
            return None

        paths = self.reverse_map[entity]
        result = defaultdict(set)
        for path in paths:
            if normalize:
                result[path[0]].add(path[-1])
            else:
                result[path[0]].add(entity)

        return dict(result)

    def decide(self, name, candidates):
        if len(candidates) == 1:
            return candidates[0]

        result = self.entities['preference'].get(name)
        if result and result in candidates:
            return result

        return None
