#!/bin/bash

DIR="$( cd "$( dirname "$0" )" && pwd )"
cd $DIR

sudo -u minecraft ./minecraft_server.sh
