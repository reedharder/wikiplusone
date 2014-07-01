# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 09:45:42 2014

@author: Reed
"""
#FIGURE OUT in wikilist
import os
import re
import codecs
import pandas as pd
from collections import Counter
os.chdir("C://Users//Reed//Documents//Github//wikiplus1")
urlfile="wiki_refs.txt"

##with codecs.open(urlfile,'r', encoding="ISO-8859-1") as f:
       ## lines = f.readlines()

def getURL_nopath(urlfile="wiki_refs.txt"):
    with codecs.open(urlfile,'r', encoding="ISO-8859-1") as f: # WORKS IF ENCODED IN IS)O, WHY IS THIS JESUS
        lines = f.readlines()
    URLnopath_list = []
    for line in lines:
        URLnopath=re.findall("http://.*?(?=/)|https://.*?(?=/)", line)
        for url in URLnopath:
            URLnopath_list.append(url)
    return URLnopath_list
        
##count_dict=Counter(getURL_nopath())

## WANT OVERALL DOMAIN COUNTS, FULL URL/DOMAIN/WIKILIST, ALL DOMAIN/WIKI PAIRS + COUNTS, HISTOGRAMS OF COUNTS (POWER)

##wikidf=pd.io.pickle.read_pickle("wikidf_simple.pddf")

##urldf=pd.DataFrame(columns=['title', 'url', 'domain'], index(1, wikidf.shape[0] + 1)

def wikidf_byrow():     
    print("loading wiki data...")
    wikidf=pd.io.pickle.read_pickle("wikidf_simple.pddf")
    urldf_list=[]
    domlinkdf_list=[] 
    domain_list=[]
    print("building dataframes..")
    for index, row in wikidf.iterrows():
        numfeet=row['num_feet']
        if numfeet > 0:
            #make url database
            urldf=pd.DataFrame(columns=['url', 'domain', 'title','archived'], index=range(1,numfeet + 1))
            urldf['url']=row['footnotes']
            urldf['title']=row['title']
            #seperate archived domain from web archive
            domains = []
            archives = []
            for line in row['footnotes']:
                domain=re.findall("http://.*?(?=/)|https://.*?(?=/)", line)
                #GET LINE BELOW INTO LINE ABOVE                
                if len(domain)==0:
                    domain=re.findall("http://.*?(?=\Z)|https://.*?(?=/Z)", line)
                if len(domain)==2:
                    domains.append(domain[1])
                    archives.append(domain[0])
                else:
                    domains.append(domain[0])
                    archives.append('0')
            urldf['domain']=domains
            urldf['archived']=archives
            #append to full df list
            urldf_list.append(urldf)
            #make domain list with links 
            domlinkpairs=[(row['title'],dom) for dom in domains]
            domlink_dict=Counter(domlinkpairs)
            domlinkdf=pd.DataFrame(columns=['domain', 'title', 'count'], index=range(1,len(domlink_dict) + 1))
            for i, entry in zip(range(1,len(domlink_dict) + 1), domlink_dict):
                domlinkdf.loc[i]['domain']=entry[1]
                domlinkdf.loc[i]['title']=entry[0]
                domlinkdf.loc[i]['count']=domlink_dict[entry]
            #append to dom/link df list
            domlinkdf_list.append(domlinkdf)
            #append domain to simple domain list
            for dom in domains:
                domain_list.append(dom)
            ##DEBUG
            if index==1:
                print("first row constructed")
    #concatnate data frames
    print("compiling dataframe..")
    urldf_full=pd.DataFrame(urldf_list)
    domlinkdf_full=pd.DataFrame(domlinkdf_list)
    domaincount=Counter(domain_list)
    domcountdf_full=pd.DataFrame([(entry,domaincount[entry]) for entry in domaincount], columns=('domain', 'count'))
    #write to csv           
    print("writing to csvs...")
    urldf_full.to_csv("urls_full.csv")    
    domlinkdf_full.to_csv("doms_links.csv")
    domcountdf_full.to_csv("doms.csv")
    
    #return list of dfs
    return [urldf_full,domlinkdf_full,domcountdf_full]
                    
                    
    
    
    




