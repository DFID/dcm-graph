import pandas as pd
import json
import os
# sudo pip3 install -U python-dotenv
from dotenv import load_dotenv
from neo4j import GraphDatabase
load_dotenv()

os.chdir('data/')

def removeNewLines( data ):
    if data is not None and "\n" in data:
        data = data.replace("\n", " ")
        return data
    else:
        return data

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
    if tempOrgTitle is not None and "\n" in tempOrgTitle:
        print("Found a new line in", tempOrgIdentifier)
        tempOrgTitle = tempOrgTitle.replace("\n", " ")
    reporting_organisation_dict = {
        "organisationIdentifier:ID": removeNewLines(tempOrgIdentifier),
        "organisationTitle": removeNewLines(tempOrgTitle),
        ":LABEL": "Organisations"
    }
    organisation_list.append(reporting_organisation_dict.copy())

    # Populate the activity data in activity item store
    tempActivityTitle = activity['title_narrative'][0] if 'title_narrative' in activity.keys() else None
    tempActivityIdentifier = activity['iati_identifier'] if 'iati_identifier' in activity.keys() else None
    tempActivityReportingOrgTitle = activity['reporting_org_narrative'][0] if 'reporting_org_narrative' in activity.keys() else None
    tempActivityReportingOrgIdent = activity['reporting_org_ref'] if 'reporting_org_ref' in activity.keys() else None
    if tempActivityTitle is not None and "\n" in tempActivityTitle:
        print("Found a new line in", tempActivityIdentifier)
        tempActivityTitle = tempActivityTitle.replace("\n", " ")
    activity_dict = {
        "iatiIdentifier:ID": removeNewLines(tempActivityIdentifier),
        "title": removeNewLines(tempActivityTitle),
        "reportingOrgTitle": removeNewLines(tempActivityReportingOrgTitle),
        "reportingOrgIdentifier": removeNewLines(tempActivityReportingOrgIdent),
        ":LABEL": "Activities"
    }
    # Add the activity to the activity list
    activity_list.append(activity_dict.copy())

    # Create relations

    # Possible parent activity to child activity relation
    if 'related_activity_ref' in activity.keys():
        for index, related_activity in enumerate(activity['related_activity_ref'], start=0):
            if activity['related_activity_type'][index] == '2':
                activity_to_activity_relation_dict = {
                    ":START_ID": removeNewLines(activity['iati_identifier']),
                    ":END_ID": removeNewLines(related_activity),
                    ":TYPE": "PARENT_OF"
                }
                tempIdentifier = activity['iati_identifier'] if activity['iati_identifier'] in locals() else ""
                tempRelatedIatiIdentifier = related_activity if related_activity in locals() else ""
                parent_to_child_relation.append(
                    activity_to_activity_relation_dict)
            elif activity['related_activity_type'][index] == '1':
                activity_to_activity_relation_dict = {
                    "reportedIatiIdentifier": activity['iati_identifier'],
                    "relatedIatiIdentifier": related_activity
                }
                child_to_parent_relation.append(
                    activity_to_activity_relation_dict)

    # Populate the participating organisations
    if 'participating_org' in activity.keys() and 'reporting_org_ref' in activity.keys():
        for part in activity['participating_org']:
            part_json = json.loads(part)
            participating_org_of_dict = {
                "activityId": activity['iati_identifier'],
                "participatingOrgRef": part_json['ref'],
                "participatingOrgActivityId": part_json['activity_id'],
                "participatingOrgRole": part_json['role']['code']
            }
            p_dict = {
                ":START_ID": removeNewLines(activity['iati_identifier']),
                "role": removeNewLines(part_json['role']['code']),
                ":END_ID": removeNewLines(part_json['ref']),
                ":TYPE": "DECLARES_PARTICIPATING_ORG"
            }
            p_declares_parti_org.append(p_dict.copy())
            if part_json['activity_id'] != activity['iati_identifier']:
                p2_dict = {
                    ":START_ID": removeNewLines(activity['iati_identifier']),
                    "role": removeNewLines(part_json['role']['code']),
                    ":END_ID": removeNewLines(part_json['activity_id']),
                    ":TYPE": "DECLARES_PARTICIPATING_ACTIVITY"
                }
                p_declares_parti_activity.append(p2_dict.copy())
    print("Processing of activity: ", count, "completed.")
    count = count + 1

