# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 10:32:36 2014

@author: Reed
"""
import os
import re 
import pandas as pd
from lxml import etree

os.chdir("C:\\Users\\Reed\\Documents\\GitHub\\wikiplus1")
a="DdumpAlgebra.xml"
b="simplewikiArticles1.xml"


#function for inserting namespace prefixes, takes name space (string), element tag (string), and a dictionary mapping namespace to url
#returns string usable as a tag call
def nstagger(ns, tag, nsdict):
    return "{" + nsdict[ns] + "}" + tag  #NAME SPACE DICTIONARY MAYBE
    
#AT WHAT POIN TO ENCODE? .ENCODE ON IBM MAY BE FOR PYTHON 2, CHECK PYTHON 2 DOCS. ALSO, GET REGEX NOT RE
#function called for parsing each </page> element in xml file
def page_parser(elem, outfile, namespaces):  #namesoaces will have format: {'a':'http://www.mediawiki.org/xml/export-0.8/'}
    #loop through pages, extract and parse titles/wikitext    
    if int(elem.xpath('a:ns', namespaces=namespaces)[0].text) == 0: #if namespace indicates that this is a standard wikipedia article (not a talk page, etc.)    
        #grab text of </title> and </text> nodes
        title_text = elem.xpath('a:title', namespaces=namespaces)[0].text.encode('utf-8')
        wikitext = elem.xpath('a:revision/a:text', namespaces=namespaces)[0].text.encode('utf-8')
        # a rough parsing of wiki links
        pattern=re.compile(b"\[\[.*?\]\]")
        re_links=pattern.findall(wikitext) #get list of all non overlapping [[..]] patterns
        wikilinks=[] #list of wiki links
        categories=[]
        for link in re_links:
            nopiclink=link.split(b"[[")[-1][:-2] # remove initial '[[', and any picture/file text, and remove final ']]'
            no_alias=nopiclink.split(b"|")[0] # take only the actual link, not what is displayed
            if (no_alias[:9] == b'Category:'):
                 categories.append(no_alias[9:])
            else:
                wikilinks.append(no_alias) #still leaves categories, pics/files with no wikilinks in caption, and subsections. Pics at least can be parsed out
        pattern=re.compile(b"<ref.*?>.*?</ref>")
        re_footnote_refs=pattern.findall(wikitext) 
        #JUST IGNORE WEB ARCHIVES PERHAPS? NO, NON ARCHIVES WILL BE BROKEN. TRY TAKING JUST LAST LINK
        foot_links=[] #list of footnote links, or archives if those exist
        for ref in re_footnote_refs:
            #find list of things after http:// or https:// and up to but not including either a space or "|" or "]"
            pattern=re.compile(b"http://.*?(?=[|\s\]])|https://.*?(?=[|\s\]])")            
            link=pattern.findall(ref)
            # if no links are found in ref, go to next ref
            if len(link) == 0:
                pass
            #if one link is found, take as footnote and append to list
            elif len(link) == 1:
                foot_links.append(link[0])
            # if multiple links are found, check a little deeper
            else: 
                #search for links labled archive
                pattern=re.compile(b"archiveurl\s*=\s*http://.*?(?=[|\s\]])|archiveurl\s*=\s*https://.*?(?=[|\s\]])")
                arch_link=pattern.findall(ref)
                #search for links labled with standard "url="
                pattern=re.compile(b"\|\s*url\s*=\s*http://.*?(?=[|\s\]])|\|\s*url\s*=\s*https://.*?(?=[|\s\]])")
                reglink=pattern.findall(ref)
                #add archive links to footnote list
                if len(arch_link) > 0:
                    foot_links.append(re.sub(b"archiveurl\s*=\s*",b'',arch_link[0],count=0))
                #if there are standard links as well, add them if they have been marked as not broken (i.e. ref has label "deadurl=no")    
                if len(reglink) > 0 and re.search(b"deadurl\s*=\s*no",ref): 
                    foot_links.append(re.sub(b"\|\s*url\s*=\s*",b'',reglink[0],count=0))
        #FOR NOW, write links unorganized to text file (LATER, SQL DATABASE PROBABLY)             
        for link in foot_links:
            outfile.write("%s\n" % link)
            
        # return row of a data frame
        return pd.Series({'title': title_text, 'wikilinks': wikilinks, 'categories': categories, 'footnotes':foot_links, 'num_feet': len(foot_links)})
    else: # if not a standard wiki page, signal this by returning empty series
        return pd.Series({})
        
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
     
     

    

  
def iter_wiki_xml(xml_file, parse_func=page_parser, txt_out='wiki_refs1.txt', nskey=''):
    page_dict_list=[] #initialize list of data for each page
    #get appropriate namespace
    nsdict=namespace_grabber(xml_file, nskey=nskey)
    namespaces={'a':nsdict[nskey]} #create dictionary of namespaces for xpath calls later
    #create iterator for parsing xml file incrementally
    iter_tree=etree.iterparse(xml_file, events=('end',), tag=nstagger('', 'page', nsdict))
    #loop through pages in xml file, call parsing function, and clear parsed elements and related references from memory
    #iterparse method modified from: http://www.ibm.com/developerworks/xml/library/x-hiperfparse/ and answers to: http://stackoverflow.com/questions/7171140/using-python-iterparse-for-large-xml-files
    with open(txt_out, 'at', encoding='utf-8') as outfile:    
        for event, elem in iter_tree: 
           #call parsing function on current page element
           parsed_page=parse_func(elem, outfile=outfile, namespaces=namespaces) 
           #if parsed page was not a non-standard page, add its data to list
           if parsed_page.empty != True:
                page_dict_list.append(parsed_page)
           #clear element
           elem.clear()
           #clear refrences from root node to element
           for ancestor in elem.xpath('ancestor-or-self::*'):                
                while ancestor.getprevious() is not None:
                    del ancestor.getparent()[0]
                
    #clear iterator
    del iter_tree
    #return list of data dictionaries for each page as a DataFrame
    return pd.DataFrame(page_dict_list)        
        

