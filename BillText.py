#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 13:16:55 2020

@author: Broth
"""

import pandas as pd
import os
import time
import requests
import urllib3
from bs4 import BeautifulSoup


#turn off warning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#get directories for each year of bills
directories = [x[0] for x in os.walk('../Data/Legiscan/') if x[0][-3:] != 'csv' and '20' in x[0]]


directories = [directories[0]]
#save text two ways; one each bill is its own text file, two compile every bill into a single csv

#create list for each variable
years = []
bill_numbers = []
bill_texts = []

#time how long it takes for entire loop and for each session
total_time = time.time()

#loop through each year
for session in directories:
    session_start = time.time()
    #get year of bill
    year = session[-4:]
    #read in necessary files
    documents = pd.read_csv(session + '/csv/documents.csv')
    bills = pd.read_csv(session + '/csv/bills.csv')

    #merge dfs together to get bill number
    bills_select = bills[['bill_id', 'bill_number', 'last_action_date']]
    merged = pd.merge(bills_select, documents, on = 'bill_id').sort_values('last_action_date').drop_duplicates('bill_id',keep='last').reset_index()

    #create directory to save bill text by year if none exists
    directory = '../Data/BillText/' + year + '/'
    if not os.path.exists(directory):
        os.makedirs(directory)

    #iterate through each bill, save a txt file
    for i in range(len(merged)):
        time.sleep(5)
        print(i)
        if os.path.isfile(directory + merged['bill_number'][i] + '.txt'):
            continue
        else:
            #save url
            url = merged['url'][i]

            #request url
            page = requests.get(url, verify=False)

            #parse html
            soup = BeautifulSoup(page.content, 'html.parser')

            #get bill text
            text = soup.find_all('div', attrs = {'class': 'WordSection2'})
            if len(text) != 0:
                for whole_bill in text:
                    main_bill = whole_bill.find_all('p')
                    bill_text = [paragraph.text for paragraph in main_bill if paragraph.text != '']
            else:
                text = soup.find_all('div', attrs = {'class': 'Section2'})
                for whole_bill in text:
                   main_bill = whole_bill.find_all('p')
                   bill_text = [paragraph.text for paragraph in main_bill if paragraph.text != '']
            #create single string
            bill_text = ' '.join(bill_text)

            #write txt file
            file = open(directory + merged['bill_number'][i] + '.txt', "w")
            file.write(bill_text)
            file.close()

            #append values to lists to be added to dataframe
            years.append(year)
            bill_numbers.append(merged['bill_number'][i])
            bill_texts.append(bill_text)
    #let know time
    print(session + ' done scraping')
    print('Time for ' + session + ' session to run: ' + str(round((time.time() - session_start)/60, 2) )+ ' minutes')


print('Time for total code to run: ' + str(round((time.time() - total_time)/60, 2) )+ ' minutes')

#create final dataframe
final_df = pd.DataFrame(list(zip(years, bill_numbers, bill_texts)), \
                      columns = ['Year', 'Bill_Number', 'Bill_Text'])

current_df = pd.read_csv('../Data/BillText/AZ_Bill_Text_2015-2020.csv')

current_df.drop(['Unnamed: 0'], axis = 1, inplace = True)

final_df = pd.concat([final_df, current_df], axis = 1)

final_df.to_csv('../Data/BillText/AZ_Bill_Text_2014-2020.csv')
