#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 16:11:10 2020

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

#ignore warnings
pd.options.mode.chained_assignment = None 

warnings.simplefilter(action='ignore', category=FutureWarning)



def article_scraper(url):
    '''
    Function that scrapes the article title, author, and text from input url
    
    Input: 
        -url: Link to the website
     
    Output:
        -title, author, article text
    '''
    #try except clause to deal with html code
    try:
        if 'podcast' in url:
            return('N/a', 'N/a', 'N/a')
        
        elif 'amp' in url:
            return('N/a', 'N/a', 'N/a')
        
        elif '/picture-gallery/' in url:
            return('N/a', 'N/a', 'N/a')
     
        elif '/videos/' in url:
            return('N/a', 'N/a', 'N/a')
        
        elif '/interactives/' in url:
            return('N/a', 'N/a', 'N/a')
        
        elif '/restricted/' in url:
            return('N/a', 'N/a', 'N/a')
    
        else:
            page = requests.get(url)

            #parse html
            soup = BeautifulSoup(page.content, 'html.parser')
        
            #get title text, if/else for differnt html formatting
            title_tag = soup.find_all('h1', attrs = {'itemprop':'headline'})
            if len(title_tag) == 0:
                title_tag = soup.find_all('h1', attrs = {'class':"topper__headline"})
                
                if len(title_tag) == 0:
                    title_tag = soup.find_all('h1', attrs = {'elementtiming':'ar-headline'})
                    if len(title_tag) == 0 :
                        title_tag = soup.find_all('h1', attrs = {'class': 'display-2'})
                        titles = [title.text for title in title_tag]
                        if len(title_tag) == 0 :
                            title_tag = soup.find_all('h1', attrs = {'class': 'title'})
                            titles = [title.text for title in title_tag]
                        else:
                            titles = [title.text for title in title_tag]
                    else: 
                        titles = [title.text for title in title_tag]
                else:
                    titles = [title.text for title in title_tag]
            else:
                titles = [title.text for title in title_tag]
    
            #get author name, if/else for different html formatting
            author_list = []
            author_tag = soup.find('a', attrs = {'rel':'author'})
            if author_tag == None:
                author_tag = soup.find('span', attrs = {'class':'asset-metabar-author asset-metabar-item'})
                if author_tag == None:
                    author_tag = soup.find('span', attrs = {'class':'topper__byline'})
                
                    if author_tag == None:
                        author_tag = soup.find('div', attrs = {'class':'gnt_ar_by'})
                    
                        if author_tag == None:
                            author_tag = soup.find('div', attrs = {'class': 'gnt_ar_pb'})
                            if author_tag == None:
                                author_tag = soup.find('a', attrs = {'slot': 'bylineInfo'})
                                if author_tag == None:
                                    author_list = [np.nan]
                                else:
                                    author_list.append(author_tag.text.split(' | ')[0])
                            else:
                                author_list.append( author_tag.text.split(' | ')[0])
                        
                        else:
                            author_list.append(author_tag.text)
            
                    else:
                        author_list.append(author_tag.text)
                else:
                    author_list.append(author_tag.text)
        
            else:
                author_list.append(author_tag.text)
    
        
            #get article text, if/else for different formatting 
            text = soup.find_all('div', attrs = {'role': 'main'})
            if len(text) == 0:
                text = soup.find_all('section', attrs = {'class': 'in-depth-content'})
        
                if len(text) == 0:
                    text = soup.find_all('div', attrs = {'class': "longform-body clearfix"})
                
                    if len(text) == 0:
                        article_text = soup.find_all('p', attrs = {'class':"gnt_ar_b_p"})
                        if len(article_text) == 0:
                            text = soup.find_all('p')
                            articles = [more_text.text for more_text in text if more_text.text != '']
                        
                        
                        else:    
                            articles = [paragraph.text for paragraph in article_text if paragraph.text != '']

                    else:
                        for more_text in text:
                            article_text = more_text.find_all('p')
                            articles = [paragraph.text for paragraph in article_text if paragraph.text != '']
            
                else:
                    for more_text in text:
                        article_text = more_text.find_all('p')
                        articles = [paragraph.text for paragraph in article_text if paragraph.text != '']

            else: 
                for more_text in text:
                    article_text = more_text.find_all('p')
                    articles = [paragraph.text for paragraph in article_text if paragraph.text != '']
    
            articles = ' '.join(articles)
    
       
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

    #loop through list of urls
    for url in url_list:
        title, author, text = article_scraper(url)
        authors_list.append(author)
        title_list.append(title)
        text_list.append(text)
            
     #convert to df   
    df = pd.DataFrame(list(zip(authors_list, title_list, text_list, url_list)),\
                      columns = ['Author', 'Title', 'Text', 'URL'])
    
    #ignore urls that are useless
    df = df[~df.URL.str.contains('-podcast/')]
    df = df[~df.URL.str.contains('/videos/')]
    df = df[~df.URL.str.contains('amp')]
    df = df[~df.URL.str.contains('/picture_gallery/')]
    df = df[~df.URL.str.contains('/interactives/')]
    df = df[~df.URL.str.contains('/restricted/')]

    
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
    all_azcen = pd.DataFrame(columns = ['Author', 'Title', 'Text', 'URL', 'Bill', 'Year'])

    start_time = time.time()

    #iteratively find articles from az capital times
    for year in range(int(year_min), int(year_max) + 1):
        year_time = time.time()
    
        year = str(year)
        
        path = save_path + 'azcen_articletext_' + str(year) + '.csv'

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
            all_azcen_year_filt = all_azcen_year[all_azcen_year['Year'] == year]
            n = len(all_azcen_year_filt.Bill.unique())
            if n == 0:
                all_azcen_year = pd.DataFrame(columns = ['Author', 'Title', 'Text', 'URL', 'Bill', 'Year'])

        except NameError:
            all_azcen_year = pd.DataFrame(columns = ['Author', 'Title', 'Text', 'URL', 'Bill', 'Year'])
            n = 0
 
        if n == len(df.bill_id.unique()):
            continue
        
        elif os.path.isfile(path) == True:
            continue
           

        else:

            for i in range(n,len(df)):
                bill_time = time.time()
        
                #initiate final df for that bill
                all_azcen_bill = pd.DataFrame(columns = ['Author', 'Title', 'Text', 'URL'])
        
                key_words = df['title'][i]

                key_words = key_words.split(';')

                date_upper = df['date'][i]
                date_lower = df['date_lower'][i]
        


                #az capital times
                azcen_urls = gn.google_scraper(key_words = key_words,
                                           date_upper = date_upper,
                                           date_lower = date_lower,
                                           site = 'azcentral')



                azcen_df = article_scraper_compiler(url_list = azcen_urls)

                all_azcen_bill = pd.concat([all_azcen_bill, azcen_df])

                all_azcen_bill['Bill'] = df['bill_number'][i]
                all_azcen_bill['Year'] = year
        
                all_azcen_year = pd.concat([all_azcen_year, all_azcen_bill], sort = True)
            
                print('Time to scrape all articles for bill ' + str(i + 1) + '/' + str(len(df)) + ' in year ' + year + ' is: ' + str(round((time.time() - bill_time)/60, 2) )+ ' minutes')    
                
            all_azcen_year.to_csv(path)
            
            
            all_azcen = pd.concat([all_azcen, all_azcen_year], sort = True)
            print('Time to scrape all articles for all bills in year ' + year + ' is: ' + str(round((time.time() - year_time)/60/60, 2) )+ ' hours')    
    
    print('Time to scrape all articles for all bills for all years is: ' +  str(round((time.time() - start_time)/60/60, 2) )+ ' hours')

    all_azcen = all_azcen.drop_duplicates()
    all_azcen.to_csv(save_path + 'azcen_articletext_all.csv')
    return(all_azcen)

df = article_aggregate(year_min = 2015, 
                       year_max = 2020, 
                       save_path = '../../../Data/ArticleText/')