# Create dataframes based on each of the lists
print("Converting to data frame..")
organisation_list_df = pd.DataFrame(organisation_list)
activity_list_df = pd.DataFrame(activity_list)
parent_to_child_relation_df = pd.DataFrame(parent_to_child_relation)
child_to_parent_relation_df = pd.DataFrame(child_to_parent_relation)
participating_org_of_df = pd.DataFrame(participating_org_of)
p_declares_parti_activity_df = pd.DataFrame(p_declares_parti_activity)
p_declares_parti_org_df = pd.DataFrame(p_declares_parti_org)
print("Sorting and cleaning duplicates..")
# Sort and clear out all the duplicates
organisation_list_df.sort_values("organisationIdentifier:ID", inplace=True)
organisation_list_df.drop_duplicates(keep="first", inplace=True)

activity_list_df.sort_values("iatiIdentifier:ID", inplace=True)
activity_list_df.drop_duplicates(keep="first", inplace=True)

parent_to_child_relation_df.sort_values(":START_ID", inplace=True)
parent_to_child_relation_df.drop_duplicates(keep="first", inplace=True)

p_declares_parti_activity_df.sort_values(":START_ID", inplace=True)
p_declares_parti_activity_df.drop_duplicates(keep="first", inplace=True)

p_declares_parti_org_df.sort_values(":START_ID", inplace=True)
p_declares_parti_org_df.drop_duplicates(keep="first", inplace=True)
print("Building the relevant CSVs..")
# Publish data in csv
organisation_list_df.to_csv(
    r'0_organisation_list.csv', index=None, header=True)
activity_list_df.to_csv(r'0_activity_list.csv', index=None, header=True)
parent_to_child_relation_df.to_csv(
    r'0_parent_to_child_relation_list.csv', index=None, header=True)

p_declares_parti_activity_df.to_csv(
    r'0_declare_parti_activity.csv', index=None, header=True)

p_declares_parti_org_df.to_csv(
    r'0_declare_parti_org.csv', index=None, header=True)

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
    tempData = removeNewLines(transaction_downrefs['transaction_receiver_org_ref'][i])
    tempData2 = removeNewLines(transaction_downrefs['transaction_receiver_org_receiver_activity_id'][i])
    tro_dict = {
        ":START_ID": transaction_downrefs['iati_identifier'][i],
        ":END_ID": tempData,
        ":TYPE": "DECLARES_TRANSACTION_RECEIVER_ORG"
    }
    transaction_declares_receiver_org_arr.append(tro_dict)
    tra_dict = {
        ":START_ID": transaction_downrefs['iati_identifier'][i],
        ":END_ID": tempData2,
        ":TYPE": "DECLARES_TRANSACTION_RECEIVER_ACTIVITY"
    }
    transaction_declares_receiver_activity_arr.append(tra_dict)
print("Processing of transaction uprefs....")
for i in transaction_uprefs.index:
    tempData = removeNewLines(transaction_uprefs['transaction_provider_org_ref'][i])
    tempData2 = removeNewLines(transaction_uprefs['transaction_provider_org_provider_activity_id'][i])
    tpo_dict = {
        ":START_ID": removeNewLines(transaction_uprefs['iati_identifier'][i]),
        ":END_ID": tempData,
        ":TYPE": "DECLARES_TRANSACTION_PROVIDER_ORG"
    }
    transaction_declares_provider_org_arr.append(tpo_dict)
    tpa_dict = {
        ":START_ID": removeNewLines(transaction_uprefs['iati_identifier'][i]),
        ":END_ID": tempData2,
        ":TYPE": "DECLARES_TRANSACTION_PROVIDER_ACTIVITY"
    }
    transaction_declares_provider_activity_arr.append(tpa_dict)
transaction_declares_receiver_org_arr_df = pd.DataFrame(transaction_declares_receiver_org_arr)
transaction_declares_receiver_activity_arr_df = pd.DataFrame(transaction_declares_receiver_activity_arr)
transaction_declares_provider_org_arr_df = pd.DataFrame(transaction_declares_provider_org_arr)
transaction_declares_provider_activity_arr_df = pd.DataFrame(transaction_declares_provider_activity_arr)

transaction_declares_receiver_org_arr_df.sort_values(":START_ID", inplace=True)
transaction_declares_receiver_activity_arr_df.sort_values(":START_ID", inplace=True)
transaction_declares_provider_org_arr_df.sort_values(":START_ID", inplace=True)
transaction_declares_provider_activity_arr_df.sort_values(":START_ID", inplace=True)

transaction_declares_receiver_org_arr_df.to_csv(
    r'0_declared_receiver_org_list.csv', index=None, header=True)

transaction_declares_receiver_activity_arr_df.to_csv(
    r'0_declared_receiver_activity_list.csv', index=None, header=True)

transaction_declares_provider_org_arr_df.to_csv(
    r'0_declared_provider_org_list.csv', index=None, header=True)

transaction_declares_provider_activity_arr_df.to_csv(
    r'0_declared_provider_activity_list.csv', index=None, header=True)