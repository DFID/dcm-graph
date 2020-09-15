# DCM Graph

This repository is created to store a research work for visualising delivery chain map based on [IATI store data](https://iati.cloud) and [neo4j graph database](https://neo4j.com).

## About DCM Graph
Our main goal for this project is to create a prototype Graph Database of International Aid Transparency Initiative (IATI) data in establishing a connection between DFID and a supplier of interest beyond immediate project funding. To do this, we have prepared a python script to import data from the [IATI store](https://iati.cloud) and prepare the necessary CSV files of Nodes and relationships for importing into a neo4j instance. 

## Get started

### Prerequisites and Assumptions

* An running instance of Neo4j at version 3.5. This has been tested on a trial instance of the enterprise edition, but may well work on the commercial edition too
* A separate server or development machine with fast and non-firewalled internet and a LOT of RAM available. The initial python script required 32GB of RAM to avoid killing the process in the most recent testing has been tested using an Azure Ubuntu Box with a download speed. However, if using a remote box you can use a beefy configuration for this step and then downsize the server for subsequent steps.
* A Neo4J instance with 16GB of RAM or higher (at least for the import - it could be downsized subsequently as long as queries are kept reasonable). 
* Python3 for processing and serving the CSVs for Neo4J to import.
* Tmux to run long downloads or processing requests on a remote box without a broken pipe halting the process.

### High-Level Process

> This assumes a fresh Ubuntu 18 box

1. SSH or use VS Code's Remote Extension to enter your desired environment, clone this repository, and cd into it.
2. Run `sudo sh setup.sh` to install requirements.
3. _Optional_ if ssh in a remote box: create a new tmux session and enter into it if you want to ensure that a download / transaction will continue if you're disconnected.
   * `tmux new -s operations`
   * within this window you can run some commands and create a [split screen dashboard](docs/tmux_demo.png)
   * 'detach' with `ctrl+B` followed by `d`
   * 'attach' later with `tmux attach -t operations`
4. Run `sh get_iati.sh`
   * Note that as of the 2nd of September 2019, the activity file is 1.88GB requiring 5 minutes to download at 6.9MB/s and the transaction file is 623MB, requiring 2:45 at the same speed. This is why running from an azure box is preferable, as it leverages Microsoft's punchy down-speed!
5. run `python3 Import-and-prepare-activity-organisation-data.py` (see 'IATI Data' below)
6. run `python3 Prepare-transaction-csv.py`
7. cd into data and run `sudo python3 -m http.server 80`. This will server a temporary http server from the data directory, allowing the Neo4J instance to access the files for import.
   * note that port 80 must be exposed for this to work!
8. Ensure your Neo4J instance is clean and has the expected login credentials and then run `populate_neo4j.sh` with the remote filenames specified in the *.cyp files that are iterated over.


## Detailed Components

### IATI Data Getter
We have imported two types of files which are used by the python scripts of this project - both very large. They are pulled from the [IATI store data](https://iati.cloud) using pre-defined queries that can be viewed in the shell scripted linked below.

The first is a JSON file containing all IATI Activities, the second a CSV file containing all transactions.

[get_iati.sh](get_iati.sh) is a script which runs a `wget` command for each, using pre-defined urls.

### Data Wrangling in Python

Two python scripts do the work of processing the data in to normalised CSVs that are ready for import into Neo4J:
* [Import-and-prepare-activity-organisation-data.py](Import-and-prepare-activity-organisation-data.py)
    * Requires a huge amount of RAM (32GB when last tested)
    * Executes relatively quickly if it doesn't crash.

* [Prepare-transaction-csv.py](Prepare-transaction-csv.py)
    * Operates much more quickly and requires less power.

### Interacting with Neo4J

Using [neo4j-client](https://neo4j-client.net/).

> Note! This only works with Neo4j 3.5 - not 4.x

Interactive query running can be done via terminal as follows: 

```sh
neo4j-client -u neo4j iatigraph.eastus.azurecontainer.io:7687
```

Inline queries can be run directly from sh commands like this:

```sh
neo4j-client -u neo4j -p <password> -o data/result.out -i cypher/load-oneshot.cyp bolt://iatigraph.eastus.azurecontainer.io:7687
```

If the file after the `-i` argument is a set of distinct, semi-colon separated cypher commands (as is the case in the file used), this command will iterate over each of them and eventually output a report to the `-o` file.

## Installing Neo4J Community to Remote Server

On a fresh Ubuntu 18 Server with 16GB RAM or higher, run the following:

```sh
# install java
sudo add-apt-repository ppa:webupd8team/java -y
sudo apt-get update -y
sudo apt-get install openjdk-8-jdk -y

# Get Neo4j packages - see https://debian.neo4j.com/
wget -O - https://debian.neo4j.com/neotechnology.gpg.key | sudo apt-key add -
echo 'deb https://debian.neo4j.com stable 3.5' | sudo tee /etc/apt/sources.list.d/neo4j.list
sudo apt-get update -y

# Install community edition
sudo apt-get install neo4j=1:3.5.21 -y

# go to /etc/neo4j and update conf file to allow remote connections...
# then run `sudo service neo4j restart`
# then run `service neo4j status and check it's running on 0.0.0.0`
```

To purge the database and start over (useful as deleting nodes is sometimes prohibitive)

```sh
cd /var/lib/neo4j/data/databases/
sudo rm -r -f graph.db
```
### NEO4J HTTPS Setup with OPENSSL Certificate

```sh
#############################################
##### NEO4J VERSION 3.5 AND ABOVE ###########
#############################################
#############################################
# Go inside folder /var/lib/neo4j/certificates and create a new folder called 'default'
# Go inside folder /var/lib/neo4j/certificates/default and create a new folder called 'revoked'
# Run the following command to generate the necesssary certificates inside folder 'default'. Please use the dns name that you had used inside your azure vm setup.
# $ openssl req -newkey rsa:2048 -nodes -keyout private.key -x509 -days 365 -out public.crt
# Make the following changes inside /etc/neo4j/neo4j.conf
dbms.ssl.policy.default.base_directory=certificates/default
dbms.ssl.policy.default.trust_all=true
dbms.ssl.policy.default.private_key=/var/lib/neo4j/certificates/default/private.key
dbms.ssl.policy.default.public_certificate=/var/lib/neo4j/certificates/default/public.crt

#############################################
##### NEO4J VERSION 4.0 AND ABOVE ###########
#############################################
# Follow below changes for version 4.0+
# run the following command to generate the necesssary certificates. Please use the dns name that you had used inside your azure vm setup.
# $ openssl req -newkey rsa:2048 -nodes -keyout private.key -x509 -days 365 -out public.crt
# Run the following commands to copy the generated certificates into the neo4j certificates folder
# $ sudo cp private.key /var/lib/neo4j/certificates/
# $ sudo cp public.crt /var/lib/neo4j/certificates/

dbms.connector.bolt.enabled=true
dbms.connector.bolt.tls_level=REQUIRED
dbms.connector.bolt.listen_address=:7687

# HTTP Connector. There can be zero or one HTTP connectors.
dbms.connector.http.enabled=true
dbms.connector.http.listen_address=:7474

# HTTPS Connector. There can be zero or one HTTPS connectors.
dbms.connector.https.enabled=true
dbms.connector.https.listen_address=:7473

# Bolt SSL configuration
dbms.ssl.policy.bolt.enabled=true
dbms.ssl.policy.bolt.base_directory=certificates
dbms.ssl.policy.bolt.private_key=/var/lib/neo4j/certificates/private.key
dbms.ssl.policy.bolt.public_certificate=/var/lib/neo4j/certificates/public.crt
dbms.ssl.policy.bolt.client_auth=NONE
dbms.ssl.policy.bolt.trust_all=true

# Https SSL configuration
dbms.ssl.policy.https.enabled=true
dbms.ssl.policy.https.base_directory=certificates
dbms.ssl.policy.https.private_key=/var/lib/neo4j/certificates/private.key
dbms.ssl.policy.https.public_certificate=/var/lib/neo4j/certificates/public.crt
dbms.ssl.policy.https.client_auth=NONE
dbms.ssl.policy.https.trust_all=true
```
