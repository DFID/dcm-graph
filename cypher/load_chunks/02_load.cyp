USING PERIODIC COMMIT
load csv with headers from 'http://rsdevbox.eastus.cloudapp.azure.com/0_activity_list.csv' AS row
CREATE (:Activities {ActivityIdentifier: row.iatiIdentifier, ActivityTitle: row.title});