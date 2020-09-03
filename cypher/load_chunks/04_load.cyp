USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'http://rsdevbox.eastus.cloudapp.azure.com/0_org_to_activity_relation_list.csv' AS row
MATCH (organisation:Organisations {OrgIdentifier: row.reportingOrgIdentifier})
MATCH (activity:Activities {ActivityIdentifier: row.activityIatiIdentifier})
MERGE (organisation)-[:PUBLISHES]->(activity);