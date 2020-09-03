#!/usr/bin/env bash

mkdir data/reports/

# remeber to set your neo4j password as $NEO4J_PW as an environment variable!

timestamp() {
  date +"%Y-%m-%dT%T.%3N%z"
}

echo $(timestamp)" - beginning process"

cd cypher/load_chunks

for file in *.cyp
do
  echo $(timestamp) - processing $file ...
  neo4j-client -u neo4j -p $NEO4J_PW -o ../../data/reports/$file.out -i $file bolt://iatigraph.eastus.azurecontainer.io:7687
  sleep 10 # wait 10 seconds to avoid confusing neo4j transactions
done