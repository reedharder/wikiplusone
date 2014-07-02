
"""
Created on Fri Jun 20 11:24:24 2014

@author: Reed

a module similar to iter_wiki, parsing links, isbn from doi
"""
#import pickle
import os
import re 
#import csv
import pandas as pd
from lxml import etree
#from collections import Counter
#from urllib.parse import urlparse
#import pickle

os.chdir("C:\\Users\\Reed\\Documents\\GitHub\\wikiplus1")

a="DdumpAlgebra.xml"
b="simplewikiArticles1.xml"
c="mitosis.xml"

#function for inserting namespace prefixes, takes name space (string), element tag (string), and a dictionary mapping namespace to url
#returns string usable as a tag call
def nstagger(ns, tag, nsdict):
    return "{" + nsdict[ns] + "}" + tag  #NAME SPACE DICTIONARY MAYBE
    
#AT WHAT POIN TO ENCODE? .ENCODE ON IBM MAY BE FOR PYTHON 2, CHECK PYTHON 2 DOCS. ALSO, GET REGEX NOT RE
#function called for parsing each </page> element in xml file
def page_parser(elem, namespaces, comment_pattern, inline_pattern, outline_pattern, link_pattern, url_sub, doi_pattern, doi_sub, isbn_pattern, isbn_sub, extlink_pattern, free_cites=True, free_links=True ):  #namesoaces will have format: {'a':'http://www.mediawiki.org/xml/export-0.8/'}
    #loop through pages, extract and parse titles/wikitext    
    if int(elem.xpath('a:ns', namespaces=namespaces)[0].text) == 0: #if namespace indicates that this is a template
        #grab text of </title> and </text> nodes
        title_text = elem.xpath('a:title', namespaces=namespaces)[0].text.encode('utf-8')
        wiki_id = int(elem.xpath('a:id', namespaces=namespaces)[0].text.encode('utf-8'))
        wiki_text = elem.xpath('a:revision/a:text', namespaces=namespaces)[0].text.encode('utf-8')
        #remove comments
        wiki_text = re.sub(comment_pattern,b'',wiki_text)
        ##DEBUG
        ##with open('wtxt.p','wb') as outfile:
            ##pickle.dump(wiki_text,outfile)
        #get all foot note refs
        re_footnote_refs=inline_pattern.findall(wiki_text)
        #initialize lists of dois
        dois=[]
        isbns=[]
        links=[]
        for ref in re_footnote_refs:
            #pull out links from ref
            reflinks=link_pattern.findall(ref)
            for link in reflinks:
                #remove end char
                link=link[:-1]
                #remove "url =" heading if it is there
                if link[:3] == b'url':
                    link = re.sub(url_sub,b'',link)
                #append to list of links
                if link: # check if empty, if not, proceed
                    links.append(link)
            #pull out dois from ref
            refdois=doi_pattern.findall(ref)
            for doi in refdois:
                #remove end char
                doi=doi[:-1]
                #remove "doi =" heading
                doi=re.sub(doi_sub,b'',doi)
                #append to list of dois
                if doi: # check if empty, if not, proceed
                    dois.append(doi)
            #pull out dois from ref
            refisbns=isbn_pattern.findall(ref)
            for isbn in refisbns:
                #remove end char
                isbn=isbn[:-1]
                #remove "doi =" heading
                isbn=re.sub(isbn_sub,b'',isbn)
                #strip string of dashes
                isbn=isbn.replace(b'-',b'')
                #append to list of dois
                if isbn: # check if empty, if not, proceed
                    isbns.append(isbn)
        #if parser is to look at non-inline citations
        if free_cites:
            #remove inline  refs from text string
            wiki_text=re.sub(inline_pattern,b'',wiki_text)
            #get all non-footnoted citations
            re_free_refs=outline_pattern.findall(wiki_text)
            for ref in re_free_refs:
                    #pull out links from ref
                reflinks=link_pattern.findall(ref)
                for link in reflinks:
                    #remove end char
                    link=link[:-1]
                    #remove "url =" heading if it is there
                    if link[:3] == b'url':
                        link = re.sub(url_sub,b'',link)
                    #append to list of links
                    if link: # check if empty, if not, proceed
                        links.append(link)
                #pull out dois from ref
                refdois=doi_pattern.findall(ref)
                for doi in refdois:
                    #remove end char
                    doi=doi[:-1]
                    #remove "doi =" heading
                    doi=re.sub(doi_sub,b'',doi)                    
                    #append to list of dois
                    if doi: # check if empty, if not, proceed
                        dois.append(doi)
                #pull out dois from ref
                refisbns=isbn_pattern.findall(ref)
                for isbn in refisbns:
                    #remove end char
                    isbn=isbn[:-1]
                    #remove "doi =" heading
                    isbn=re.sub(isbn_sub,b'',isbn)
                    #remove all dashes
                    isbn=isbn.replace(b'-',b'')
                    #append to list of dois
                    if isbn: # check if empty, if not, proceed
                        isbns.append(isbn)
                    
        if free_links:
            #remove free citations from wikitext
            wiki_text=re.sub(outline_pattern,b'',wiki_text)
            #get links from text
            extlinks=extlink_pattern.findall(wiki_text)
            #remove end character
            extlinks=[x[:-1] for x in extlinks if x]
            #add links to list
            links.extend(extlinks)
                  
            
            
        # return row of a data frame
        if len(dois+isbns+links) > 0:
            return {'title': title_text,'id':wiki_id, 'dois': dois, "isbns": isbns, 'links': links, "numlinks": len(links)}
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
     
     

    

  
#main parse function, runs through each page and parses
def iter_parse_xml(xml_file, parse_func=page_parser, nskey=''):
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
        
        #compile all regular expression patterns        
        comment_pattern=re.compile(b'<!--.*?-->',re.DOTALL)
        inline_pattern=re.compile(b'<ref.*?>.*?</ref>',re.DOTALL)
        outline_pattern=re.compile(b'{{\s*cite.*?}}|{{\s*Cite.*?}}|{{\s*wikicite.*?}}',re.DOTALL)
        #LATER ADD OTHER PREFIXES PERHAPS, PLUS ARCHIVE SCRIPT FROM EARLIER
        link_pattern=re.compile(b'(?<=\[)http://.*?[\s|\]"]|(?<=\[)https://.*?[\s|\"]]|(?<=\[)ftp://.*?[\s|\"]]|(?<=\[)//.*?[\s|\"]]|url\s*=\s*.*?[\s|}]', re.DOTALL)
        #PERHAPS TO CHECK LINK VALIDITY? DO WE WANT ARCHIVES? IF SO, do if archive found and dead url no is not found:
        #link_pattern=re.compile(b'(?<=\[)http://.*?[\s|\]"]|(?<=\[)https://.*?[\s|\"]]|(?<=\[)ftp://.*?[\s|\"]]|(?<=\[)//.*?[\s|\"]]|archive\s*=.*?[\s|}]')
        url_sub=re.compile(b'url\s*=\s*')
        doi_pattern=re.compile(b'doi\s*=\s*.*?[|\s}]',re.DOTALL)
        doi_sub=re.compile(b'doi\s*=\s*')
        isbn_pattern=re.compile(b'isbn\s*=\s*.*?[|\s}]',re.DOTALL)
        isbn_sub=re.compile(b'isbn\s*=\s*')
        extlink_pattern=re.compile(b'(?<=\[)http://.*?[\s|\]"]|(?<=\[)https://.*?[\s|\"]]|(?<=\[)ftp://.*?[\s|\"]]|(?<=\[)//.*?[\s|\"]]',re.DOTALL)
        for event, elem in iter_tree: 
           #call parsing function on current page element
            parsed_page=parse_func(elem, namespaces, comment_pattern, inline_pattern, outline_pattern, link_pattern, url_sub, doi_pattern, doi_sub, isbn_pattern, isbn_sub, extlink_pattern) 
           #if parsed page was not a non-standard page, add its data to list
                                                    
            if len(parsed_page) > 0:
                #append data for template page
                ffull.append(parsed_page)
       
                #go through list of URLs for page
                for link in parsed_page['links']:
                #write URL to txt file
                    urltempfile.write(link + b'\n')
                                            
                 
            
                                            
           #clear element
            elem.clear()
           #clear refrences from root node to element
            for ancestor in elem.xpath('ancestor-or-self::*'):                
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]
        
        #write data to dataframe and csv
        textdf=pd.DataFrame(ffull)
        textdf.to_csv('doi_parse.csv',sep='\t')
    #clear iterator
    del iter_tree
    
    #return list of data dictionaries for each page as a DataFrame
    return  textdf


