# noval
Analyse and visualize novels, to make some hopefully interesting observations.

# Analysis
The idea is to parse all sentences, recognize proper nouns as entities (persons, organizations, places), 
then figure out who is talking and to whom and what about... from the context and the way most novels are written.

Currently it figures out dialogues, but places would be nice as well, corelation between characters and persons in particular.

## Requirements
 * Python3
 * `pip install -r requirements.txt`
 * Stanford POS Tagger: http://nlp.stanford.edu/software/tagger.shtml#Download (the JAR must be somewhere in the classpath)

## Visualization
Uses d3 (https://d3js.org/).

Currently it renders an interactive graph showing the characters talking most to each other, and therefore likely being
close to each other or at least involved in some way.

In addition I'd like to show some stats on vocabulary and vocabulary-per-character, which in very well-written novels
might be distinctive (my assumption). Furthermore there could be a "time" line as the novel progresses.

Once places are parsed out nicely, it'd be nice to show characters on a map (just have to manually set certain points
as the geo position of the entities) and again perhaps animate their movements throughout the novel.

## A Song of Ice and Fire
ASOIF was the first choice and the trigger for the idea, because of the big number of characters and all their interactions,
it also has very consistent structure, e.g. each chapter is named after a character, which I thought would even help
guessing the context. Tho in the current version that information isn't even used anymore.

## Accuracy
I think the scripts perform quite well. Most random samples of the annotated JSON files show a pretty decent
detection of who is the speaker and who is he/she talking to.

However, it is not perfect. Sometimes it requires a human brain to understand who took over the dialogue and
the (messy) heuristics I use probably also aren't perfect. A good measure and an indicator that the scripts
are not 100% correct is Hodor's vocabulary... of over 100 distinct words. Work in progress. ;)

That being said, the few times the scripts annotate wrongly don't change the graph that much, because when
a line is annotated with the wrong speaker, it *usually* is a character present in the scene, so still
adding to the right nodes of the graphs.

## Observations
Some things one'd expect are nicely visualized now:
 * a thick, close edge between Eddard Stark and Robert Baratheon in the first book, their relationship is very 
   dominant in the first book
 * similarly Tyrion Lannister and Bronn are "close"
 * the whole prologue forms a sub graph (the 3 pictureless nodes only talking among each other)
 * the whole Daenerys arc forms a sub graph, except for a very thin line between Daenerys and Robert, I believe that's
   another inaccuracy, where Robert talks *about* Daenerys

One example of a surprise:
 * Jaime Lannister and Cersei Lannister have almost no interactions in the first book, according to the scripts,
   manual checking revealed: they are together in a group at times, but rarely talk to each other, which seems
   like very clever and subtle writing. The main scene they DO talk to each other is their congress in the tower,
   when Bran discovers their relationship... but only when I checked that scene to figure out why the script
   missed it, I realized that the novel only refers to them as "the man" or "he" and "the woman" or "she", which
   of course is beyond the understanding capabilities of the script.

## Usage
The steps are as follows:
```bash
echo "reading..."
./read.py $1
echo "parsing..."
java -classpath . Parser $1.read
echo "assigning entities..."
./assign_entities.py $1.read.tagged
echo "normalizing entities..."
./normalize_entities.py $1.read.tagged.entities
echo "generate statistics..."
./generate_stats.py $1.read.tagged.entities.normalized
```
It's single scripts because each step can take a while and since there might be manual steps to clean up data or annotate
it, I made each script standalone.

 * read: read a text file in, trying to parse chapters, paragraphs, chunks of a paragraph 
   (indirect speech, inquit, direct speech), output that to `$1.read` in JSON format
 * parse: use the Stanford POS Tagger, to recognize all words in all sentences, include that info in the JSON, output
   to `$1.tagged`
 * assign entities: guess which entity is speaker for all direct speech chunks, write to `$1.entities`
 * normalize entities: map all raw entities to a canonical name, as defined by `entities.json`, e.g. Tyrion Lannister,
   Tyrion, dwarf, imp, halfman... are all aliases for the same character, write to `$1.normalized`
 * generate statistics: read all the data and aggregate it into something useful, write to `$1.stats`

Finally there's a script `./build_dialogues_json.py` that uses the stats file to generate JSON data for the visualization.

A semi-manual step is needed after parsing and before assigning entities: `find_potential_entities.py` reads (or creates a fresh) `entities.json`, reads the tagged data, and guesses which entities are persons, based on titles and such. It
generates `generated.entities.json`, which can be used to update `entities.json`. However, `entities.json` requires quite
a bit of manual work to map all aliases to the same character and decide which entities to ignore, it also allows
specifying some whitelist for words that should be treated as entities, even tho the tagger tagged them as normal words.

## Disclaimer
The A Song of Ice and Fire series and its characters were created and are owned by George R.R. Martin, 
who holds the copyright. This project is not affiliated with George R.R. Martin.

Some images and graphics used on this website were created and are owned by HBO, the copyright of which 
is held by HBO. All trademarks and registered trademarks present in the images are proprietary to HBO, 
the inclusion of which implies no affiliation with this project. The use of such images is believed to 
fall under the fair use of copyright law. The copyright holder can request their removal at any time.
