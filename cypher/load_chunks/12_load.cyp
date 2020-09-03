USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'http://rsdevbox.eastus.cloudapp.azure.com/0_transaction_uprefs_list.csv' AS row
MATCH (organisation:Organisations {OrgIdentifier: row.transaction_provider_org_ref})
MATCH (activity:Activities {ActivityIdentifier: row.iati_identifier})
MERGE (activity)-[:DECLARES_TRANSACTION_PROVIDER_ORG]->(organisation);