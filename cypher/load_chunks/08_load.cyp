USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'http://rsdevbox.eastus.cloudapp.azure.com/0_activity_to_participating_org_relation_list.csv' AS row
MATCH (organisation:Organisations {OrgIdentifier: row.participatingOrgRef})
MATCH (activity:Activities {ActivityIdentifier: row.activityId})
MERGE (activity)-[:DECLARES_PARTICIPATING_ORG]->(organisation);