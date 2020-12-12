#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 12 13:16:10 2020

@author: Broth
"""

import requests
from bs4 import BeautifulSoup


def google_scraper(key_words, date_upper, date_lower, site, check = None):
    """
    Function that gets list of urls for relevant based on key words, and date range.
    
    Inputs:
        - key_words: Key words that the articles will relate to
        - date_upper: Date that you want articles to come before. Format = mm/dd/yyyy
        - date_lower: Date that you want articles to come after. Format = mm/dd/yyyy
        - site: News site to find stories from
        - check: string to make sure urls are from proper site 
                 (e.g. check = 'cronkite' if want to check cronkite news where results
                 show cronkite)
        
    Output:
        - List of urls to get article text from
    """  
    try:
        key_words = [word for word in key_words if '&' not in word]
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
    
        url = "https://news.google.com/search?q=" + search_terms + " %20source%3A" + \
            site + "%20before%3A" + yu + "-" + mu + "-" + du + "%20after%3A" + yl + \
            "-" + ml + "-" + dl + "&hl=en-US&gl=US&ceid=US%3Aen"
    
    #request url
        page = requests.get(url)
    
    #parse html
        soup = BeautifulSoup(page.content, 'html.parser')

    #find article tags
        article_urls = soup.find_all('article')

    #retrieve initial urls that link through google news
        article_titles = []
        for article_text in article_urls:
            article_title = article_text.find('a')
            article_titles.append(article_title['href'])

    
        #initiate actual urls list
        urls = []
    
    #get actual site urls
        for google_url in article_titles:
            try:
                #get link and combine with google news url
                bad_url = google_url[1:]
                combined_url = 'https://news.google.com' + bad_url
        
                #request site, then get actual url from requests
                actual_page = requests.get(combined_url)
        
                #return actual url
                actual_url = actual_page.url
        
            #add actual url to list
                urls.append(actual_url)
            except:
                continue
    
        #only get urls from site of interest
        if check == None:
            urls = [url for url in urls if site in url]
        else:
            urls = [url for url in urls if check in url]
    
        if len(urls) == 0:
            search_terms = ' '.join(key_words)
            search_terms = search_terms.replace('  ', ' ')
            search_terms = search_terms.replace(' ', '%20OR%20')
        
            url = "https://news.google.com/search?q=" + search_terms + " %20source%3A" + \
            site + "%20before%3A" + yu + "-" + mu + "-" + du + "%20after%3A" + yl + \
            "-" + ml + "-" + dl + "&hl=en-US&gl=US&ceid=US%3Aen"
    
            #request url
            page = requests.get(url)
    
            #parse html
            soup = BeautifulSoup(page.content, 'html.parser')

            #find article tags
            article_urls = soup.find_all('article')

            #retrieve initial urls that link through google news
            article_titles = []
            for article_text in article_urls:
                article_title = article_text.find('a')
                article_titles.append(article_title['href'])

    
            #initiate actual urls list
            urls = []
    
            #get actual site urls
            for google_url in article_titles:
                try:
                    #get link and combine with google news url
                    bad_url = google_url[1:]
                    combined_url = 'https://news.google.com' + bad_url
            
                    #request site, then get actual url from requests
                    actual_page = requests.get(combined_url)
        
                    #return actual url
                    actual_url = actual_page.url
                
                    #add actual url to list
                    urls.append(actual_url)
                except:
                    continue
    
        #only get urls from site of interest
            if check == None:
                urls = [url for url in urls if site in url]
            else:
                urls = [url for url in urls if check in url]
            
            return(urls)
    
        else:
            return(urls)
            
    except:
        return([])




