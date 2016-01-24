import json
from collections import defaultdict

ENTITIES_FILENAME = 'entities.json'


def set2list(entities, path):
    obj = entities
    for chunk in path[:-1]:
        obj = entities[chunk]

    last = path[-1]
    if last == '*':
        for k, v in obj.items():
            obj[k] = list(sorted(v))

    else:
        obj[last] = list(sorted(obj.get(last, set())))


def list2set(entities, path):
    obj = entities
    for chunk in path[:-1]:
        obj = entities[chunk]

    last = path[-1]
    if last == '*':
        for k, v in obj.items():
            obj[k] = set(v)

    else:
        obj[last] = set(obj.get(last, []))


def use_sets(entities):
    for path in (['gender', '*'],
                 ['title', '*'],
                 ['person', '*'],
                 ['organization', '*'],
                 ['place', '*'],
                 ['ignore'],
                 ['unknown']):
        list2set(entities, path)


def use_lists(entities):
    for path in (['gender', '*'],
                 ['title', '*'],
                 ['person', '*'],
                 ['organization', '*'],
                 ['place', '*'],
                 ['ignore'],
                 ['unknown']):
        set2list(entities, path)


def empty_entities():
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


def load_entities():
    entities = empty_entities()
    read_entities = json.load(open(ENTITIES_FILENAME))
    use_sets(read_entities)
    entities.update(read_entities)
    return entities


def store_entities(entities):
    use_lists(entities)
    json.dump(entities, open('generated.' + ENTITIES_FILENAME, 'w'), indent=4)
    use_sets(entities)


def get_all_known_entities(entities):
    known = set()
    for kind in ('person', 'organization', 'place'):
        for word in entities[kind]:
            known.add(word)
            for w in entities[kind][word]:
                known.add(w)

    for word in entities['ignore']:
        known.add(word)

    return known


def compact_entities(entities):
    """
    Remove unknown single words that occur in already known entities.
    These will be first names, last names, parts of the place name and so on.
    """
    single_words = defaultdict(list)
    full = set()

    for kind in ('person', 'organization', 'place'):
        for entity in entities[kind]:
            full.add(entity)
            for word in entity.split():
                single_words[word].append([kind, entity])

            for alias in entities[kind][entity]:
                full.add(alias)
                for word in alias.split():
                    single_words[word].append([kind, entity])

    # using a copied list here, allows mutating the set inside the loop
    for x in list(entities['unknown']):
        if x in single_words or x in full:
            entities['unknown'].remove(x)
            for path in single_words[x]:
                entities[path[0]][path[1]].add(x)

        elif x.endswith('s'):
            singular = x[:-1]
            if singular in single_words:
                entities['unknown'].remove(x)
                for path in single_words[singular]:
                    if path[0] == 'organization':
                        entities[path[0]][path[1]].add(x)

    for word in single_words:
        for path in single_words[word]:
            entities[path[0]][path[1]].add(word)


def enumerate_entities(tagged_words, entities):
    def assemble(words):
        return ' '.join(x['word'] for x in words)

    last_words = []
    for word in tagged_words:
        if word['tag'] != 'NNP' or word['word'] in entities['ignore']:
            if last_words:
                entity = assemble(last_words)
                if entity not in entities['ignore']:
                    yield entity

                last_words = []

            continue

        last_words.append(word)

    if last_words:
        yield assemble(last_words)


def add_entity(entities, known, entity):
    if not entity:
        return

    if entity in known:
        return

    for kind in ('person', 'organization'):
        for title in entities['title'][kind]:
            if entity == title:
                return

            if not entity.startswith(title + ' '):
                continue

            raw_entity = entity[len(title) + 1:]
            aliases = entities[kind].get(raw_entity, set())
            if raw_entity != entity:
                aliases.add(entity)

            aliases.add(title)
            entities[kind][raw_entity] = aliases

            return

    entities['unknown'].add(entity)


def get_entities_stats(entities):
    stats = {'num_' + k: len(v) for k, v in entities.items()}

    return stats
