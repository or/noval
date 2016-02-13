#!/bin/bash
cd pics
IFS=$(echo -en "\n\b")
for i in $(ls -1 *.jpg); do
    convert $i -resize 400x -quality 95 small/$i
done