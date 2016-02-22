#!/bin/bash

cd html/images/characters
IFS=$(echo -en "\n\b")
for i in $(ls -1 *.jpg); do
    convert $i -resize 200x -quality 95 small/$i
done
