### Dataset Creation ###

library(readtext)
library(quanteda)
library(dplyr)
library(stringr)
library(stopwords)
library(tm)
library(SentimentAnalysis)
library(zoo)
library(e1071)
library(caret)


setwd(dirname(rstudioapi::getActiveDocumentContext()$path))

getwd()
### article texts ###

#read in article text for thus-far scraped news sites
azcap = read.csv('../Data/ArticleText/az_capitol_times.csv')
azcap$X = NULL

#change column names
azcap = azcap %>% rename(Author = Title, Title = Author)


#summarise data to create average by bill, year
azcap_sum = azcap %>%
  group_by(Bill, Year) %>%
  summarise(AZCap_Count = n())

#create azcentral dataframe
azcen = NULL

years = 2015:2019
for (year in years) {
  file = paste0('../Data/ArticleText/azcen_articletext_', as.character(year), '.csv')
  if (is.null(azcen)) {
    azcen = read.csv(file)
  } else {
    azcenyear = read.csv(file)
    azcen = rbind(azcen, azcenyear)
    remove(azcenyear)
  }
}
#remove X column
azcen$X = NULL

#remove duplicates
azcen = azcen %>% distinct(Author, Bill, Text, Title, Year)


#summarise data to create average by bill, year
azcen_sum = azcen %>%
  group_by(Bill, Year) %>%
  summarise(AZCen_Count = n())



## Phoenix New Times ##

pnt = NULL

for (year in years) {
  file = paste0('../Data/ArticleText/pnt_articletext_', as.character(year), '.csv')
  if (is.null(pnt)) {
    pnt = read.csv(file)
  } else {
    pntyear = read.csv(file)
    pnt = rbind(pnt, pntyear)
    remove(pntyear)
  }
}

pnt$X = NULL

#remove duplicates
pnt = pnt %>% distinct(Author, Bill, Text, Title, Year)


#summarise data to create average by bill, year
pnt_sum = pnt %>%
  group_by(Bill, Year) %>%
  summarise(PNT_Count = n())



## Arizona Daily Star ## 

azds = NULL

for (year in years) {
  file = paste0('../Data/ArticleText/azds_articletext_', as.character(year), '.csv')
  if (is.null(azds)) {
    azds = read.csv(file)
  } else {
    azdsyear = read.csv(file)
    azds = rbind(azds, azdsyear)
    remove(azdsyear)
  }
}

azds$X = NULL

#remove duplicates
azds = azds %>% distinct(Author, Bill, Text, Title, Year)


#summarise data to create average by bill, year
azds_sum = azds %>%
  group_by(Bill, Year) %>%
  summarise(AZDS_Count = n())


