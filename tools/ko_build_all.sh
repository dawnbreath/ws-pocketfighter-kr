#!/bin/sh
# usage: ko_build_all.sh OUT.ws
cd /home/user/pocketfighter/tools && python3 build.py "$1" --img --ko ../text/ko/story.json ../text/ko/fixed.json ../text/ko/wg.json
