# Masters-Capstone
This repository contains the code used to generate the results discussed in my Master's Capstone. Listed below are short descriptions of each script/folder, as well as the abstract to the paper itself.

## Folders and Files

- BillText.py
  - Scrapes bill text for each year-bill number key specificed in the main function of the script.
  
- TopicModeling.py
  - Grid searches and trains a topic model to split bill titles into optimal number of topics. 
  - Saves dataframe of topic probability distributions by year-bill number.
  - Pulls out key words from each topic, saves into separate dataframe
  
- scraping/
  - Contains scraping scripts for the Arizona Capitol Times, the Arizona Republic, the Arizona Daily Star, the Phoenix Times, and Google News search. 
  - Each News Site scraping script contains functions that scrape a given url and return the associated article text, article title, and article author. The Arizona Republic scraping script contains a third function that uses the site's search function to scrape articles given input key words and a specified date range. The other three site scrapers receive their list of article urls by utilizing a Google News searchs scraper. This Google News scraper inputs key words and a date range, and outputs article urls.
  
- DataMerge.R
  - Manipulates bill demographic csvs to create variables for modelling (number of committees introduced into, introduced in the Senate or the House, number of sponsors, percentage of sponsors that are Republican).
  - Creates article variables that count number of articles scraped by year-bill number per news source.
  - Merges bill demographic variable dataframe with topic modeling results, and merges that dataframe with article variable dataframe.
  
- DataModelStargazer.pdf
  - Trains three models, and places model results into stargazer for organized outputs.
  - Generates graphs that show article counts and model performance.
  - Compares model fit for statistically significant variables, and displays fit differences in tables.
  
## Abstract

The influence of media effects on policy is well documented. Existing research often points to clear relationships between media attention on national issues and legislative activity on those issues; increased attention on a policy area leads to an increase in bills passed on that topic. While state legislatures pass bills at a higher rate than Congress, less research has been focused on state-level activity. As state-based newspapers often focus on their state-relevant issues more so than national newspapers, this research seeks to develop a generalized media effects model by focusing on article activity of four Arizona newspapers: The Arizona Daily Star, the Arizona Republic, the Arizona Capitol Times, and the Phoenix New Times. While accounting for bill meta variables (number of sponsors, number of committees introduced to, etc.) and bill text data, a logit model was trained on per-bill-topic article counts from each of those four newspapers to determine their effect on the probability of bill passage in the Arizona Legislature. None of the article variables proved to be significant, suggesting that local media coverage on the topic of general legislative topics does not have the same impact on bill passage as national coverage on singular issues. Bill passage rate, however, positively statistically significantly increased with increases to bill meta variables; this finding confirms that these demographic variables are important in understanding why a bill passes. Finally, while initial analysis showed that text data is not inferential to the passage of bill, more work remains to confirm this finding.
