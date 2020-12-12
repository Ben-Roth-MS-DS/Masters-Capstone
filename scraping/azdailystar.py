#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 16:38:06 2020

@author: Broth
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import googlenews as gn
import time
import warnings
import os

def article_scraper(url):
    '''
    Function that scrapes the article title, author, and text from input url
    
    Input: 
        -url: Link to the website
     
    Output:
        -title, author, article text
    '''
    try:
    
        page = requests.get(url)

        #parse html
        soup = BeautifulSoup(page.content, 'html.parser')
        
        #get title text
        title_tag = soup.find('h1', attrs = {'class':'headline'})
        title_text = title_tag.find_all('span')
        titles = [title.text.strip() for title in title_text]
    
        #get author name
        author_list = []
        author_tag = soup.find('span', attrs = {'itemprop':'author'})
        author_list.append(author_tag.text.strip())
    
        author_list = [author.replace('By ', '') for author in author_list]
        author_list = [author.split("\n",2)[0] for author in author_list]
        
    
    
        #get article text 
        text = soup.find_all('p', attrs = None)
    
        articles = [paragraph.text for paragraph in text if paragraph.text != '']
    
        articles = ' '.join(articles)
    
        drop = "To continue viewing content on tucson.com, please sign in with your existing account or subscribe. We have not been able to find your subscription. Current Subscriber? Log in Current Subscriber? Activate now Or Don't have a subscription? Subscribe now Subscribe today for unlimited access Subscribe today for unlimited access"

        articles = articles.replace('\n', '').replace('\t', '').replace(drop, '')
    
        return(titles[0], author_list[0], articles)

    except:
        return('N/A', 'N/A', 'N/A')
        
        
def article_scraper_compiler(url_list):
    """
    Function that outputs lists of authors, titles, and article texts for multiple 
    article scrapers
    
    Inputs:
        - url_list: List of urls to scrape.
       
                   
    Outputs:
        - author_list: List of authors from each article
        - title_list: List of article titles from each article
        - text_list: List containing text of each article
    """
    #define outputs
    
    authors_list = []
    title_list = []
    text_list = []

    for url in url_list:
        title, author, text = article_scraper(url)
        authors_list.append(author)
        title_list.append(title)
        text_list.append(text)
            
    df = pd.DataFrame(list(zip(authors_list, title_list, text_list, url_list)),\
                      columns = ['Author', 'Title', 'Text', 'URL'])
    
        
    return(df)
    
    
    
def article_aggregate(year_min, year_max, save_path):
    '''
    Function that finds every article for each bill in the given years based on 
    each bill's key words
    
    Inputs
    - year_min: Starting year
    - year_max: Ending year
    - save_path: where yearly aggregates will be saved
    
    Outputs
    - Combined df of every bill
    '''
    #ignore warnings
    pd.options.mode.chained_assignment = None 
    warnings.simplefilter(action='ignore', category=FutureWarning)
    
    
    #create empty final df
    all_azds = pd.DataFrame(columns = ['Author', 'Title', 'Text', 'URL', 'Bill', 'Year'])

    start_time = time.time()

    #iteratively find articles from az capital times
    for year in range(int(year_min), int(year_max) + 1):
        year_time = time.time()
    
        year = str(year)
        
        path = save_path + 'azds_articletext_' + str(year) + '.csv'

        bills = pd.read_csv('../../../Data/Legiscan/' + year + '/csv/bills.csv')
        hist = pd.read_csv('../../../Data/Legiscan/' + year + '/csv/history.csv')

        #keep date of introduction for each bill
        hist_intro = hist.drop_duplicates('bill_id', keep = 'first')

        #only keep columns of interest
        hist_intro = hist_intro[['bill_id', 'date']]
    
        #change format of date column
        hist_intro['date'] = pd.to_datetime(hist_intro['date'])
        hist_intro['date'] = hist_intro['date'].dt.strftime('%m/%d/%Y')
    
        #calculate date 6 months prior, convert to proper format
        hist_intro['date_lower'] = pd.to_datetime(hist_intro['date']) - pd.DateOffset(months = 6)
        hist_intro['date_lower'] = hist_intro['date_lower'].dt.strftime('%m/%d/%Y')


        df = pd.merge(hist_intro, bills, on = 'bill_id')
    
        #initiate final df for that year
        try:
            all_azds_year_filt = all_azds_year[all_azds_year['Year'] == year]
            n = len(all_azds_year_filt.Bill.unique())
            if n == 0:
                all_azds_year = pd.DataFrame(columns = ['Author', 'Title', 'Text', 'URL', 'Bill', 'Year'])

        except NameError:
            all_azds_year = pd.DataFrame(columns = ['Author', 'Title', 'Text', 'URL', 'Bill', 'Year'])
            n = 0
 
        if n == len(df.bill_id.unique()):
            continue
        
        elif os.path.isfile(path) == True:
            continue
           

        else:

            for i in range(n,len(df)):
                bill_time = time.time()
        
                #initiate final df for that bill
                all_azds_bill = pd.DataFrame(columns = ['Author', 'Title', 'Text', 'URL'])
        
                key_words = df['title'][i]

                key_words = key_words.split(';')

                date_upper = df['date'][i]
                date_lower = df['date_lower'][i]
        


                #az capital times
                azds_urls = gn.google_scraper(key_words = key_words,
                                           date_upper = date_upper,
                                           date_lower = date_lower,
                                           site = 'tucson.com')



                azds_df = article_scraper_compiler(url_list = azds_urls)

                all_azds_bill = pd.concat([all_azds_bill, azds_df])

                all_azds_bill['Bill'] = df['bill_number'][i]
                all_azds_bill['Year'] = year
        
                all_azds_year = pd.concat([all_azds_year, all_azds_bill], sort = True)
            
                print('Time to scrape all articles for bill ' + str(i + 1) + '/' + str(len(df)) + ' in year ' + year + ' is: ' + str(round((time.time() - bill_time)/60, 2) )+ ' minutes')    
                
            all_azds_year.to_csv(path)
            
            
            all_azds = pd.concat([all_azds, all_azds_year], sort = True)
            print('Time to scrape all articles for all bills in year ' + year + 'is: ' + str(round((time.time() - year_time)/60/60, 2) )+ ' hours')    
    
    print('Time to scrape all articles for all bills for all years is: ' +  str(round((time.time() - start_time)/60/60, 2) )+ ' hours')

    all_azds = all_azds.drop_duplicates()
    all_azds.to_csv(save_path + 'azds_articletext_all.csv')
    return(all_azds)

df = article_aggregate(year_min = 2015, 
                       year_max = 2020, 
                       save_path = '../../../Data/ArticleText/')