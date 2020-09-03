USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'http://rsdevbox.eastus.cloudapp.azure.com/0_transaction_downrefs_list.csv' AS row
MATCH (organisation:Organisations {OrgIdentifier: row.transaction_receiver_org_ref})
MATCH (activity:Activities {ActivityIdentifier: row.iati_identifier})
MERGE (activity)-[:DECLARES_TRANSACTION_RECEIVER_ORG]->(organisation);