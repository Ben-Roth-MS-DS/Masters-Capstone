#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 19:13:18 2020

@author: Broth
"""
import numpy as np
import pandas as pd
import spacy
import string

import nltk
from nltk.corpus import stopwords

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation as LDA
from sklearn.model_selection import GridSearchCV

#initiate spacy
nlp = spacy.load('en')

nltk.download('stopwords')

## read in bill data ##

#array of years
years = np.arange(2015, 2020, 1)

#initialize empty dataframe
df = pd.DataFrame(columns = ['bill_number', 'year', 'title'])

# create complete df of bill titles
for year in years:
    #read in year bills df
    bill_df = pd.read_csv('../Data/Legiscan/' + str(year) + '/csv/bills.csv')
   
    #create year column as another key
    bill_df['year'] = str(year)
    
    #select columns of interest
    bill_df_select = bill_df[['bill_number', 'year', 'title']]
    
    #concat to df of interest
    df = pd.concat([df, bill_df_select], axis = 0)
    
    
    
# Initialize the Wordnet Lemmatizer
def lemmatize_text(text):
    '''
    Function that lemmatizes text
    
    Input:
    -String
    
    Output:
    -Lemmatized string
    '''
    #initialize lemmatizer
    words = nlp(' '.join(text))
    
    #return list of lemmatized text
    return([word.lemma_ for word in words])  

df = df.reset_index(drop = True)
    
#convert single string to list
df['title'] = df['title'].apply(lambda x: x.lower().split('; '))
df.title = df.title.apply(lambda x: ' '.join(x).split(' '))


#remove stopwords
df['title'] = df['title'].apply(lambda x: [item for item in x if item not in stopwords.words('english')])

#lemmatize text
df['title'] = df['title'].apply(lambda x :lemmatize_text(x))


df['title'] = df['title'].apply(lambda x: [word for word in x if not word[0].isdigit()])
df['title'] = df['title'].apply(lambda x: [word for word in x if word not in string.punctuation])


#join text
df.title = df.title.apply(lambda x: ' '.join(x))



#initialize vectorizer
vectorizer = CountVectorizer()

#vectorize column
title_vectors = vectorizer.fit_transform(df['title'])


### Topic Modeling ###

# grid search set up

# optimal number of parameters, min number of committees to max number of committees
topics = np.arange(3, 21, 1)

# learning rate
learning_rate = np.arange(0.5, 0.9, 0.1)

#buil param dict
params = {'n_components':topics, 'learning_decay':learning_rate}


# initialize
lda_gridsearch = LDA(random_state = 1234)

# Init Grid Search Class
model_search = GridSearchCV(lda_gridsearch, param_grid = params, cv = 5)

#fit model
model_search.fit(title_vectors)


#pull out best paramters
best_lda_params = model_search.best_params_

#train best model
best_lda = LDA(random_state = 1234, n_components = best_lda_params['n_components'],
               learning_decay = best_lda_params['learning_decay'])


#fit best model
best_lda.fit(title_vectors)

#transform titles into topics
topic_fit = best_lda.transform(title_vectors)

# column names
topicnames = ["Topic" + str(i + 1) for i in range(best_lda.n_components)]


# Make the pandas dataframe
df_topics = pd.DataFrame(np.round(topic_fit, 2), columns=topicnames)

# join with bill title data
df_topics = pd.concat([df.reset_index(drop=True), df_topics.reset_index(drop=True)], axis = 1)

#save as csv
df_topics.to_csv('../Data/BillTitleTopics.csv')


### below code for generating best key words matrix generated from and scoring graph 
### https://www.machinelearningplus.com/nlp/topic-modeling-python-sklearn-examples/#11howtogridsearchthebestldamodel

#get cv results
cv_results = model_search.cv_results_

#get log likelihood scores for each topic with learning decay = optimum
mean_log_likelihood = cv_results['mean_test_score']
mean_log_likelihood = mean_log_likelihood[cv_results['param_learning_decay'] == best_lda_params['learning_decay']]

#plot


# Topic-Keyword Matrix
df_topic_keywords = pd.DataFrame(best_lda.components_)

# Assign Column and Index
df_topic_keywords.columns = vectorizer.get_feature_names()
df_topic_keywords.index = topicnames

# View

# Show top n keywords for each topic
def show_topics(vectorizer=vectorizer, lda_model=best_lda, n_words=20):
    keywords = np.array(vectorizer.get_feature_names())
    topic_keywords = []
    for topic_weights in lda_model.components_:
        top_keyword_locs = (-topic_weights).argsort()[:n_words]
        topic_keywords.append(keywords.take(top_keyword_locs))
    return(topic_keywords)

topic_keywords = show_topics(vectorizer=vectorizer, lda_model=best_lda, n_words = 7)        

# Topic - Keywords Dataframe
df_topic_keywords = pd.DataFrame(topic_keywords)
df_topic_keywords.columns = ['Word '+str(i + 1) for i in range(df_topic_keywords.shape[1])]
df_topic_keywords.index = ['Topic '+str(i + 1) for i in range(df_topic_keywords.shape[0])]
df_topic_keywords.to_csv('../Data/BillTitleTopicsKeyWords.csv')









