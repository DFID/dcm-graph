#!/usr/bin/env bash

add-apt-repository ppa:cleishm/neo4j -y
apt update
apt upgrade -y
apt install tmux -y

apt install -y neo4j-client libneo4j-client-dev

apt install python3-pip -y
pip3 install pandas
