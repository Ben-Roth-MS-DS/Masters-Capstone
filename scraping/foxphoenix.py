#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 19:19:55 2020

@author: Broth
"""


import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
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
        
        if page.status_code == 404:
            return('N/A', 'N/A', 'N/A')

        #parse html
        soup = BeautifulSoup(page.content, 'html.parser')
        
        #get title text
        title_tag = soup.find_all('h1', attrs = {'headline'})
        titles = [title.text for title in title_tag]
    
        #get author name
        author_list = []
        author_tag = soup.find_all('div', attrs = {'class':'article-body'})
        sep = ','
        for authors in author_tag:
            author_list = [name.text.split(sep, 1)[0] for name in authors.find_all('a')]
    
    
        #get article text 
        text = soup.find_all('div', attrs = {'class': 'article-body'})
        for more_text in text:
            article_text = more_text.find_all('p', attrs = {'class': None})
            articles = [paragraph.text for paragraph in article_text if paragraph.text != '']
            
        if len(articles) == 0:
            article_text = soup.find_all('p')
            articles = [paragraph.text for paragraph in article_text if paragraph.text != '']
  

        articles = ' '.join(articles)
    
        if len(author_list) == 0:
            if '(AP)' in articles:
                author_list.append('Associated Press')
                
            elif '(FOX NEWS)' in articles:
                author_list.append('FOX News')
                
            else:
                author_list.append('FOX News')
        return(titles[0], author_list[0], articles)
            
    except:
        return('N/A', 'N/A', 'N/A')
        print(url)
    
    
    
def article_scraper_compiler(url_list):
    """
    Function that outputs lists of authors, titles, and article texts for multiple 
    article scrapers
    
    Inputs:
        - url_list: List of urls to scrape.
        - scraper: Designates the scraper that the url corresponds to. Currently
                   choose from: 'azcapitoltimes', 'azcentral', 'azpbs', '12news',
                   and 'fox10'
                   
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
        if '/video/' in url:
            continue
        
        else:
            title, author, text = article_scraper(url)
            authors_list.append(author)
            title_list.append(title)
            text_list.append(text)
            
    df = pd.DataFrame(list(zip(authors_list, title_list, text_list, url_list)),\
                      columns = ['Author', 'Title', 'Text', 'URL'])
    
    df = df[~df.URL.str.contains('/video/')]
    
    df = df[df['Text'].map(len) > 0 ]
    
    
    return(df)
        
    
def url_getter(key_words, date_upper, date_lower, pages = 5):
    """
    Function that gets list of urls for relevant based on key words, and date range.
    
    Inputs:
        - key_words: Key words that the articles will relate to
        - date_upper: Date that you want articles to come before. Format = mm/dd/yyyy
        - date_lower: Date that you want articles to come after. Format = mm/dd/yyyy
        - pages: Number of pages to go search term for
        
    Output:
        - List of urls to get article text from
    """    
    try:
       search_terms = ' '.join(key_words)
       search_terms = search_terms.replace(' ', '%20')

      #month of upper date
       mu = date_upper[:2]
        #day of upper
       du = date_upper[3:5]
      #year of upper
       yu = date_upper[6:]
    
      #month of lower date
       ml = date_lower[:2]
      #day of lower
       dl = date_lower[3:5]
      #year of lower
       yl = date_lower[6:]
    
       urls = []
       for pagen in range(0, pages + 1):
           url = 'https://www.fox10phoenix.com/search?q=' + search_terms + \
                '&sort=relevance&page='+ str(pagen) + '&from=' + yl + '-' + ml + '-' + dl + \
                '&to=' + yu + '-' + mu + '-' + du

        #request url
           page = requests.get(url)
    
        #parse html
           soup = BeautifulSoup(page.content, 'html.parser')

        #find article tags
           article_urls = soup.find_all('h3', attrs = {'class':'title'})

           for article_url in article_urls:
               a = article_url.find('a', href = True)
               if a.text:
                   urls.append(a['href'])
               else:
                   continue
        
       urls = ['https://www.fox10phoenix.com' + url for url in urls]

       return(urls)
    except:
        return([])

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
    all_fox10 = pd.DataFrame(columns = ['Author', 'Title', 'Text', 'URL', 'Bill', 'Year'])

    start_time = time.time()

    #iteratively find articles from az capital times
    for year in range(int(year_min), int(year_max) + 1):
        year_time = time.time()
    
        year = str(year)
        
        path = save_path + 'fox10_articletext_' + str(year) + '.csv'

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
            all_fox10_year_filt = all_fox10_year[all_fox10_year['Year'] == year]
            n = len(all_fox10_year_filt.Bill.unique())
            if n == 0:
                all_fox10_year = pd.DataFrame(columns = ['Author', 'Title', 'Text', 'URL', 'Bill', 'Year'])

        except NameError:
            all_fox10_year = pd.DataFrame(columns = ['Author', 'Title', 'Text', 'URL', 'Bill', 'Year'])
            n = 0
 
        if n == len(df.bill_id.unique()):
            continue
        
        elif os.path.isfile(path) == True:
            continue
           

        else:

            for i in range(n,len(df)):
                bill_time = time.time()
        
                #initiate final df for that bill
                all_fox10_bill = pd.DataFrame(columns = ['Author', 'Title', 'Text', 'URL'])
        
                key_words = df['title'][i]

                key_words = key_words.split(';')

                date_upper = df['date'][i]
                date_lower = df['date_lower'][i]
        


                #az capital times
                fox10_urls = url_getter(key_words = key_words,
                                        date_upper = date_upper,
                                        date_lower = date_lower)



                fox10_df = article_scraper_compiler(url_list = fox10_urls)

                all_fox10_bill = pd.concat([all_fox10_bill, fox10_df])

                all_fox10_bill['Bill'] = df['bill_number'][i]
                all_fox10_bill['Year'] = year
        
                all_fox10_year = pd.concat([all_fox10_year, all_fox10_bill], sort = True)
            
                print('Time to scrape all articles for bill ' + str(i + 1) + '/' + str(len(df)) + ' in year ' + year + ' is: ' + str(round((time.time() - bill_time)/60, 2) )+ ' minutes')    
                
            all_fox10_year.to_csv(path)
            
            
            all_fox10 = pd.concat([all_fox10, all_fox10_year], sort = True)
            print('Time to scrape all articles for all bills in year ' + year + 'is: ' + str(round((time.time() - year_time)/60/60, 2) )+ ' hours')    
    
    print('Time to scrape all articles for all bills for all years is: ' +  str(round((time.time() - start_time)/60/60, 2) )+ ' hours')

    all_fox10 = all_fox10.drop_duplicates()
    all_fox10.to_csv(save_path + 'fox10_articletext_all.csv')
    return(all_fox10)
    
df = article_aggregate(year_min = 2015, 
                       year_max = 2020, 
                       save_path = '../../../Data/ArticleText/')
