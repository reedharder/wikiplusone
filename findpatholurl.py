# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 11:57:34 2014

@author: Reed
"""

#script to find pathological URLs in URL list

##import re 
from publicsuffix import PublicSuffixList
from urllib.parse import urlparse
import os
import re
os.chdir("C://Users//Reed//Documents//Github//wikiplus1")
psl=PublicSuffixList()
with open("dat_wiki_urls.txt", 'r', encoding='utf-8') as infile:
    weirdurls_reg=[]
    weirdurls_arc=[]
    for line in infile:
        ##if len(re.findall("^//|^http://|^https://",line)) ==0:
            ##weirdurls.append(line)
    #check if potential web archive
        if re.search("//",line):
            slashsplit=line.split("http://")
            if len(slashsplit)<=2:
                #REMOVE PORT, ADD THIS TO SCRIPT PIPELINE
                dom=urlparse(line).netloc.split(':')[0]
                archive='NULL'
                tldn=psl.get_public_suffix(dom.rstrip())
                try:
                    suff=tldn.split(".",1)[1]
                except IndexError:             
                    errow=[line,dom,tldn]
                    weirdurls_reg.append(errow)
                #ADD THIS POTENTIALLY:
                
            elif len(slashsplit)==3:
                dom=urlparse('//'+ slashsplit[2]).netloc
                archive=urlparse('//'.join([slashsplit[0],slashsplit[1]])).netloc
                tldn=psl.get_public_suffix(dom.rstrip())
                try:
                    suff=tldn.split(".",1)[1]
                except IndexError:
                    
                    errow=[line,dom,tldn]
                    weirdurls_arc.append(errow)
            else:
                pass
