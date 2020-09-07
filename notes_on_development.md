# 2020-09-07

Cracked the import. Moved away from a pre-built container instance, and just installed Neo4J community (3.5.2) on a bare Ubuntu 18 box. Turns out the most reasonable way to stop `08_load.cyp` from crashing the server is to just beef up the RAM. Now the data import at least should take place on a machine with 16GB or more.

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
    * Start by running `wget -r -np -R "index.html*" http://rsdevbox.eastus.cloudapp.azure.com/` in the `/import` folder, then moving the files in the downloaded directory up to the `/import` directory.
    * Run the separate chunks in [load-oneshot-local.cyp](load-oneshot-local.cyp) via the browser
    * Result: this is much, much quicker. The following command created all the publishing relationships in just over a minute (instead of one tenth of it being complete after more than 12 hours):
    ```cyp
    :auto USING PERIODIC COMMIT
    LOAD CSV WITH HEADERS FROM 'file:///0_org_to_activity_relation_list.csv' AS row
    MATCH (organisation:Organisations {OrgIdentifier: row.reportingOrgIdentifier})
    MATCH (activity:Activities {ActivityIdentifier: row.activityIatiIdentifier})
    MERGE (organisation)-[:PUBLISHES]->(activity)
    ```
* Attempting this with a remote file for diagnostics... remote file is just as fast. **No need for the wget strategy.**
* Attempting this with single chunks via terminal... works almost as fast (extra few seconds). **No need to use the console, can be scripted**


### Chunking Files

* Chunked files into [cypher/load_chunks](cypher/load_chunks) to be iterated over.
* Discovered that you need to wait after each transaction is completed for around 10 seconds to avoid confusing the Neo4J instance and causing a halt / dramatic slowdown
* The 8th chunk causes an out-of-memory error in the container instance used.
* **TODO** Deploy a bigger instance of Neo4J, or refactor the load to require less RAM.

## General Design Consideration

It would be good to try creating all of the nodes with their various fields first, and then create relations on in-graph match conditions such as this:

```cypher
MATCH (p:Product),(c:Category)
WHERE p.categoryID = c.categoryID
CREATE (p)-[:PART_OF]->(c)
```

# 2020-09-02

* Clarified process using http.server to surface files for separate Neo4J
* Lots of work done to make the data-munging server easy to deploy and documented
* Clear-up of directory structure
* Set CLI Neo4J import process running over-night