"""
Wrapper around the Stanford Parser.

"""
import sys
from java.io import StringReader

JAR_FILE = '/home/thi/stanford-postagger/stanford-postagger.jar'
MODEL = '/home/thi/stanford-postagger/models/english-bidirectional-distsim.tagger'


def load_stanford_postagger():
    if JAR_FILE not in sys.path:
        sys.path.append(JAR_FILE)

    from edu.stanford.nlp.tagger.maxent import MaxentTagger
    return MaxentTagger(MODEL)


def get_tags(tagger, data):
    sentences = tagger.tokenizeText(StringReader(data))
    output = []
    for sentence in sentences:
        output.append([(x.word(), x.tag()) for x in tagger.tagSentence(sentence)])
    return output
