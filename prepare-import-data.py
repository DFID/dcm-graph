import pandas as pd
import json
import os
# sudo pip3 install -U python-dotenv
from dotenv import load_dotenv
from neo4j import GraphDatabase
load_dotenv()
# Prepare the bolt driver
uri = os.getenv("boltURL")
driver = GraphDatabase.driver(uri, auth=(os.getenv("neo4jUser"), os.getenv("neo4jPass")))

# Prepare methods for importing data into neo4j db
def create_orgs(tx, identifier, title):
    tx.run("CREATE (:Organisations {OrgIdentifier: $identifier, OrgName: $title})", identifier=identifier, title=title)

def create_activities(tx, iatiIdentifier, title, reportingOrgTitle, reportingOrgIdentifier):
    tx.run("CREATE (:Activities {ActivityIdentifier: $iatiIdentifier, ActivityTitle: $title, ReportingOrgTitle: $reportingOrgTitle, ReportingOrgIdentifier: $reportingOrgIdentifier})", iatiIdentifier=iatiIdentifier, title=title,  reportingOrgTitle=reportingOrgTitle, reportingOrgIdentifier=reportingOrgIdentifier)

def create_parent_to_child_relation(tx, reportedIdentifier, relatedIdentifier):
    tx.run("MATCH (reportedActivity:Activities {ActivityIdentifier: $reportedIatiIdentifier}) MATCH (relatedActivity:Activities {ActivityIdentifier: $relatedIatiIdentifier}) MERGE (reportedActivity)-[:PARENT_OF]->(relatedActivity)", reportedIdentifier=reportedIdentifier, relatedIdentifier=relatedIdentifier)

def create_parti_org_relations(tx, participatingOrgRef, activityId, participatingOrgRole, participatingOrgActivityId):
    tx.run("MATCH (organisation:Organisations {OrgIdentifier: $participatingOrgRef}) MATCH (activity:Activities {ActivityIdentifier: $activityId}) MERGE (activity)-[:DECLARES_PARTICIPATING_ORG {role:$participatingOrgRole}]->(organisation)", participatingOrgRef=participatingOrgRef, activityId=activityId, participatingOrgRole=participatingOrgRole)
    tx.run("MATCH (activity:Activities {ActivityIdentifier: $activityId}) MATCH (participating_activity:Activities {ActivityIdentifier: $participatingOrgActivityId}) WHERE NOT $participatingOrgActivityId = $activityId MERGE (activity)-[:DECLARES_PARTICIPATING_ACTIVITY {role:$participatingOrgRole}]->(participating_activity)", activityId=activityId, participatingOrgActivityId=participatingOrgActivityId, participatingOrgRole=participatingOrgRole)

def create_index(tx):
    tx.run("create index on :Activities(ActivityIdentifier)")
    tx.run("create index on :Organisations(OrgIdentifier)")

os.chdir('data/')

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
print("Starting parse of each activity..")
count = 0
for activity in activities_from_json['response']['docs']:
    print("Processing activity: ", count)
    # Populate the main item stores
    tempOrgTitle = activity['reporting_org_narrative'][0] if 'reporting_org_narrative' in activity.keys() else None
    tempOrgIdentifier = activity['reporting_org_ref'] if 'reporting_org_ref' in activity.keys() else None
    reporting_organisation_dict = {
        "organisationTitle": tempOrgTitle,
        "organisationIdentifier": tempOrgIdentifier
    }
    # Run bolt query to push data to the neo4j db
    with driver.session() as session:
    session.write_transaction(create_orgs, tempOrgIdentifier, tempOrgTitle)
    # Add the reporting_org data to the main organisations array
    organisation_list.append(reporting_organisation_dict.copy())

    # Populate the activity data in activity item store
    tempActivityTitle = activity['title_narrative'][0] if 'title_narrative' in activity.keys() else None
    tempActivityIdentifier = activity['iati_identifier'] if 'iati_identifier' in activity.keys() else None
    tempActivityReportingOrgTitle = activity['reporting_org_narrative'][0] if 'reporting_org_narrative' in activity.keys() else None
    tempActivityReportingOrgIdent = activity['reporting_org_ref'] if 'reporting_org_ref' in activity.keys() else None
    activity_dict = {
        "title": tempActivityTitle,
        "iatiIdentifier": tempActivityIdentifier,
        "reportingOrgTitle": tempActivityReportingOrgTitle,
        "reportingOrgIdentifier": tempActivityReportingOrgIdent
    }
    # Run bolt query to push data to the neo4j db
    with driver.session() as session:
    session.write_transaction(create_activities, tempActivityIdentifier, tempActivityTitle, tempActivityReportingOrgTitle, tempActivityReportingOrgIdent)
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
                    "reportedIatiIdentifier": activity['iati_identifier'],
                    "relatedIatiIdentifier": related_activity
                    # "relationship": activity['related_activity_type'][index]
                }
                # Run bolt query to push data to the neo4j db
                with driver.session() as session:
                    session.write_transaction(create_parent_to_child_relation, activity['iati_identifier'], related_activity)
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
            with driver.session() as session:
                    session.write_transaction(create_parti_org_relations, part_json['ref'], activity['iati_identifier'], part_json['role']['code'], part_json['activity_id'])
            participating_org_of.append(participating_org_of_dict.copy())
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

print("Sorting and cleaning duplicates..")
# Sort and clear out all the duplicates
organisation_list_df.sort_values("organisationIdentifier", inplace=True)
organisation_list_df.drop_duplicates(keep="first", inplace=True)

activity_list_df.sort_values("iatiIdentifier", inplace=True)
activity_list_df.drop_duplicates(keep="first", inplace=True)

##activity_published_by_df.sort_values("activityIatiIdentifier", inplace=True)
##activity_published_by_df.drop_duplicates(keep="first", inplace=True)

parent_to_child_relation_df.sort_values("reportedIatiIdentifier", inplace=True)
parent_to_child_relation_df.drop_duplicates(keep="first", inplace=True)
child_to_parent_relation_df.sort_values("reportedIatiIdentifier", inplace=True)
child_to_parent_relation_df.drop_duplicates(keep="first", inplace=True)
##child_to_child_relation_df.sort_values("reportedIatiIdentifier", inplace=True)
##child_to_child_relation_df.drop_duplicates(keep="first", inplace=True)

participating_org_of_df.sort_values("participatingOrgRef", inplace=True)
participating_org_of_df.drop_duplicates(keep="first", inplace=True)

print("Building the relevant CSVs..")
# Publish data in csv
organisation_list_df.to_csv(
    r'0_organisation_list.csv', index=None, header=True)
activity_list_df.to_csv(r'0_activity_list.csv', index=None, header=True)
##activity_published_by_df.to_csv(
##    r'0_org_to_activity_relation_list.csv', index=None, header=True)
parent_to_child_relation_df.to_csv(
    r'0_parent_to_child_relation_list.csv', index=None, header=True)
child_to_parent_relation_df.to_csv(
    r'0_child_to_parent_relation_list.csv', index=None, header=True)
##child_to_child_relation_df.to_csv(
##    r'0_child_to_child_relation_list.csv', index=None, header=True)
participating_org_of_df.to_csv(
    r'0_activity_to_participating_org_relation_list.csv', index=None, header=True)
