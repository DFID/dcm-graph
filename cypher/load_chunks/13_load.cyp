USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'http://rsdevbox.eastus.cloudapp.azure.com/0_transaction_uprefs_list.csv' AS row
MATCH (reportedActivity:Activities {ActivityIdentifier: row.iati_identifier})
MATCH (relatedActivity:Activities {ActivityIdentifier: row.transaction_provider_org_provider_activity_id})
MERGE (reportedActivity)-[:DECLARES_TRANSACTION_PROVIDER_ACTIVITY]->(relatedActivity);