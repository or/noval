#!/bin/bash

cd raw_banners
for i in $(ls -1); do
  name=$(expr match "$i" '.*house-\(.*\)-10.*')
  if [ -z "$name" ]; then
    continue
  fi
  echo $name
  ../make_banner.py $i ../html/banners/$name.jpg
done
