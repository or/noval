import json

from progressbar import ETA, Bar, Percentage, ProgressBar


class Entity(object):
    def __init__(self, name):
        self.name = name
        self.aliases = set([name])

    def __unicode__(self):
        return '%s:%s' % (self.__class__.__name__, self.name)

    def __lt__(self, o):
        if self.__class__ != o.__class__:
            return self.__class__ < o.__class__

        return self.name < o.name

    def __eq__(self, o):
        return self.__class__ == o.__class__ and self.name == o.name


class Character(Entity):
    def __init__(self, name):
        super(Character, self).__init__(name)


class Organization(Entity):
    def __init__(self, name):
        super(Organization, self).__init__(name)


class Place(Entity):
    def __init__(self, name):
        super(Place, self).__init__(name)


class Scene(object):
    """
    The current scene while analysing the novel.
    It contains information like the place and the characters involved in the scene.

    """

    def __init__(self):
        self.characters = set()
        self.last_speakers = []

    def add_speaker(self, speaker):
        if self.get_speaker(-1) != speaker:
            self.last_speakers.append(speaker)

    def get_speaker(self, index):
        try:
            return self.last_speakers[index]
        except IndexError:
            return None


class Novel(object):
    def __init__(self, filename=None):
        if filename:
            self.data = json.load(open(filename))
        else:
            self.data = {}

    def for_each_sentence(self, function):
        chapters = self.data['chapters']
        total_number_paragraphs = \
            sum([len(chunk['sentences'])
                 for c in chapters
                 for p in c['paragraphs'] for chunk in p])

        widgets = [Percentage(), Bar(), ETA()]
        pbar = ProgressBar(widgets=widgets, maxval=total_number_paragraphs).start()
        num_sentences = 0
        for chapter in chapters:
            for paragraph in chapter['paragraphs']:
                for chunk in paragraph:
                    for sentence in chunk['sentences']:
                        pbar.update(num_sentences)
                        num_sentences += 1

                        function(Sentence(sentence))

        pbar.finish()


class Chapter(object):
    def __init__(self, data=None):
        self.data = data or {}


class Paragraph(object):
    def __init__(self, data=None):
        self.data = data or {}


class ParagraphChunk(object):
    def __init__(self, data=None):
        self.data = data or {}


class Sentence(object):
    def __init__(self, data=None):
        self.data = data or {}

    def get_words(self):
        return self.data['words']
