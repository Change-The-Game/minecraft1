#!/bin/bash

mcmemmb=7936

for (( ; ; ))
do
        java -Xmx${mcmemmb}M -jar minecraft_server.jar nogui
        echo "Server closed unexpectedly, restarting in 10 seconds..."
        sleep 10
done
