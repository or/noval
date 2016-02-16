#!/bin/bash -e

for i in 01-got 02-cok 03-sos 04-ffc 05-dwd all-got; do
  echo "processing $i..."
  #./process_novel.sh $i.txt.fixed
  ./build_dialogues_json.py --groups html/data/asoiaf/groups.json $i.txt.fixed.read.tagged.entities.normalized.stats html/data/asoiaf/$i.json
done
