USING PERIODIC COMMIT
LOAD CSV WITH HEADERS FROM 'http://rsdevbox.eastus.cloudapp.azure.com/0_child_to_child_relation_list.csv' AS row
MATCH (reportedActivity:Activities {ActivityIdentifier: row.reportedIatiIdentifier})
MATCH (relatedActivity:Activities {ActivityIdentifier: row.relatedIatiIdentifier})
MERGE (reportedActivity)-[:SIBLING_OF]->(relatedActivity);