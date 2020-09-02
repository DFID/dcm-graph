#!/usr/bin/env bash

mkdir data/
cd data

# Create a crude download log file if it doesn't aready exist.
touch download_log.txt

# Define a timestamp function
timestamp() {
  date +"%Y-%m-%dT%T.%3N%z"
}

echo Getting Activities JSON file...

echo $(timestamp): begin download >> download_log.txt

wget -O all-activities.json "https://iati.cloud/search/activity?q=dataset_iati_version:"2.*"&fl=dataset_iati_version,participating_org,iati_identifier,reporting_org_ref,reporting_org_narrative,title_narrative,description,participating_org,activity_status_code,related_activity_type,related_activity_ref,activity_date_start_*,activity_date_end_*,hierarchy&wt=json&rows=5000000"

echo $(timestamp): activites downloaded >> download_log.txt

echo Getting Transactions CSV file...

wget -O transactions.csv "https://iati.cloud/search/transaction?q=*:*&fl=transaction_type,transaction_value,transaction_value_currency,reporting_org_narrative,iati_identifier,transaction_value_currency,transaction_provider_org_provider_activity_id,transaction_provider_org_ref,transaction_provider_org_narrative,transaction_receiver_org_receiver_activity_id,transaction_receiver_org_ref,transaction_receiver_org_narrative&wt=csv&rows=10000000"

echo $(timestamp): transactions downloaded >> download_log.txt

cd ..
touch z.delete.me.download.$(timestamp).is.done