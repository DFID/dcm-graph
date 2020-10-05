import pandas as pd
import json
import os
# sudo pip3 install -U python-dotenv
from dotenv import load_dotenv
from neo4j import GraphDatabase
load_dotenv()
# Prepare the bolt driver                               
# uri = os.getenv("boltURL")
# driver = GraphDatabase.driver(uri, auth=(os.getenv("neo4jUser"), os.getenv("neo4jPass")))

# Prepare methods for importing data into neo4j db
# def create_orgs(tx, identifier, title):
#     tx.run("CREATE (:Organisations {OrgIdentifier: $identifier, OrgName: $title})", identifier=identifier, title=title)

# def create_activities(tx, iatiIdentifier, title, reportingOrgTitle, reportingOrgIdentifier):
#     tx.run("CREATE (:Activities {ActivityIdentifier: $iatiIdentifier, ActivityTitle: $title, ReportingOrgTitle: $reportingOrgTitle, ReportingOrgIdentifier: $reportingOrgIdentifier})", iatiIdentifier=iatiIdentifier, title=title,  reportingOrgTitle=reportingOrgTitle, reportingOrgIdentifier=reportingOrgIdentifier)

# def create_parent_to_child_relation(tx, reportedIdentifier, relatedIdentifier):
#     tx.run("MATCH (reportedActivity:Activities {ActivityIdentifier: $reportedIdentifier}) MATCH (relatedActivity:Activities {ActivityIdentifier: $relatedIdentifier}) MERGE (reportedActivity)-[:PARENT_OF]->(relatedActivity)", reportedIdentifier=reportedIdentifier, relatedIdentifier=relatedIdentifier)

# def create_parti_org_relations(tx, participatingOrgRef, activityId, participatingOrgRole, participatingOrgActivityId):
#     tx.run("MATCH (organisation:Organisations {OrgIdentifier: $participatingOrgRef}) MATCH (activity:Activities {ActivityIdentifier: $activityId}) MERGE (activity)-[:DECLARES_PARTICIPATING_ORG {role:$participatingOrgRole}]->(organisation)", participatingOrgRef=participatingOrgRef, activityId=activityId, participatingOrgRole=participatingOrgRole)
#     tx.run("MATCH (activity:Activities {ActivityIdentifier: $activityId}) MATCH (participating_activity:Activities {ActivityIdentifier: $participatingOrgActivityId}) WHERE NOT $participatingOrgActivityId = $activityId MERGE (activity)-[:DECLARES_PARTICIPATING_ACTIVITY {role:$participatingOrgRole}]->(participating_activity)", activityId=activityId, participatingOrgActivityId=participatingOrgActivityId, participatingOrgRole=participatingOrgRole)

# def create_index(tx):
#     tx.run("create index on :Activities(ActivityIdentifier)")
#     tx.run("create index on :Organisations(OrgIdentifier)")

#os.chdir('data/')

print("Processing started..")
activities_from_json = {}

with open('all-activities.json') as json_file:
    activities_from_json = json.load(json_file)

# Main item stores
organisation_list = []
activity_list = []

