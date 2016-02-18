#!/bin/bash

root=$(pwd)
cd raw_images/banners
for i in $(ls -1); do
  name=$(expr match "$i" '.*house-\(.*\)-10.*')
  if [ -z "$name" ]; then
    name=$(expr match "$i" '.*\(nights-watch\|freefolk\)-10.*')
    if [ -z "$name" ]; then
      continue
    fi
  fi
  if [ "$name" = "frey" ]; then
    continue
  fi

  echo $name
  $root/make_banner.py $i $root/html/banners/$name.jpg
done
