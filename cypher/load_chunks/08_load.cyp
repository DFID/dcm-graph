USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'http://rsdevbox.eastus.cloudapp.azure.com/0_activity_to_participating_org_relation_list.csv' AS row
// merge participating organisation
MATCH (organisation:Organisations {OrgIdentifier: row.participatingOrgRef})
MATCH (activity:Activities {ActivityIdentifier: row.activityId})
MERGE (activity)-[:DECLARES_PARTICIPATING_ORG {role:row.participatingOrgRole}]->(organisation)

// merge participating activity
WITH row
MATCH (activity:Activities {ActivityIdentifier: row.activityId})
MATCH (participating_activity:Activities {ActivityIdentifier: row.participatingOrgActivityId})
WHERE NOT row.participatingOrgActivityId = row.activityId
MERGE (activity)-[:DECLARES_PARTICIPATING_ACTIVITY {role:row.participatingOrgRole}]->(participating_activity);