# Item relations
activity_published_by = []
activity_to_activity_relation = []
parent_to_child_relation = []
child_to_parent_relation = []
child_to_child_relation = []
participating_org_of = []
p_declares_parti_org = []
p_declares_parti_activity = []
print("Starting parse of each activity..")
count = 0
for activity in activities_from_json['response']['docs']:
    print("Processing activity: ", count)
    # Populate the main item stores
    tempOrgTitle = activity['reporting_org_narrative'][0] if 'reporting_org_narrative' in activity.keys() else None
    tempOrgIdentifier = activity['reporting_org_ref'] if 'reporting_org_ref' in activity.keys() else None
    reporting_organisation_dict = {
        "organisationIdentifier:ID": tempOrgIdentifier,
        "organisationTitle": tempOrgTitle,
        ":LABEL": "Organisations"
    }
    # Run bolt query to push data to the neo4j db
    # with driver.session() as session:
    #     session.write_transaction(create_orgs, tempOrgIdentifier, tempOrgTitle)
    # Add the reporting_org data to the main organisations array
    organisation_list.append(reporting_organisation_dict.copy())

    # Populate the activity data in activity item store
    tempActivityTitle = activity['title_narrative'][0] if 'title_narrative' in activity.keys() else None
    tempActivityIdentifier = activity['iati_identifier'] if 'iati_identifier' in activity.keys() else None
    tempActivityReportingOrgTitle = activity['reporting_org_narrative'][0] if 'reporting_org_narrative' in activity.keys() else None
    tempActivityReportingOrgIdent = activity['reporting_org_ref'] if 'reporting_org_ref' in activity.keys() else None
    activity_dict = {
        "iatiIdentifier:ID": tempActivityIdentifier,
        "title": tempActivityTitle,
        "reportingOrgTitle": tempActivityReportingOrgTitle,
        "reportingOrgIdentifier": tempActivityReportingOrgIdent,
        ":LABEL": "Activities"
    }
    # Run bolt query to push data to the neo4j db
    # with driver.session() as session:
    #     session.write_transaction(create_activities, tempActivityIdentifier, tempActivityTitle, tempActivityReportingOrgTitle, tempActivityReportingOrgIdent)
    # Add the activity to the activity list
    activity_list.append(activity_dict.copy())

    # Create relations
    # Published by relations
    ##hierarchy = activity['hierarchy'] if 'hierarchy' in activity.keys(
    ##) else None
    """ activity_published_by_dict = {
        "reportingOrgIdentifier": activity['reporting_org_ref'] if 'reporting_org_ref' in activity.keys() else None,
        "activityIatiIdentifier": activity['iati_identifier'] if 'iati_identifier' in activity.keys() else None,
        "activityHierarchy": hierarchy
    } """
    # push the data to it's relevant list
    ##activity_published_by.append(activity_published_by_dict)

    # Possible parent activity to child activity relation
    if 'related_activity_ref' in activity.keys():
        for index, related_activity in enumerate(activity['related_activity_ref'], start=0):
            if activity['related_activity_type'][index] == '2':
                activity_to_activity_relation_dict = {
                    ":START_ID": activity['iati_identifier'],
                    ":END_ID": related_activity,
                    ":TYPE": "PARENT_OF"
                    # "relationship": activity['related_activity_type'][index]
                }
                tempIdentifier = activity['iati_identifier'] if activity['iati_identifier'] in locals() else ""
                tempRelatedIatiIdentifier = related_activity if related_activity in locals() else ""
                # Run bolt query to push data to the neo4j db
                # with driver.session() as session:
                #     session.write_transaction(create_parent_to_child_relation, tempIdentifier, tempRelatedIatiIdentifier)
                parent_to_child_relation.append(
                    activity_to_activity_relation_dict)
            elif activity['related_activity_type'][index] == '1':
                activity_to_activity_relation_dict = {
                    "reportedIatiIdentifier": activity['iati_identifier'],
                    "relatedIatiIdentifier": related_activity
                    # "relationship": activity['related_activity_type'][index]
                }
                child_to_parent_relation.append(
                    activity_to_activity_relation_dict)
            """ elif activity['related_activity_type'][index] == '3':
                activity_to_activity_relation_dict = {
                    "reportedIatiIdentifier": activity['iati_identifier'],
                    "relatedIatiIdentifier": related_activity
                    # "relationship": activity['related_activity_type'][index]
                }
                child_to_child_relation.append(
                    activity_to_activity_relation_dict) """

    # Populate the participating organisations
    if 'participating_org' in activity.keys() and 'reporting_org_ref' in activity.keys():
        for part in activity['participating_org']:
            part_json = json.loads(part)
            participating_org_of_dict = {
                "activityId": activity['iati_identifier'],
                # "reportingOrgRef": activity['reporting_org_ref'],
                "participatingOrgRef": part_json['ref'],
                # "participatingOrgText": part_json['narratives'][0]['text'] if part_json['narratives'] else None,
                "participatingOrgActivityId": part_json['activity_id'],
                "participatingOrgRole": part_json['role']['code']
            }
            p_dict = {
                ":START_ID": activity['iati_identifier'],
                "role": part_json['role']['code'],
                ":END_ID": part_json['ref'],
                ":TYPE": "DECLARES_PARTICIPATING_ORG"
            }
            p_declares_parti_org.append(p_dict.copy())
            if part_json['activity_id'] != activity['iati_identifier']:
                p2_dict = {
                    ":START_ID": activity['iati_identifier'],
                    "role": part_json['role']['code'],
                    ":END_ID": part_json['activity_id'],
                    ":TYPE": "DECLARES_PARTICIPATING_ACTIVITY"
                }
                p_declares_parti_activity.append(p2_dict.copy())
            # with driver.session() as session:
            #         session.write_transaction(create_parti_org_relations, part_json['ref'], activity['iati_identifier'], part_json['role']['code'], part_json['activity_id'])
            #participating_org_of.append(participating_org_of_dict.copy())
    print("Processing of activity: ", count, "completed.")
    count = count + 1

