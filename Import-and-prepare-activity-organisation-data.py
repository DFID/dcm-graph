import pandas as pd
import json
import os

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
    reporting_organisation_dict = {
        "organisationTitle": activity['reporting_org_narrative'][0] if 'reporting_org_narrative' in activity.keys() else None,
        "organisationIdentifier": activity['reporting_org_ref'] if 'reporting_org_ref' in activity.keys() else None
    }
    # Add the reporting_org data to the main organisations array
    organisation_list.append(reporting_organisation_dict.copy())

    # Populate the activity data in activity item store
    activity_dict = {
        "title": activity['title_narrative'][0] if 'title_narrative' in activity.keys() else None,
        "iatiIdentifier": activity['iati_identifier'] if 'iati_identifier' in activity.keys() else None
    }
    # Add the activity to the activity list
    activity_list.append(activity_dict.copy())

    # Create relations
    # Published by relations
    hierarchy = activity['hierarchy'] if 'hierarchy' in activity.keys(
    ) else None
    activity_published_by_dict = {
        "reportingOrgIdentifier": activity['reporting_org_ref'] if 'reporting_org_ref' in activity.keys() else None,
        "activityIatiIdentifier": activity['iati_identifier'] if 'iati_identifier' in activity.keys() else None,
        "activityHierarchy": hierarchy
    }
    # push the data to it's relevant list
    activity_published_by.append(activity_published_by_dict)

    # Possible parent activity to child activity relation
    if 'related_activity_ref' in activity.keys():
        for index, related_activity in enumerate(activity['related_activity_ref'], start=0):
            if activity['related_activity_type'][index] == '2':
                activity_to_activity_relation_dict = {
                    "reportedIatiIdentifier": activity['iati_identifier'],
                    "relatedIatiIdentifier": related_activity
                    # "relationship": activity['related_activity_type'][index]
                }
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
            elif activity['related_activity_type'][index] == '3':
                activity_to_activity_relation_dict = {
                    "reportedIatiIdentifier": activity['iati_identifier'],
                    "relatedIatiIdentifier": related_activity
                    # "relationship": activity['related_activity_type'][index]
                }
                child_to_child_relation.append(
                    activity_to_activity_relation_dict)

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
            participating_org_of.append(participating_org_of_dict.copy())
    print("Processing of activity: ", count, "completed.")
    count = count + 1

# Create dataframes based on each of the lists
print("Converting to data frame..")
organisation_list_df = pd.DataFrame(organisation_list)
activity_list_df = pd.DataFrame(activity_list)
activity_published_by_df = pd.DataFrame(activity_published_by)
# activity_to_activity_relation_df = pd.DataFrame(activity_to_activity_relation)
parent_to_child_relation_df = pd.DataFrame(parent_to_child_relation)
child_to_parent_relation_df = pd.DataFrame(child_to_parent_relation)
child_to_child_relation_df = pd.DataFrame(child_to_child_relation)
participating_org_of_df = pd.DataFrame(participating_org_of)

print("Sorting and cleaning duplicates..")
# Sort and clear out all the duplicates
organisation_list_df.sort_values("organisationIdentifier", inplace=True)
organisation_list_df.drop_duplicates(keep="first", inplace=True)

activity_list_df.sort_values("iatiIdentifier", inplace=True)
activity_list_df.drop_duplicates(keep="first", inplace=True)

activity_published_by_df.sort_values("activityIatiIdentifier", inplace=True)
activity_published_by_df.drop_duplicates(keep="first", inplace=True)

parent_to_child_relation_df.sort_values("reportedIatiIdentifier", inplace=True)
parent_to_child_relation_df.drop_duplicates(keep="first", inplace=True)
child_to_parent_relation_df.sort_values("reportedIatiIdentifier", inplace=True)
child_to_parent_relation_df.drop_duplicates(keep="first", inplace=True)
child_to_child_relation_df.sort_values("reportedIatiIdentifier", inplace=True)
child_to_child_relation_df.drop_duplicates(keep="first", inplace=True)

participating_org_of_df.sort_values("participatingOrgRef", inplace=True)
participating_org_of_df.drop_duplicates(keep="first", inplace=True)

print("Building the relevant CSVs..")
# Publish data in csv
organisation_list_df.to_csv(
    r'0_organisation_list.csv', index=None, header=True)
activity_list_df.to_csv(r'0_activity_list.csv', index=None, header=True)
activity_published_by_df.to_csv(
    r'0_org_to_activity_relation_list.csv', index=None, header=True)
parent_to_child_relation_df.to_csv(
    r'0_parent_to_child_relation_list.csv', index=None, header=True)
child_to_parent_relation_df.to_csv(
    r'0_child_to_parent_relation_list.csv', index=None, header=True)
child_to_child_relation_df.to_csv(
    r'0_child_to_child_relation_list.csv', index=None, header=True)
participating_org_of_df.to_csv(
    r'0_activity_to_participating_org_relation_list.csv', index=None, header=True)
