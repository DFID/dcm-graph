# DCM Graph

This repository is created to store a research work for visualising delivery chain map based on [IATI store data](https://iati.cloud) and [neo4j graph database](https://neo4j.com).

## About DCM Graph
Our main goal for this project is to create a prototype Graph Database of International Aid Transparency Initiative (IATI) data in establishing a connection between DFID and a supplier of interest beyond immediate project funding. To do this, we have prepared a python script to import data from the [IATI store](https://iati.cloud) and prepare the necessary CSV files of Nodes and relationships for importing into a neo4j instance. 

## Get started

### Prerequisites and Assumptions

* An running instance of Neo4j at version 3.5. This has been tested on a trial instance of the enterprise edition, but may well work on the commercial edition too
* A separate server or development machine with fast and non-firewalled internet and a LOT of RAM available. This required 32GB of RAM to avoid killing the process in the most recent testing has been tested using an Azure Ubuntu Box with a download speed.
* Python3 for processing and serving the CSVs for Neo4J to import.
* Tmux to run long downloads or processing requests on a remote box without a broken pipe halting the process.

### High-Level Process

> This assumes a fresh Ubuntu 18 box

1. SSH or use VS Code's Remote Extension to enter your desired environment, clone this repository, and cd into it.
2. Run `sudo sh setup.sh` to install requirements.
3. Optional if ssh in a remote box: create a new tmux session and enter into it if you want to ensure that a download will continue if you're disconnected.
4. Run `sh get_iati.sh`
   * Note that as of the 2nd of September 2019, the activity file is 1.88GB requiring 5 minutes to download at 6.9MB/s and the transaction file is 623MB, requiring 2:45 at the same speed. This is why running from an azure box is preferable, as it leverages Microsoft's punchy down-speed!
5. run `python3 Import-and-prepare-activity-organisation-data.py` (see 'IATI Data' below)
6. run `python3 Prepare-transaction-csv.py`
7. cd into data and run `sudo python3 -m http.server 80`. This will server a temporary http server from the data directory, allowing the Neo4J instance to access the files for import.
8. **TODO** Run Neo4J import processes (still to be finalised) with your chosen instance.


## IATI Data
We have imported two types of files which are used by the python scripts of this project - both very large.

The first is a JSON file containing all IATI Activities, the second a CSV file containing all transactions.

[get_iati.sh](get_iati.sh) is a script which runs a `wget` command for each, using pre-defined urls.

### Interacting with Neo4J

> Note! This only works with Neo4j 3.5 - not 4.x

Interactive query running can be done via terminal as follows: 

```sh
neo4j-client -u neo4j iatigraph.eastus.azurecontainer.io:7687
```

Inline queries can be run directly from sh commands like this:

```sh
neo4j-client -u neo4j -p <password> -o result.out -i <filepath>.cyp bolt://iatigraph.eastus.azurecontainer.io:7687
```

**TODO**: iterate over [CQL-query-oneshot.cql](CQL-query-oneshot.cql), or chunk into separate files in the [/cypher](/cyper) folder to automate population.