# Create dataframes based on each of the lists
print("Converting to data frame..")
organisation_list_df = pd.DataFrame(organisation_list)
activity_list_df = pd.DataFrame(activity_list)
##activity_published_by_df = pd.DataFrame(activity_published_by)
# activity_to_activity_relation_df = pd.DataFrame(activity_to_activity_relation)
parent_to_child_relation_df = pd.DataFrame(parent_to_child_relation)
child_to_parent_relation_df = pd.DataFrame(child_to_parent_relation)
##child_to_child_relation_df = pd.DataFrame(child_to_child_relation)
participating_org_of_df = pd.DataFrame(participating_org_of)
p_declares_parti_activity_df = pd.DataFrame(p_declares_parti_activity)
p_declares_parti_org_df = pd.DataFrame(p_declares_parti_org)
print("Sorting and cleaning duplicates..")
# Sort and clear out all the duplicates
organisation_list_df.sort_values("organisationIdentifier:ID", inplace=True)
organisation_list_df.drop_duplicates(keep="first", inplace=True)

activity_list_df.sort_values("iatiIdentifier:ID", inplace=True)
activity_list_df.drop_duplicates(keep="first", inplace=True)

##activity_published_by_df.sort_values("activityIatiIdentifier", inplace=True)
##activity_published_by_df.drop_duplicates(keep="first", inplace=True)

parent_to_child_relation_df.sort_values(":START_ID", inplace=True)
parent_to_child_relation_df.drop_duplicates(keep="first", inplace=True)
# child_to_parent_relation_df.sort_values("reportedIatiIdentifier", inplace=True)
# child_to_parent_relation_df.drop_duplicates(keep="first", inplace=True)
##child_to_child_relation_df.sort_values("reportedIatiIdentifier", inplace=True)
##child_to_child_relation_df.drop_duplicates(keep="first", inplace=True)

# participating_org_of_df.sort_values("participatingOrgRef", inplace=True)
# participating_org_of_df.drop_duplicates(keep="first", inplace=True)

p_declares_parti_activity_df.sort_values(":START_ID", inplace=True)
p_declares_parti_activity_df.drop_duplicates(keep="first", inplace=True)

p_declares_parti_org_df.sort_values(":START_ID", inplace=True)
p_declares_parti_org_df.drop_duplicates(keep="first", inplace=True)
print("Building the relevant CSVs..")
# Publish data in csv
organisation_list_df.to_csv(
    r'0_organisation_list.csv', index=None, header=True)
activity_list_df.to_csv(r'0_activity_list.csv', index=None, header=True)
##activity_published_by_df.to_csv(
##    r'0_org_to_activity_relation_list.csv', index=None, header=True)
parent_to_child_relation_df.to_csv(
    r'0_parent_to_child_relation_list.csv', index=None, header=True)
# child_to_parent_relation_df.to_csv(
#     r'0_child_to_parent_relation_list.csv', index=None, header=True)
##child_to_child_relation_df.to_csv(
##    r'0_child_to_child_relation_list.csv', index=None, header=True)
# participating_org_of_df.to_csv(
#     r'0_activity_to_participating_org_relation_list.csv', index=None, header=True)

p_declares_parti_activity_df.to_csv(
    r'0_declare_parti_activity.csv', index=None, header=True)

p_declares_parti_org_df.to_csv(
    r'0_declare_parti_org.csv', index=None, header=True)

# Load transaction data into the neo4j db
# Create necessary functions

# def process_downref_transactions(tx, transaction_receiver_org_ref, iati_identifier, transaction_receiver_org_receiver_activity_id):
#     tx.run("MATCH (organisation:Organisations {OrgIdentifier: $transaction_receiver_org_ref}) MATCH (activity:Activities {ActivityIdentifier: $iati_identifier}) MERGE (activity)-[:DECLARES_TRANSACTION_RECEIVER_ORG]->(organisation)", transaction_receiver_org_ref=transaction_receiver_org_ref, iati_identifier=iati_identifier)
#     tx.run("MATCH (reportedActivity:Activities {ActivityIdentifier: $iati_identifier}) MATCH (relatedActivity:Activities {ActivityIdentifier: $transaction_receiver_org_receiver_activity_id}) MERGE (reportedActivity)-[:DECLARES_TRANSACTION_RECEIVER_ACTIVITY]->(relatedActivity)", iati_identifier=iati_identifier, transaction_receiver_org_receiver_activity_id=transaction_receiver_org_receiver_activity_id)

