load csv with headers from 'file:///0_organisation_list.csv' AS row
CREATE (:Organisations {OrgIdentifier: row.organisationIdentifier, OrgName: row.organisationTitle});

USING PERIODIC COMMIT
load csv with headers from 'file:///0_activity_list.csv' AS row
CREATE (:Activities {ActivityIdentifier: row.iatiIdentifier, ActivityTitle: row.title});

create index on :Activities(ActivityIdentifier);

create index on :Organisations(OrgIdentifier);

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///0_org_to_activity_relation_list.csv' AS row
MATCH (organisation:Organisations {OrgIdentifier: row.reportingOrgIdentifier})
MATCH (activity:Activities {ActivityIdentifier: row.activityIatiIdentifier})
MERGE (organisation)-[:PUBLISHES]->(activity);

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///0_parent_to_child_relation_list.csv' AS row
MATCH (reportedActivity:Activities {ActivityIdentifier: row.reportedIatiIdentifier})
MATCH (relatedActivity:Activities {ActivityIdentifier: row.relatedIatiIdentifier})
MERGE (reportedActivity)-[:PARENT_OF]->(relatedActivity);

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///0_child_to_parent_relation_list.csv' AS row
MATCH (reportedActivity:Activities {ActivityIdentifier: row.reportedIatiIdentifier})
MATCH (relatedActivity:Activities {ActivityIdentifier: row.relatedIatiIdentifier})
MERGE (reportedActivity)-[:CHILD_OF]->(relatedActivity);

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///0_child_to_child_relation_list.csv' AS row
MATCH (reportedActivity:Activities {ActivityIdentifier: row.reportedIatiIdentifier})
MATCH (relatedActivity:Activities {ActivityIdentifier: row.relatedIatiIdentifier})
MERGE (reportedActivity)-[:SIBLING_OF]->(relatedActivity);

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///0_activity_to_participating_org_relation_list.csv' AS row
MATCH (organisation:Organisations {OrgIdentifier: row.participatingOrgRef})
MATCH (activity:Activities {ActivityIdentifier: row.activityId})
MERGE (activity)-[:DECLARES_PARTICIPATING_ORG]->(organisation);

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///0_transaction_downrefs_list.csv' AS row
MATCH (organisation:Organisations {OrgIdentifier: row.transaction_receiver_org_ref})
MATCH (activity:Activities {ActivityIdentifier: row.iati_identifier})
MERGE (activity)-[:DECLARES_TRANSACTION_RECEIVER_ORG]->(organisation);

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///0_transaction_downrefs_list.csv' AS row
MATCH (reportedActivity:Activities {ActivityIdentifier: row.iati_identifier})
MATCH (relatedActivity:Activities {ActivityIdentifier: row.transaction_receiver_org_receiver_activity_id})
MERGE (reportedActivity)-[:DECLARES_TRANSACTION_RECEIVER_ACTIVITY]->(relatedActivity);

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///0_transaction_uprefs_list.csv' AS row
MATCH (organisation:Organisations {OrgIdentifier: row.transaction_provider_org_ref})
MATCH (activity:Activities {ActivityIdentifier: row.iati_identifier})
MERGE (activity)-[:DECLARES_TRANSACTION_PROVIDER_ORG]->(organisation);

USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'file:///0_transaction_uprefs_list.csv' AS row
MATCH (reportedActivity:Activities {ActivityIdentifier: row.iati_identifier})
MATCH (relatedActivity:Activities {ActivityIdentifier: row.transaction_provider_org_provider_activity_id})
MERGE (reportedActivity)-[:DECLARES_TRANSACTION_PROVIDER_ACTIVITY]->(relatedActivity);