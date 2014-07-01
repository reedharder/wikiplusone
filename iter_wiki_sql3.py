# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 11:24:24 2014

@author: Reed

a module similar to iter_wiki but removing deprecated URL parsing, replaced with external links SQL file
"""
import os
import re 
import MySQLdb
import csv
#import pandas as pd
from lxml import etree
from collections import Counter
from urllib.parse import urlparse
import pickle

os.chdir("C:\\Users\\Reed\\Documents\\GitHub\\wikiplus1")
a="DdumpAlgebra.xml"
b="simplewikiArticles1.xml"


#function for inserting namespace prefixes, takes name space (string), element tag (string), and a dictionary mapping namespace to url
#returns string usable as a tag call
def nstagger(ns, tag, nsdict):
    return "{" + nsdict[ns] + "}" + tag  #NAME SPACE DICTIONARY MAYBE
    
#AT WHAT POIN TO ENCODE? .ENCODE ON IBM MAY BE FOR PYTHON 2, CHECK PYTHON 2 DOCS. ALSO, GET REGEX NOT RE
#function called for parsing each </page> element in xml file
def page_parser(elem, namespaces, db):  #namesoaces will have format: {'a':'http://www.mediawiki.org/xml/export-0.8/'}
    #loop through pages, extract and parse titles/wikitext    
    if int(elem.xpath('a:ns', namespaces=namespaces)[0].text) == 0: #if namespace indicates that this is a standard wikipedia article (not a talk page, etc.)    
        #grab text of </title> and </text> nodes
        title_text = elem.xpath('a:title', namespaces=namespaces)[0].text.encode('utf-8')
        wiki_id = int(elem.xpath('a:id', namespaces=namespaces)[0].text.encode('utf-8'))
        #text of wiki not necessary for now:
        ##wikitext = elem.xpath('a:revision/a:text', namespaces=namespaces)[0].text.encode('utf-8')   
        
        #Use wiki article id to look up external links from SQL table
        cur=db.cursor()
        cur.execute("SELECT el_to FROM externallinks WHERE el_from=%s" % wiki_id)
        #get list of links for title
        ext_links=[]
        for row in cur.fetchall():
            ext_links.append(row[0])      
            
            
        # return row of a data frame
        return {'title': title_text, 'wiki_id': wiki_id, 'ext_links': ext_links, 'num_links': len(ext_links)}
    else: # if not a standard wiki page, signal this by returning empty series
        return {}
        
#grabs namespaces using iterparse if default is not valid
def namespace_grabber(xml_file, nskey=''):
    nsdict = {} # initialize dictonary of namespaces
    # look through start-ns events for namespace
    for event, elem in etree.iterparse(xml_file, events=('start-ns',)):
      ns, url = elem
      nsdict[ns] = url
      # once '' ns is acquired, break
      try: 
          dummy=nsdict['']
          del dummy
          break 
      except KeyError:
          pass
     
    return nsdict
     
     

    

  
  
def iter_wiki_xml(xml_file, parse_func=page_parser, nskey=''):
    dom_full_agg_list=[] #initialize lists of data for each page
    dom_full_split_list=[]
    book_full_id_list=[]
    #get appropriate namespace
    nsdict=namespace_grabber(xml_file, nskey=nskey)
    namespaces={'a':nsdict[nskey]} #create dictionary of namespaces for xpath calls later
    #create iterator for parsing xml file incrementally
    iter_tree=etree.iterparse(xml_file, events=('end',), tag=nstagger('', 'page', nsdict))
    #loop through pages in xml file, call parsing function, and clear parsed elements and related references from memory
    #iterparse method modified from: http://www.ibm.com/developerworks/xml/library/x-hiperfparse/ and answers to: http://stackoverflow.com/questions/7171140/using-python-iterparse-for-large-xml-files
    with open('dat_wiki_full.csv', 'w', newline='', encoding='utf-8') as fullfile, open('dat_wiki_domaggr.csv', 'w', newline='', encoding='utf-8') as domfile, open('dat_wiki_googdomsplit.csv', 'w', newline='', encoding='utf-8') as gdomfile, open('dat_wiki_article_id.csv', 'w', newline='', encoding='utf-8') as article_ind, open('dat_wiki_urls.txt','wb') as urltxtfile:
        #prepare csv files/headers
        ffull = csv.writer(fullfile, delimiter='\t')
        ffull.writerow(['index','title','wiki_id','num_links', 'url','domain','book_id','archive'])
        fdom = csv.writer(domfile, delimiter='\t')
        fdom.writerow(['article','domain(aggregated)','count'])
        fg = csv.writer(gdomfile, delimiter='\t')
        fg.writerow(['article','domain(booksplit)','count'])
        f_ind = csv.writer(article_ind, delimiter='\t')
        f_ind.writerow(['index','article','wiki_id'])
        db = MySQLdb.connect(user='root', passwd='reed2[shandy', db='simple1')
        index=0 # initialize index
        for event, elem in iter_tree: 
           #call parsing function on current page element
            parsed_page=parse_func(elem, namespaces=namespaces, db=db) 
           #if parsed page was not a non-standard page, add its data to list
                                                    
            if len(parsed_page) > 0:
                if len(parsed_page['ext_links'])>0:
					#initialize domain lists
                    dom_aggr=[]
                    dom_googsplit=[]
                                        #google  books pattern
                    pattern=re.compile(b'://books\.google.*?books\?id') #TEST WITH THIS NEW EDIT
                    for link in parsed_page['ext_links']:
                                             
                        #add to index
                        index=index+1
                        #check for google books
                        if pattern.search(link):
                            idpattern=re.compile(b'(?<=books\?id=).*?\Z') 
                            googbook_id=idpattern.findall(link.split(b'&')[0])[0]
                            book_dom=link.split(b'&')[0]
                            book_full_id_list.append(googbook_id)
                        else:
                            googbook_id=b'NULL'
                            book_dom=0
                        
                        #check if potential web archive, parse URL, get DOMAIN
                        if re.search('//',link.decode('utf-8')):
                            slashsplit=link.decode('utf-8').split("http://")
                            if len(slashsplit)<=2:
                                dom=urlparse(link.decode('utf-8')).netloc.split(':')[0].encode('utf-8')
                                archive=b'NULL'
                            elif len(slashsplit)==3:
                                dom=urlparse(link.decode('utf-8')).netloc.split(':')[0].encode('utf-8')
                                archive=urlparse('//'.join([slashsplit[0],slashsplit[1]])).netloc.encode('utf-8')
                            elif len(slashsplit)>3:
                                dom=urlparse(link.decode('utf-8')).netloc.split(':')[0].encode('utf-8')
                                archive=b'UNKNOWN_MULTI_HTTP'                            
                        else:
                            dom=b"STRANGE_OR_BROKEN_LINK"
                            archive=b"NULL"
                            
                        #add doms to list for page                           
                        dom_aggr.append(dom)
                        #if link is google book, add URL all the way to end of id to split domain list
                        if book_dom == 0:
                            dom_googsplit.append(dom)
                        else:
                            dom_googsplit.append(book_dom)
                        #fill full file row:
                        #['index','title','wiki_id','num_links', 'url','domain','book_id','archive']
                        row=[index,parsed_page['title'],parsed_page['wiki_id'],parsed_page['num_links'],link,dom,googbook_id,archive]
                        ffull.writerow(row)
                        
                        #write URL to txt file
                        urltxtfile.write(link + b'\n')
                                            
                    #Once domain lists have been created: analyze, add to files, and add to final lists
                    try:
                        agg_count=Counter(dom_aggr)
                    except TypeError:
                        print(dom_aggr)
                    disagg_count=Counter(dom_googsplit)
                    #fdom.writerow(['article','domain(aggregated)','count'])
                    for key in agg_count:
                        fdom.writerow([parsed_page['title'],key,agg_count[key]])
                    #fg.writerow(['article','domain(booksplit)','count'])    
                    for key in disagg_count:
                        fg.writerow([parsed_page['title'],key,disagg_count[key]])
                    #f_ind.writerow(['index','article','wiki_id'])
                    f_ind.writerow([index,parsed_page['title'],parsed_page['wiki_id']])
                    for l in dom_aggr:
                        dom_full_agg_list.append(l) #initialize list of data for each page
                    for l in dom_googsplit:
                        dom_full_split_list.append(l)
                    
    
                        
                
                                    
                                        
                else:
                        #add to index
                    index=index+1
                        #fill full file row:
                        #['index','title','wiki_id','num_links', 'url','domain','book_id','archive']
                    row=[index,parsed_page['title'],parsed_page['wiki_id'],parsed_page['num_links'],b'_no',b'_no',b'_no',b'_no']
                    ffull.writerow(row)
                    #f_ind.writerow(['index','article','wiki_id'])
                    f_ind.writerow([index,parsed_page['title'],parsed_page['wiki_id']])
            
                                            
           #clear element
            elem.clear()
           #clear refrences from root node to element
            for ancestor in elem.xpath('ancestor-or-self::*'):                
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]
                
    #clear iterator
    del iter_tree
    with open('dat_wiki_bookid_simple.pickle', 'wb') as j:
        pickle.dump(book_full_id_list, j)
    with open('dat_wiki_dom_agg.pickle', 'wb') as k:
        pickle.dump(dom_full_agg_list, k)
    with open('dat_wiki_dom_split.pickle', 'wb') as l:
        pickle.dump(dom_full_split_list, l)
    #return list of data dictionaries for each page as a DataFrame
    return  [book_full_id_list,dom_full_agg_list,dom_full_split_list]     


