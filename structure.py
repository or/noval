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