### bills ###
#read in bills to get info if bill passed or not
bill_status = data.frame()
for (year in 2015:2019) {
  #convert to year to read in bill
  year = as.character(year)
  #create path variable
  path= paste0("../Data/Legiscan/", year, "/csv/")
  #read in bills csv and prep it
  year_df = read.csv(paste0(path, 'bills.csv'))
  year_df$passed = ifelse(str_detect(year_df$last_action, 'Chapter') == T, 1, 0)
  year_select = year_df %>% select(bill_number, passed, bill_id)
  year_select$year = year
  
  #read in hist csv
  hist = read.csv(paste0(path, 'history.csv'))
  hist$action = as.character(hist$action)
  
  hist_select = hist %>%
    group_by(bill_id) %>%
    #only keep actions where bills is assigned to committe
    filter(str_detect(action, pattern = 'Assigned')) %>%
    
    #remove rules committe(since every bill is assigned to Rules), unless Rules is only committee of assignment
    mutate(count = n(),
           sen_intro = ifelse(str_detect(action, 'Senate') == T, 1, 0)) %>%
    
    filter((str_detect(action, pattern = 'RULES', negate = T)) | (str_detect(action, pattern = 'RULES') & count == 1)) %>%
    
    #remove other useless words & create variable if introduced in senate
    mutate(action = removeWords(action, c('Assigned to ', ' Committee'))) %>%
    
    #filter so that only house of initial introduction is kept
    filter((sequence - min() < 5) & ((sen_intro == 1 & str_detect(action, 'Senate')) | (sen_intro == 0 & str_detect(action, 'House')))) %>%
    
    #remove Senate and House from actions
    mutate(action = str_remove(action, 'Senate'),
           action = str_remove(action, 'House')) %>%
    
    #create concatenated variable for committees introduced in
    mutate(Committees_Concat = paste(unique(action), collapse = ','),
           Committee_Intro_Count = n()) %>%
    
    #only keep unique rows
    distinct(bill_id, Committees_Concat, Committee_Intro_Count, sen_intro) %>%
    
    #only choose first
    filter(row_number() == 1) %>%
    
    #keep only what we need
    select(bill_id, Committee_Intro_Count, Committees_Concat, sen_intro)
  
  #get sponsor of bill
  people = read.csv(paste0(path, 'people.csv'))
  people_select = people %>% 
                    #binary variable for party of sponsor
                    mutate(RepublicanSponsor = ifelse(party == 'R',1,0)) %>%
                    #keep variables of interest
                    select(people_id, RepublicanSponsor)
  
  #add sponsor data
  sponsors = read.csv(paste0(path, 'sponsors.csv'))
  
  #merge together
  merg = merge(sponsors, people_select)
  #count bill sponsors
  grp = merg %>%
          group_by(bill_id) %>%
          summarise(SponsorCount = n(),
                    RepubSponsorPct = round(sum(RepublicanSponsor)/n(), 3))
  
  hist_select = merge(hist_select, grp, on = 'bill_id', all.x = T)
  
  #merge two dfs together
  year_select = merge(year_select, hist_select, on = 'bill_id', all.x = T)
  
  bill_status = rbind(bill_status, year_select)
}


#fill in nas
bill_status = bill_status %>%
  mutate(Committee_Intro_Count = na.fill(Committee_Intro_Count, 0),
         Committees_Concat = na.fill(Committees_Concat, 'RULES'),
         sen_intro = ifelse(str_sub(bill_status$bill_number, 1, 1) == 'S', 1, 0))

#merge in article data
model_df = merge(bill_status, azcen_sum, 
                 by.x = c('bill_number', 'year'), by.y = c('Bill', 'Year'), all.x = T)%>%
           mutate(AZCen_Count = na.fill(AZCen_Count, 0))
                 
model_df = merge(model_df, azds_sum, 
                 by.x = c('bill_number', 'year'), by.y = c('Bill', 'Year'), all.x = T) %>%
          mutate(AZDS_Count = na.fill(AZDS_Count, 0))               
                 
model_df = merge(model_df, azcap_sum, 
                 by.x = c('bill_number', 'year'), by.y = c('Bill', 'Year'), all.x = T)  %>%
          mutate(AZCap_Count = na.fill(AZCap_Count, 0))

model_df = merge(model_df, pnt_sum, 
                 by.x = c('bill_number', 'year'), by.y = c('Bill', 'Year'), all.x = T)  %>%
           mutate(PNT_Count = na.fill(PNT_Count, 0))        

#read in topic modeling results
bill_topics = read.csv('../Data/BillTitleTopics.csv')
bill_topics$X = NULL
topics_only = bill_topics %>% select(Topic1, Topic2, Topic3)

#get most probable bill topic
topics = colnames(topics_only)[apply(topics_only,1,which.max)]
#add to main df
bill_topics$Top_Topic = topics

#keep columns of interest
topics_select = bill_topics %>% select(bill_number, year, Top_Topic, title)
sim_select = sim %>% select(bill_number, Year, Bill_Sim_Binary)

#merge data together
model_df = merge(model_df, sim_select,
                 by.x = c('bill_number', 'year'),
                 by.y = c('bill_number', 'Year'), all.x = T)

#merge back to model_df
model_df = merge(model_df, topics_select,
                 by.x = c('bill_number', 'year'), 
                 by.y = c('bill_number', 'year'), all.x = T)

#save
write.csv(model_df, '../Data/Model_DataFrame.csv')



