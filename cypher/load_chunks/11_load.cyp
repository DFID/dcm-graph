USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'http://rsdevbox.eastus.cloudapp.azure.com/0_transaction_downrefs_list.csv' AS row
MATCH (reportedActivity:Activities {ActivityIdentifier: row.iati_identifier})
MATCH (relatedActivity:Activities {ActivityIdentifier: row.transaction_receiver_org_receiver_activity_id})
MERGE (reportedActivity)-[:DECLARES_TRANSACTION_RECEIVER_ACTIVITY]->(relatedActivity);