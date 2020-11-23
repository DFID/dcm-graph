#!/usr/bin/env bash

add-apt-repository -y ppa:openjdk-r/ppa
apt-get update
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable latest' | sudo tee -a /etc/apt/sources.list.d/neo4j.list
apt-get update
apt-get install neo4j=1:4.2.0 -y
apt install tmux -y
apt install python3-pip -y
pip3 install -U python-dotenv
pip3 install pandas
cd /var/lib/neo4j/certificates/
openssl req -newkey rsa:2048 -nodes -keyout private.key -x509 -days 365 -out public.crt