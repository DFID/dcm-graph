// Create simple 'Funds' relationship.

match (a1:Activities)-[:DECLARES_TRANSACTION_RECEIVER_ACTIVITY]->(a2:Activities)
where not a1=a2
merge (a1)-[:Funds {type:"simple"}]->(a2);

match (b1:Activities)<-[:DECLARES_TRANSACTION_PROVIDER_ACTIVITY]-(b2:Activities)
where not b1=b2
merge (b1)-[:Funds {type:"simple"}]->(b2)