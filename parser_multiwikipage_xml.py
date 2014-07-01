# -*- coding: utf-8 -*-
"""
Created on Thu Jun 12 10:22:08 2014

@author: Reed

Parser for wiki xml docs with multiple wiki pages, though not suitable for large files 
"""
from lxml import etree
import os
import re
import pandas as pd 
try:
    from itertools import izip as zip
except ImportError: # for Python 3
    pass

os.chdir("C:\\Users\\Reed\\Documents\\GitHub\\wikiplus1")


# get wiki article text and title
#CHECK IF NOT CATEGORY/REDIRECT/DISAMBIGUATION PAGE??????
file="DdumpAlgebra.xml"

def dump_parser(file="DdumpAlgebra.xml", txt_out="wikilinks1.txt"):
  
    #parse xml file, get root
    tree=etree.parse(file)
    root=tree.getroot()
    prefix='{' + root.nsmap[None] + '}'
    #get all elements labeled page
    page_list=root.findall(prefix + 'page') #how to make this cleaner??
    #initialize dataframe for storing parsed data
    num_pages=len(page_list) #number of pages
    wiki_df = pd.DataFrame(columns=['title','wikilinks','footnotes','num_feet'], index=range(1,num_pages+1))
    #loop through pages, extract and parse titles/wikitext
    with open(txt_out, 'wt') as outfile:   
        for page, i in zip(page_list, range(1,num_pages+1)):        
            title_text = page.find(prefix + 'title').text
            wikitext = page.find(prefix + 'revision').find(prefix + 'text').text
            
            # a very rough parsing of wiki links 
            re_links=re.findall("\[\[.*?\]\]",wikitext) #get list of all non overlapping [[..]] patterns
            wikilinks=[] #list of wiki links
            categories=[]
            for link in re_links:
                nopiclink=link.split("[[")[-1][:-2] # remove initial '[[', and any picture/file text, and remove final ']]'
                no_alias=nopiclink.split("|")[0] # take only the actual link, not what is displayed
                if (no_alias[:9] == 'Category:'):
                     categories.append(no_alias[9:])
                else:
                    wikilinks.append(no_alias) #still leaves categories, pics/files with no wikilinks in caption, and subsections. Pics at least can be parsed out
            
            re_footnote_refs=re.findall("<ref.*?>.*?</ref>",wikitext) 
            #JUST IGNORE WEB ARCHIVES PERHAPS? NO, NON ARCHIVES WILL BE BROKEN. TRY TAKING JUST LAST LINK
            foot_links=[] #list of footnote links, or archives if those exist
            for ref in re_footnote_refs:
                #find list of things after http:// or https:// and up to but not including either a space or "|" or "]"
                link=re.findall("http://.*?(?=[|\s\]])|https://.*?(?=[|\s\]])",ref)
                # if no links are found in ref, go to next ref
                if len(link) == 0:
                    pass
                #if one link is found, take as footnote and append to list
                elif len(link) == 1:
                    foot_links.append(link[0])
                # if multiple links are found, check a little deeper
                else: 
                    #search for links labled archive
                    arch_link=re.findall("archiveurl\s*=\s*http://.*?(?=[|\s\]])|archiveurl\s*=\s*https://.*?(?=[|\s\]])",ref)
                    #search for links labled with standard "url="
                    reglink=re.findall("\|\s*url\s*=\s*http://.*?(?=[|\s\]])|\|\s*url\s*=\s*https://.*?(?=[|\s\]])",ref)
                    #add archive links to footnote list
                    if len(arch_link) > 0:
                        foot_links.append(re.sub("archiveurl\s*=\s*",'',arch_link[0],count=0))
                    #if there are standard links as well, add them if they have been marked as not broken (i.e. ref has label "deadurl=no")    
                    if len(reglink) > 0 and re.search("deadurl\s*=\s*no",ref): 
                        foot_links.append(re.sub("\|\s*url\s*=\s*",'',reglink[0],count=0))
            #FOR NOW, write links unorganized to text file (LATER, SQL DATABASE PROBABLY)
                 
            for link in foot_links:
                outfile.write("%s\n" % link.encode('utf-8'))
            #stick data into pandas DataFrame (MAKE SURE IT WON'T GET TO BIG)      
            wiki_df.loc[i]=pd.Series({'title': title_text, 'wikilinks': wikilinks, 'categories': categories, 'footnotes':foot_links, 'num_feet': len(foot_links)})

#NOW GET OTHERTYPES OF LINKS: EXTERNAL, ADDITIONAL FOOT NOTES, ETC. OTHER DATA? REDIRECTS?
#GET JUST DOMAINS OF LINKS ALSO? PROBABLY WAIT UNTIL FINAL ANALYSIS
    
    
    return wiki_df
    
'''
START NEW SCRIPT COPY FOR DATABASE 

<ref name=name>content</ref> ADD THIS KIND OF CITATION TO REG EXPRESSIONS
AND OTHER CITATION TYPES
AND MODIFY SUCH THAT LARGE XML FILES CAN BE PARSED NOT IN MEM
FROM WIKI LINKS, PERHAPS REMOVE ALL {{..}}, such as {{PAGENAME}}, plus (disambiguation)


FOR TXT FILE SAVING, PERHAPS compress, or WHEN IT GETS TO LARGE START A NEW TEXT FILE?
'''
