#!/bin/bash

imageName=intro-bot
containerName=intro-bot

docker build -t $imageName -f Dockerfile  .

echo Delete old container...
docker rm -f $containerName

echo Run new container...
docker run --name $containerName $imageName
