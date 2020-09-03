# 2020-09-03

## Results of overnight CLI Run

The following command was run: `neo4j-client -u neo4j -p <password> -o data/result.out -i cypher/load-oneshot.cyp bolt://iatigraph.eastus.azurecontainer.io:7687`

As of 1400 the following day, the output from the `sudo python3 -m http.server 80` command is as follows:

```
40.114.42.61 - - [02/Sep/2020 20:45:39] "GET /0_organisation_list.csv HTTP/1.1" 200 -                                     
40.114.42.61 - - [02/Sep/2020 20:45:40] "GET /0_activity_list.csv HTTP/1.1" 200 -
40.114.42.61 - - [02/Sep/2020 20:46:22] "GET /0_org_to_activity_relation_list.csv HTTP/1.1" 200 -  
```

And there are now just above 80k 'publishes' relationships in the neo4j box used. File being processed above has around 10 times that:

```sh
azureuser@devbox:~/dcm-graph$ wc -l < data/0_org_to_activity_relation_list.csv 
824852
```

Conclusion: this is a **slow** process.

Possible explanations:

1. The use of a remote CSV file makes the process slower.
    * I don't think this is likely - it's not like streaming the data would take this long (the file is only 32MB)
2. The use of the command-line library (`neo4j-client`) is much slower
    * Unclear, but would likely have shown up in the many support pages I've googled.
3. The batch command itself (having a set of Cypher statements in one file) is slower
    * Very possible
4. The way we're building our relations is much slower
    * Possible, though doesn't appear to have taken this long before
    * Regardless though, I think we should be making less normalised and fewer tables when we load entities and then matching them on their attributes (type `:play northwind-graph` into an interactive Neo4J instance to see this paradigm in action)

**Next Steps**

* Try separate command runs (iterating over different 1-statement cypher files)
* Try running _from the neo4j box_ having downloaded the CSV files locally to that machine
* Try creating all of the nodes with their various fields first, and then create relations on in-graph match conditions such as this:
    ```cypher
    MATCH (p:Product),(c:Category)
    WHERE p.categoryID = c.categoryID
    CREATE (p)-[:PART_OF]->(c)
    ```
    * This may well require a different setup than the current 'live container instance' deployment used on Azure, but it does seem possible to wget through a browser terminal in the Azure Portal. 
# 2020-09-02

* Clarified process using http.server to surface files for separate Neo4J
* Lots of work done to make the data-munging server easy to deploy and documented
* Clear-up of directory structure
* Set CLI Neo4J import process running over-night