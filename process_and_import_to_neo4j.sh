#!/usr/bin/env bash

echo "Getting iati files from iati.cloud.."

/bin/bash scripts/get_iati.sh

echo "Processing the downloaded data and creating necessary csv files for import.."

python3 scripts/prepare_data_for_import.py

echo "Importing data to the neo4j instance"

neo4j-admin import --nodes=data/0_activity_list.csv  --nodes=data/0_organisation_list.csv --relationships=data/0_parent_to_child_relation_list.csv --relationships=data/0_declare_parti_org.csv --relationship=data/0_declared_receiver_org_list.csv --relationship=data/0_declared_receiver_activity_list.csv --relationship=data/0_declared_provider_org_list.csv --relationship=data/0_declared_provider_activity_list.csv --ignore-empty-strings=true --skip-duplicate-nodes=true --skip-bad-relationships=true

#echo "Create necessary indexes"

#python3 create-neo4jdb-indexes.py