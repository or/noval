import json

from progressbar import ETA, Bar, Percentage, ProgressBar


def _uniq(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


class NovelPart(object):
    def __init__(self, data=None, parent=None):
        self.data = data or {}
        if isinstance(self.data, dict):
            self.entities = self.data.get('entities', [])
        else:
            self.entities = []

        self.children = []
        self.parent = parent
        if parent:
            parent.add_child(self)

    def add_entity(self, entity):
        self.entities.append(entity)
        if self.parent:
            self.parent.add_entity(entity)

    def get_entities(self):
        return self.entities

    def add_child(self, child):
        self.children.append(child)

    def get_children(self):
        return self.children

    def prepare_save(self):
        if isinstance(self.data, dict):
            self.data['entities'] = self.entities

        for child in self.get_children():
            child.prepare_save()


class Novel(NovelPart):
    def __init__(self, filename=None):
        super(Novel, self).__init__()
        if filename:
            self.data = json.load(open(filename))
        else:
            self.data = {}

        self.parse_structure()

    def parse_structure(self):
        self.children = []
        self.total_number_sentences = 0
        chapters = self.data['chapters']
        for chapter in chapters:
            c = Chapter(chapter, novel=self)
            for paragraph in chapter['paragraphs']:
                p = Paragraph(paragraph, chapter=c)
                for chunk in paragraph:
                    ch = ParagraphChunk(chunk, paragraph=p)
                    for sentence in chunk['sentences']:
                        Sentence(sentence, chunk=ch)
                        self.total_number_sentences += 1

    def for_each(self, chapter=None, chapter_done=None, paragraph=None, chunk=None, sentence=None):
        widgets = [Percentage(), Bar(), ETA()]
        pbar = ProgressBar(widgets=widgets, maxval=self.total_number_sentences).start()
        num_sentences = 0
        for c in self.get_children():
            if chapter:
                chapter(c)

            for p in c.get_children():
                if paragraph:
                    paragraph(p)

                for ch in p.get_children():
                    if chunk:
                        chunk(ch)

                    for s in ch.get_children():
                        pbar.update(num_sentences)
                        num_sentences += 1
                        if sentence:
                            sentence(s)

            if chapter_done:
                chapter_done(c)

        pbar.finish()

    def save(self, filename):
        self.prepare_save()
        json.dump(self.data, open(filename, 'w'), indent=4)


class Chapter(NovelPart):
    def __init__(self, data=None, novel=None):
        super(Chapter, self).__init__(data=data, parent=novel)
        self.novel = novel
        self.speakers = self.data.get('speakers', [])

    def set_speakers(self, speakers):
        self.speakers = speakers

    def prepare_save(self):
        super(Chapter, self).prepare_save()
        self.data['speakers'] = self.speakers

    @staticmethod
    def _build_entity_map(entities, edb, fallback=None):
        normalized_entities = set()
        entity_map = {}
        undecided = {}
        for name in entities:
            if name in entity_map:
                continue

            result = edb.look_up(name, normalize=True)
            if 'person' not in result:
                continue

            persons = result['person']
            candidates = list(persons)
            likely_matches = normalized_entities & persons
            if likely_matches:
                candidates = list(likely_matches)

            person = edb.decide(name, candidates)
            if not person:
                if fallback and name in fallback:
                    person = fallback[name]

                else:
                    undecided[name] = candidates
                    continue

            normalized_entities.add(person)
            entity_map[name] = person

        return entity_map, undecided

    def identify_speakers(self, edb):
        all_entity_map, all_undecided = self._build_entity_map(self.entities, edb)
        speaker_entity_map, speaker_undecided = \
            self._build_entity_map(self.speakers, edb, fallback=all_entity_map)

        for name in speaker_undecided:
            candidates = speaker_undecided[name]
            print("\n")
            print("warning: {} couldn't be decided: {}".format(name, candidates))

        self.speakers = _uniq([speaker_entity_map.get(x, x) for x in self.speakers])
        for paragraph in self.children:
            for chunk in paragraph.children:
                if chunk.is_direct() and chunk.speaker:
                    chunk.speaker = speaker_entity_map.get(chunk.speaker, chunk.speaker)


class Paragraph(NovelPart):
    def __init__(self, data=None, chapter=None):
        super(Paragraph, self).__init__(data=data, parent=chapter)
        self.chapter = chapter


class ParagraphChunk(NovelPart):
    INDIRECT = 'indirect'
    DIRECT = 'direct'
    INQUIT = 'inquit'

    def __init__(self, data=None, paragraph=None):
        super(ParagraphChunk, self).__init__(data=data, parent=paragraph)
        self.paragraph = paragraph
        self.speaker = self.data.get('speaker', None)
        self.speaker_rule = self.data.get('speaker_rule', None)
        self.potential_speakers = []

    def get_type(self):
        return self.data['type']

    def get_data(self):
        return self.data['data']

    def is_direct(self):
        return self.get_type() == ParagraphChunk.DIRECT

    def is_indirect(self):
        return self.get_type() == ParagraphChunk.INDIRECT

    def is_inquit(self):
        return self.get_type() == ParagraphChunk.INQUIT

    def prepare_save(self):
        super(ParagraphChunk, self).prepare_save()
        self.data['speaker'] = self.speaker
        self.data['speaker_rule'] = self.speaker_rule


class Sentence(NovelPart):
    def __init__(self, data=None, chunk=None):
        super(Sentence, self).__init__(data=data, parent=chunk)
        self.chunk = chunk
        self.potential_speakers = []

    def get_words(self):
        return self.data['words']


class Context(object):
    def __init__(self):
        self.last_chapter = None
        self.current_chapter = None

        self.last_paragraph = None
        self.current_paragraph = None

        self.last_chunk = None
        self.current_chunk = None

        self.first_person_in_chunk = None
        self.first_sentence_in_chunk = None

        self.speaker_history = []

        self.current_speaker = None

    def set_current_speaker(self, speaker, rule):
        self.current_chunk.speaker = speaker
        self.current_chunk.speaker_rule = rule
        self.current_speaker = speaker
        if not self.speaker_history or self.speaker_history[-1] != speaker:
            self.speaker_history.append(speaker)

    def change_last_speaker(self, speaker):
        if not self.last_chunk:
            return

        if self.last_chunk.speaker == speaker:
            return

        self.last_chunk.speaker = speaker

        if self.speaker_history and self.speaker_history[-1] == self.last_chunk.speaker:
            self.speaker_history[-1] = speaker
        else:
            self.speaker_history.append(speaker)

    def set_chapter(self, chapter):
        if chapter == self.current_chapter:
            return

        self.last_chapter = self.current_chapter
        self.current_chapter = chapter

        self.speaker_history = []

        self.current_paragraph = None
        self.set_paragraph(None)

        self.current_speaker = None

    def set_paragraph(self, paragraph):
        if paragraph and paragraph == self.current_paragraph:
            return

        if paragraph:
            self.set_chapter(paragraph.chapter)

        self.last_paragraph = self.current_paragraph
        self.current_paragraph = paragraph

        self.current_chunk = None
        self.set_chunk(None)

        self.current_speaker = None

    def find_most_likely_speaker(self, chunk):
        first_per_chunk = []

        for child in chunk.paragraph.children:
            if child == chunk:
                break

            if child.is_direct():
                first_per_chunk = []
            else:
                for sentence in child.children:
                    if sentence.potential_speakers:
                        first_per_chunk.append(sentence.potential_speakers[0])

        if first_per_chunk:
            return first_per_chunk[-1]

        return None

    def set_chunk(self, chunk):
        if chunk and chunk == self.current_chunk:
            return

        if chunk:
            self.set_paragraph(chunk.paragraph)

        self.last_chunk = self.current_chunk
        self.current_chunk = chunk

        self.first_person_in_chunk = None
        self.first_sentence_in_chunk = None

        if self.is_direct():
            first_chunk = chunk.paragraph.children[0]
            most_likely_speaker = self.find_most_likely_speaker(chunk)

            if self.current_speaker:
                self.set_current_speaker(self.current_speaker, rule="kept")

            elif most_likely_speaker:
                self.set_current_speaker(most_likely_speaker, rule="most_likely")

            # if the paragraph starts with an indirect chunk but
            # since then we've found no likely speaker, then
            # assume the speaker hasn't changed
            elif (chunk != first_chunk and first_chunk.is_indirect and
                  self.speaker_history):
                self.set_current_speaker(self.speaker_history[-1], "last_known")

            # TODO need a rule to change the speaker if a new speaker was
            # *addressed* in the last direct chunk

            elif len(self.speaker_history) > 1:
                self.set_current_speaker(self.speaker_history[-2], "dialogue")

    def is_direct(self):
        if self.current_chunk and self.current_chunk.is_direct():
            return True

        return False

    def is_indirect(self):
        if self.current_chunk and self.current_chunk.is_indirect():
            return True

        return False

    def is_inquit(self):
        if self.current_chunk and self.current_chunk.is_inquit():
            return True

        return False

    def was_direct(self):
        if self.last_chunk and self.last_chunk.is_direct():
            return True

        return False

    def was_indirect(self):
        if self.last_chunk and self.last_chunk.is_indirect():
            return True

        return False

    def was_inquit(self):
        if self.last_chunk and self.last_chunk.is_inquit():
            return True

        return False

    def process_chapter_done(self, chapter):
        chapter.set_speakers(self.speaker_history)
        self.speaker_history = []

    def process_sentence(self, sentence, edb):
        self.set_chunk(sentence.chunk)

        if not self.first_sentence_in_chunk:
            self.first_sentence_in_chunk = sentence

        for entity in edb.enumerate_entities(sentence.get_words()):
            entities = edb.look_up(entity)
            if not entities:
                continue

            sentence.add_entity(entity)

            if not self.is_direct():
                if 'person' in entities:
                    self.current_chunk.potential_speakers.append(entity)
                    sentence.potential_speakers.append(entity)

            if self.is_inquit() and sentence == self.first_sentence_in_chunk:
                if 'person' in entities and not self.first_person_in_chunk:
                    self.first_person_in_chunk = entity
                    self.current_speaker = entity
                    if self.was_direct():
                        self.change_last_speaker(entity)

            self.last_sentence = sentence
