#!/bin/bash -e

echo "reading..."
#./read.py $1
echo "parsing..."
#java -classpath . Parser $1.read
echo "assigning entities..."
./assign_entities.py $1.read.tagged
echo "normalizing entities..."
./normalize_entities.py $1.read.tagged.entities
echo "generate statistics..."
./generate_stats.py $1.read.tagged.entities.normalized
