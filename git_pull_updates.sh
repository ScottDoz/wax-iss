#!/bin/bash

echo "git fetch"
cd ~/wax-iss
git fetch
sleep 1

echo "git status"
git status
sleep 5

echo "git pull"
git pull
sleep 10
