import json

from progressbar import ETA, Bar, Percentage, ProgressBar


class NovelPart(object):
    def __init__(self, data=None, parent=None):
        self.data = data or {}
        self.entities = {
            'person': {},
            'organization': {},
            'place': {},
            'title': {},
        }
        self.children = []
        self.parent = parent
        if parent:
            parent.add_child(self)

    def add_entities(self, entities):
        for kind, values in entities.items():
            for e in values:
                n = values[e] if isinstance(values, dict) else 1
                self.entities[kind][e] = self.entities[kind].get(e, 0) + n

    def get_entities(self):
        return self.entities

    def collect_entities(self):
        for child in self.get_children():
            self.add_entities(child.get_entities())

    def add_child(self, child):
        self.children.append(child)

    def get_children(self):
        return self.children

    def prepare_save(self):
        if isinstance(self.data, dict):
            # self.data['entities'] = {k: list(sorted(v)) for k, v in self.entities.items()}
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

    def for_each_sentence(self, function):
        widgets = [Percentage(), Bar(), ETA()]
        pbar = ProgressBar(widgets=widgets, maxval=self.total_number_sentences).start()
        num_sentences = 0
        for chapter in self.get_children():
            for paragraph in chapter.get_children():
                for chunk in paragraph.get_children():
                    for sentence in chunk.get_children():
                        pbar.update(num_sentences)
                        num_sentences += 1
                        function(sentence)

        pbar.finish()

    def save(self, filename):
        self.prepare_save()
        json.dump(self.data, open(filename, 'w'), indent=4)


class Chapter(NovelPart):
    def __init__(self, data=None, novel=None):
        super(Chapter, self).__init__(data=data, parent=novel)
        self.novel = novel
        self.speakers = []

    def set_speakers(self, speakers):
        self.speakers = speakers

    def prepare_save(self):
        super(Chapter, self).prepare_save()
        self.data['speakers'] = self.speakers


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
        self.speaker = None
        self.potential_speakers = []

    def get_type(self):
        return self.data['type']

    def is_direct(self):
        return self.get_type() == ParagraphChunk.DIRECT

    def is_indirect(self):
        return self.get_type() == ParagraphChunk.INDIRECT

    def is_inquit(self):
        return self.get_type() == ParagraphChunk.INQUIT

    def prepare_save(self):
        super(ParagraphChunk, self).prepare_save()
        self.data['speaker'] = self.speaker


class Sentence(NovelPart):
    def __init__(self, data=None, chunk=None):
        super(Sentence, self).__init__(data=data, parent=chunk)
        self.chunk = chunk

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

    def set_current_speaker(self, speaker):
        self.current_chunk.speaker = speaker
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

        if self.last_chapter:
            self.last_chapter.set_speakers(self.speaker_history)

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
            if self.current_speaker:
                self.set_current_speaker(self.current_speaker)

            elif self.last_chunk and self.last_chunk.potential_speakers:
                self.set_current_speaker(self.last_chunk.potential_speakers[0])

            elif len(self.speaker_history) > 1:
                self.set_current_speaker(self.speaker_history[-2])

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

    def process_sentence(self, sentence, edb):
        self.set_chunk(sentence.chunk)

        if not self.first_sentence_in_chunk:
            self.first_sentence_in_chunk = sentence

        for entity in edb.enumerate_entities(sentence.get_words()):
            entities = edb.look_up(entity)
            if not entities:
                continue

            sentence.add_entities(entities)

            if not self.is_direct():
                if 'person' in entities:
                    self.current_chunk.potential_speakers.append(entity)

            if self.is_inquit() and sentence == self.first_sentence_in_chunk:
                if 'person' in entities and not self.first_person_in_chunk:
                    self.first_person_in_chunk = entity
                    self.current_speaker = entity
                    if self.was_direct():
                        self.change_last_speaker(entity)

                    self.last_sentence = sentence

            elif self.is_indirect():
                if 'person' in entities:
                    self.last_mentioned_person = entity