# def process_upref_transactions(tx, transaction_provider_org_ref, iati_identifier, transaction_provider_org_provider_activity_id):
#     tx.run("MATCH (organisation:Organisations {OrgIdentifier: $transaction_provider_org_ref}) MATCH (activity:Activities {ActivityIdentifier: $iati_identifier}) MERGE (activity)-[:DECLARES_TRANSACTION_PROVIDER_ORG]->(organisation)", transaction_provider_org_ref=transaction_provider_org_ref, iati_identifier=iati_identifier)
#     tx.run("MATCH (reportedActivity:Activities {ActivityIdentifier: $iati_identifier}) MATCH (relatedActivity:Activities {ActivityIdentifier: $transaction_provider_org_provider_activity_id}) MERGE (reportedActivity)-[:DECLARES_TRANSACTION_PROVIDER_ACTIVITY]->(relatedActivity)", iati_identifier=iati_identifier, transaction_provider_org_provider_activity_id=transaction_provider_org_provider_activity_id)

transactions = pd.read_csv('transactions.csv')
transaction_uprefs = transactions.pivot_table(
    index=['iati_identifier', 'transaction_provider_org_ref',
           'transaction_provider_org_provider_activity_id'],
    columns=['transaction_type'],
    values='transaction_value',
    aggfunc='sum').reset_index()
transaction_downrefs = transactions.pivot_table(
    index=['iati_identifier', 'transaction_receiver_org_ref',
           'transaction_receiver_org_receiver_activity_id'],
    columns=['transaction_type'],
    values='transaction_value',
    aggfunc='sum').reset_index()

transaction_uprefs.sort_values("iati_identifier")
transaction_uprefs.drop_duplicates(keep="first", inplace=True)

transaction_downrefs.sort_values("iati_identifier")
transaction_downrefs.drop_duplicates(keep="first", inplace=True)

transaction_uprefs.to_csv(
    r'0_transaction_uprefs_list.csv', index=None, header=True)
transaction_downrefs.to_csv(
    r'0_transaction_downrefs_list.csv', index=None, header=True)
transaction_declares_receiver_org_arr = []
transaction_declares_receiver_activity_arr = []
transaction_declares_provider_org_arr = []
transaction_declares_provider_activity_arr = []
print("Processing of transaction downrefs..")
for i in transaction_downrefs.index:
    tro_dict = {
        ":START_ID": transaction_downrefs['iati_identifier'][i],
        #"role": part_json['role']['code'],
        ":END_ID": transaction_downrefs['transaction_receiver_org_ref'][i],
        ":TYPE": "DECLARES_TRANSACTION_RECEIVER_ORG"
    }
    transaction_declares_receiver_org_arr.append(tro_dict.copy())
    tra_dict = {
        ":START_ID": transaction_downrefs['iati_identifier'][i],
        #"role": part_json['role']['code'],
        ":END_ID": transaction_downrefs['transaction_receiver_org_receiver_activity_id'][i],
        ":TYPE": "DECLARES_TRANSACTION_RECEIVER_ACTIVITY"
    }
    transaction_declares_receiver_activity_arr.append(tra_dict.copy())
print("Processing of transaction uprefs....")
for i in transaction_uprefs.index:
    tpo_dict = {
        ":START_ID": transaction_uprefs['iati_identifier'][i],
        #"role": part_json['role']['code'],
        ":END_ID": transaction_uprefs['transaction_provider_org_ref'][i],
        ":TYPE": "DECLARES_TRANSACTION_PROVIDER_ORG"
    }
    transaction_declares_provider_org_arr.append(tpo_dict.copy())
    tpa_dict = {
        ":START_ID": transaction_uprefs['iati_identifier'][i],
        #"role": part_json['role']['code'],
        ":END_ID": transaction_uprefs['transaction_provider_org_provider_activity_id'][i],
        ":TYPE": "DECLARES_TRANSACTION_PROVIDER_ACTIVITY"
    }
    transaction_declares_provider_activity_arr.append(tpa_dict.copy())

transaction_declares_receiver_org_arr.sort_values(":START_ID", inplace=True)
transaction_declares_receiver_activity_arr.sort_values(":START_ID", inplace=True)
transaction_declares_provider_org_arr.sort_values(":START_ID", inplace=True)
transaction_declares_provider_activity_arr.sort_values(":START_ID", inplace=True)

transaction_declares_receiver_org_arr.to_csv(
    r'0_declared_receiver_org_list.csv', index=None, header=True)

transaction_declares_receiver_activity_arr.to_csv(
    r'0_declared_receiver_activity_list.csv', index=None, header=True)

transaction_declares_provider_org_arr.to_csv(
    r'0_declared_provider_org_list.csv', index=None, header=True)

transaction_declares_provider_activity_arr.to_csv(
    r'0_declared_provider_activity_list.csv', index=None, header=True)