# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 10:06:55 2014

@author: Reed
"""
import os
import pandas as pd
from publicsuffix import PublicSuffixList
os.chdir("C://Users//Reed//Documents//GitHub//wikiplus1")

#get list of country code TLDs from following source:
# http://en.wikipedia.org/wiki/List_of_Internet_top-level_domains#Country_code_top-level_domains
#also interesting: http://www.iana.org/domains/root/db
def countrysufflist():
    code=[]
    country=[]
    with open("countrycodenamelist.txt","r") as ccfile:
        for line in ccfile:
            byct=line.split("\t")
            code.append(byct[0])
            country.append(byct[1].rstrip()[2:])
    
    return [code,country]
            
        
#get parellel lists of country code top level domain and 
cclist=countrysufflist()

#initialize lists
psl=PublicSuffixList()
tldns=[] #domain full
doms=[] #domain base
suffs=[] # suffix
ct_codes=[] #last piece of TLD, potentially country code
ct_names=[] #name if valid
urlcount=[] #count of urls
majorDoms=[] #.com, .edu, .gov, .org (even with additional suffix), else NULL
error=[]
with open("dom_count_full.txt","rb") as funfile:    
    for line in funfile:
        line_list=line.decode('utf-8').split('\t')
        
        tldn=psl.get_public_suffix(line_list[0].rstrip())
        count=int(line_list[1])
        #split domain
        dom_list=tldn.split(".")
        dom=dom_list[0]
        try:
            suff=tldn.split(".",1)[1]
        except IndexError:
            ##print(line_list[0].rstrip())
            ##print(tldn) #WHAT IS GOING ON HERE????
            ##print(line) 
            errow=[line,line_list[0].rstrip(),tldn]
            error.append(errow)
            tldn=line_list[0].rstrip()
            suff='UNKNOWN'
            majDom='NULL'
        else:
            # Check if suffix contains one of the major domains, else NULL
            majBool=False
            for part in reversed(suff.split(".")):
                if part in ['gov','edu','com','org']:
                    majDom=part
                    majBool=True
                    break
            if majBool==False:
                majDom='NULL'
        ct_code=dom_list[-1]
        #search for country code, if successful report name, else NULL
        try:
            ind=cclist[0].index("."+ct_code)
            ct_name=cclist[1][ind]
        except ValueError:
            ct_name="NULL"
            ##ct_code="NULL" #ADD BACK IN ONCE LIST IS INSPECTED
        #append to lists
        tldns.append(tldn)
        doms.append(dom)
        suffs.append(suff)
        ct_codes.append(ct_code)
        ct_names.append(ct_name)
        urlcount.append(count)
        majorDoms.append(majDom)
        
domdf=pd.DataFrame({"domain":tldns,"site_name":doms,"public_suffix":suffs,"country":ct_names,"count":urlcount,"MajorDomain":majorDoms})
    