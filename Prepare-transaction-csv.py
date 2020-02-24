import csv
import pandas as pd



transactions = pd.read_csv('transactions.csv')
transaction_uprefs = transactions.pivot_table(
    index=['iati_identifier','transaction_provider_org_ref','transaction_provider_org_provider_activity_id'], 
    columns=['transaction_type'], 
    values='transaction_value', 
    aggfunc='sum').reset_index()
transaction_downrefs = transactions.pivot_table(
    index=['iati_identifier','transaction_receiver_org_ref','transaction_receiver_org_receiver_activity_id'], 
    columns=['transaction_type'], 
    values='transaction_value', 
    aggfunc='sum').reset_index()

transaction_uprefs.sort_values("iati_identifier")
transaction_uprefs.drop_duplicates(keep="first", inplace=True)

transaction_downrefs.sort_values("iati_identifier")
transaction_downrefs.drop_duplicates(keep="first", inplace=True)

transaction_uprefs.to_csv(r'0_transaction_uprefs_list.csv', index=None, header=True)
transaction_downrefs.to_csv(r'0_transaction_downrefs_list.csv', index=None, header=True)
