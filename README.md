# DCM Graph

This repository is created to store a research work for visualising delivery chain map based on [IATI store data](https://iati.cloud) and [neo4j graph database](https://neo4j.com).

## About DCM Graph
Our main goal for this project is to create a prototype Graph Database of International Aid Transparency Initiative (IATI)1 data in establishing a connection between DFID and a supplier of interest beyond immediate project funding. To do this, we have prepared a python script to import data from the [IATI store](https://iati.cloud) and prepare the necessary CSV files of Nodes and relationships for importing into a neo4j instance. 

## Get started
[Wiki](https://github.com/DFID/dcm-graph/wiki)

## JSON Data
We have imported two types of json files which are used by the python scripts of this project.
### Activities data (used by Import-and-prepare-activity-organisation-data.py) ###

Run the following command that will pull the activities json data from the IATI cloud store.

`$ wget -O all-activities.json "https://iati.cloud/search/activity?q=dataset_iati_version:"2.*"&fl=dataset_iati_version,participating_org,iati_identifier,reporting_org_*,title_*,description_*,participating_org_*,activity_status_code,related_activity_*,related_activity_ref,activity_date_*,hierarchy&wt=json&rows=5000000"`

### Transactions data (used by Prepare-transaction-csv.py) ###

Run the following command that will pull the transactions csv data from the IATI cloud store.

`$ wget -O transactions.csv "https://iati.cloud/search/transaction?q=*:*&fl=transaction_type,transaction_value,transaction_value_currency,reporting_org_narrative,iati_identifier,transaction_value_currency,transaction_provider_org_provider_activity_id,transaction_provider_org_ref,transaction_provider_org_narrative,transaction_receiver_org_receiver_activity_id,transaction_receiver_org_ref,transaction_receiver_org_narrative&wt=csv&rows=10000000"`
