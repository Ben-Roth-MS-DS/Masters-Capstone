#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 17:02:35 2020

@author: Broth
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

def article_scraper(url):
    '''
    Function that scrapes the article title, author, and text from input url
    '''
    #try/except in case of error that may break code and cause restart
    try:
        #request url
        page = requests.get(url)

        #parse html
        soup = BeautifulSoup(page.content, 'html.parser')

        #get title text
        title_tag = soup.find_all('h1')
        titles = [title.text for title in title_tag]

        #get author name
        author_list = []
        author_tag = soup.find_all('span', attrs = {'class':'post-meta-author'})
        sep = ','
        for authors in author_tag:
            author_list = [name.text.split(sep, 1)[0] for name in authors.find_all('a')]

        if len(author_list) == 0:
            author_list.append(np.nan)

        #get article text
        text = soup.find_all('div', attrs = {'class': 'post-inner'})
        for more_text in text:
            article_text = more_text.find_all('p', attrs = {'class': None})
            articles = [paragraph.text for paragraph in article_text if paragraph.text != '']

        #combine article text into single string
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
        - scraper: Designates the scraper that the url corresponds to. Currently
                   choose from: 'azcapitoltimes', 'azcentral', 'azpbs', '12news',
                   and 'fox10'

    Outputs:
        - author_list: List of authors from each article
        - title_list: List of article titles from each article
        - text_list: List containing text of each article
    """
    #try/except in case of error that breaks code and causes restart
    try:
        #define outputs
        authors_list = []
        title_list = []
        text_list = []

        #iterate through each article, add title, author, text for each to respective list
        for url in url_list:
            if '.pdf' in url:
                continue
            else:
                title, author, text = article_scraper(url)
                authors_list.append(author)
                title_list.append(title)
                text_list.append(text)

        #combine list to datarfame
        df = pd.DataFrame(list(zip(authors_list, title_list, text_list, url_list)), \
                      columns = ['Title', 'Author', 'Text', 'URL'])

        #remove articles without meaningful text
        df = df[~df['Text'].str.contains('Enter your user name and password in the fields above to gain access to the subscriber content on this site.')]
        return(df)

    except:
        df = pd.DataFrame(columns = ['Title', 'Author', 'Text', 'URL'])
        return(df)


def url_getter(key_words, date_upper, date_lower, npages = 5):
    """
    Function that gets list of urls for relevant based on key words, and date range.

    Inputs:
        - key_words: Key words that the articles will relate to
        - date_upper: Date that you want articles to come before. Format = mm/dd/yyyy
        - date_lower: Date that you want articles to come after. Format = mm/dd/yyyy
        - npages: Number of pages to go search term for


    Output:
        - List of urls to get article text from
    """
    #try/except in case error breaks code
    try:
        #combine key words into single string to url
        search_terms = ' '.join(key_words)
        search_terms = search_terms.replace(' ', '+')

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

        #get list of article urls to scrape
        for npage in range(0, npages + 1):
            url = 'https://azcapitoltimes.com/?s=' + str(search_terms) + '&search_category=&date_start=' + \
                   ml + '%2F' + dl +'%2F' + yl + '&date_end=' + mu + '%2F' + du + '%2F' + yu + \
                   '&sort=rel&page=' + str(npage)

            #request url
            page = requests.get(url)

            #parse html
            soup = BeautifulSoup(page.content, 'html.parser')

            #get list of urls
            article_urls = soup.find_all('span', attrs = {'class':'doc_title'})

            #pull out actual url
            for article_url in article_urls:
                a = article_url.find('a', href = True)
                if a.text:
                    urls.append(a['href'])
                else:
                    continue

        return(urls)

    except:
        return([])
