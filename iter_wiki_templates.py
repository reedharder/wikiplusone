# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 13:53:57 2014

@author: Reed
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 11:24:24 2014

@author: Reed

a module similar to iter_wiki but for finding links in templates
"""
import os
#import re 
import MySQLdb
#import csv
import pandas as pd
from lxml import etree
#from collections import Counter
#from urllib.parse import urlparse
#import pickle

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
    if int(elem.xpath('a:ns', namespaces=namespaces)[0].text) == 10: #if namespace indicates that this is a template
        #grab text of </title> and </text> nodes
        title_text = elem.xpath('a:title', namespaces=namespaces)[0].text.encode('utf-8')
        template=title_text.split(b':')[1]
        temp_id = int(elem.xpath('a:id', namespaces=namespaces)[0].text.encode('utf-8'))
        #text of wiki not necessary for now:
        ##wikitext = elem.xpath('a:revision/a:text', namespaces=namespaces)[0].text.encode('utf-8')   
        
        #Use wiki article id to look up external links from SQL table
        cur=db.cursor()
        cur.execute("SELECT el_to FROM externallinks WHERE el_from=%s" % temp_id)
        #get list of links for title
        ext_links=[]
        for row in cur.fetchall():
            ext_links.append(row[0])      
            
            
        # return row of a data frame
        if len(ext_links) > 0:
            return {'title': title_text, 'template':template,'temp_id': temp_id, 'ext_links': ext_links, 'num_links': len(ext_links)}
        else: 
            return {}
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
     
     

    

  
  
def iter_temp_xml(xml_file, parse_func=page_parser, nskey=''):
    #get appropriate namespace
    nsdict=namespace_grabber(xml_file, nskey=nskey)
    namespaces={'a':nsdict[nskey]} #create dictionary of namespaces for xpath calls later
    #create iterator for parsing xml file incrementally
    iter_tree=etree.iterparse(xml_file, events=('end',), tag=nstagger('', 'page', nsdict))
    #loop through pages in xml file, call parsing function, and clear parsed elements and related references from memory
    #iterparse method modified from: http://www.ibm.com/developerworks/xml/library/x-hiperfparse/ and answers to: http://stackoverflow.com/questions/7171140/using-python-iterparse-for-large-xml-files
    with open('temp_wiki_urls.txt','wb') as urltempfile:
        #prepare csv files/headers
        ffull = []
        db = MySQLdb.connect(user='root', passwd='reed2[shandy', db='simple1')
        
        for event, elem in iter_tree: 
           #call parsing function on current page element
            parsed_page=parse_func(elem, namespaces=namespaces, db=db) 
           #if parsed page was not a non-standard page, add its data to list
                                                    
            if len(parsed_page) > 0:
                #append data for template page
                ffull.append(parsed_page)
       
                #go through list of URLs for page
                for link in parsed_page['ext_links']:
                #write URL to txt file
                    urltempfile.write(link + b'\n')
                                            
                 
            
                                            
           #clear element
            elem.clear()
           #clear refrences from root node to element
            for ancestor in elem.xpath('ancestor-or-self::*'):                
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]
        
        #write data to dataframe and csv
        tempdf=pd.DataFrame(ffull)
        tempdf.to_csv('temp_wii_full.csv',sep='\t')
    #clear iterator
    del iter_tree
    
    #return list of data dictionaries for each page as a DataFrame
    return  tempdf


