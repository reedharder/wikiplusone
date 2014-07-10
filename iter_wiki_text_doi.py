
"""
Created on Fri Jun 20 11:24:24 2014

@author: Reed

a module similar to iter_wiki, parsing links, isbn, arvix number, pmid, pmc, doi
"""
#import pickle
import op
import os
import re 
import itertools
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
                #remove "isbn =" heading
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
                    #remove "isbn =" heading
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
        
# page parser with additional functionality (pmid, pmc, archive parsing, citation type, link category, etc.), can be passed to iter_wiki doi, with *args
def page_parser_plus(elem, namespaces, comment_pattern, inline_pattern, outline_pattern, link_pattern, url_sub, doi_pattern, doi_sub, isbn_pattern, isbn_sub, extlink_pattern, type_pattern,type_sub,pmid_pattern,pmid_sub,pmc_pattern,pmc_sub,arxiv_pattern,arxiv_sub,eprint_pattern,eprint_sub, free_cites=True, free_links=True, include_nolinkpages=False ):  #namesoaces will have format: {'a':'http://www.mediawiki.org/xml/export-0.8/'}
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
        #initialize list of dictionaries, one for each citation/link within page
        link_or_citation_list=[]
        
        #parsing refs with <ref/> tags, to be categorized as in_line references. At present, some older  historical styles, such as the footnote2 and footnote3 methods, are not parsed (see http://en.wikipedia.org/wiki/Wikipedia:Inline_citation)
        #At present, parenthetical citations will not be classed as inline citations because of the added overhead of identifying them as such across different citation templates
        #parenthical citations may instead be classed as free citations, provided that their anchor uses one of the common Citation templates        
        for ref in re_footnote_refs:
            #initialize list of links
            ref_links=[]            
                
            #get type of citation if it exists
            try:
                ref_type=type_pattern.findall(ref)[0][:-1].rstrip().lower()
            except IndexError:
                ref_type=b''
            else:
                ref_type=re.sub(type_sub,b'',ref_type).lstrip()            
        
            #pull out links from ref
            singlereflinks=link_pattern.findall(ref)
            for link in singlereflinks:
                #remove end char
                link=link[:-1]
                #remove "url =" heading if it is there
                if link[:3] == b'url':
                    link = re.sub(url_sub,b'',link)
                #append to list of links from ref
                ref_links.append(link)
                
            #pull out dois from ref
            try:
                doi=doi_pattern.findall(ref)[0]
            except IndexError:
                if ref_type == b'doi': #if cite is doi type, grab number from expected second field and clean it
                    doi = ref.split(b'|')[1].rstrip().lstrip()
                else: # otherwise, assume doi is unavailable
                    doi=b''                
            else:
                #remove end char
                doi=doi[:-1]
                #remove "doi =" heading
                doi=re.sub(doi_sub,b'',doi)
                
            #pull out dois from ref
            try:
                isbn=isbn_pattern.findall(ref)[0]
            except IndexError:
                if ref_type == b'isbn': #if cite is isbn type, grab number from expected second field and clean it
                    isbn = ref.split(b'|')[1].rstrip().lstrip().replace(b'-',b'') 
                else: # otherwise, assume isbn is unavailable
                    isbn=b''
            else:
                #remove end char
                isbn=isbn[:-1]
                #remove "isbn =" heading
                isbn=re.sub(isbn_sub,b'',isbn)
                #strip string of dashes
                isbn=isbn.replace(b'-',b'')
            
            #pull out pmids from ref
            try:
                pmid=pmid_pattern.findall(ref)[0]
            except IndexError:
                 if ref_type == b'pmid': #if cite is pmid type, grab number from expected second field and clean it
                    pmid = ref.split(b'|')[1].rstrip().lstrip()
                 else: # otherwise, assume pmid is unavailable
                    pmid=b''
            else:
                #remove end char
                pmid=pmid[:-1]
                #remove "pmid =" heading
                pmid=re.sub(pmid_sub,b'',pmid)
                
            #pull out pmids from ref
            try:
                pmc=pmc_pattern.findall(ref)[0]
            except IndexError:
                pmc=b''
            else:
                #remove end char
                pmc=pmc[:-1]
                #remove "pmc =" heading
                pmc=re.sub(pmc_sub,b'',pmc)
            
            #get arXiv number from either eprint or arxiv parameter
            try: #get arxiv params from ref
                refarxiv=arxiv_pattern.findall(ref)[0]
            except IndexError:
                refarxiv=b''
                
            try: #eprint params from list
                refeprint=eprint_pattern.findall(ref)[0]
            except IndexError:
                refeprint=b''
            
            if refarxiv:
                arxiv=refarxiv
            elif ref_type.lower() == b'arxiv' and refeprint: # i.e. if type of cite is arxiv and eprint parameter exists...
                arxiv=refeprint
            else:
                arxiv=b''
            
            #append data from ref to list of data from page
            if len(ref_links)+len(isbn)+len(doi)+len(pmid)+len(pmc)+len(arxiv) > 0:
                link_or_citation_list.append({'id':wiki_id,'title':title_text,'info_type':'inline_ref','ref_type':ref_type,'links':ref_links,'isbn':isbn,'doi':doi,'pmid':pmid,'pmc':pmc,'arxiv':arxiv})
            
                        
        
                
        #if parser is to look at non-inline citations
        if free_cites:
           
            #remove inline  refs from text string
            wiki_text=re.sub(inline_pattern,b'',wiki_text)
            #get all non-footnoted citations
            re_free_refs=outline_pattern.findall(wiki_text)
            #loop through refs
            for ref in re_free_refs: 
                
                #initialize list of links
                free_cite_links=[]
                #get type of citation if it exists
                try:
                    ref_type=type_pattern.findall(ref)[0][:-1].rstrip().lower()
                except IndexError:
                    ref_type=b''
                else:
                    ref_type=re.sub(type_sub,b'',ref_type).lstrip()            
            
                #pull out links from ref
                reflinks=link_pattern.findall(ref)
                for link in reflinks:
                    #remove end char
                    link=link[:-1]
                    #remove "url =" heading if it is there
                    if link[:3] == b'url':
                        link = re.sub(url_sub,b'',link)
                    #append to list of links from ref
                    free_cite_links.append(link)
                    
                #pull out dois from ref
                try:
                    doi=doi_pattern.findall(ref)[0]
                except IndexError:
                    if ref_type == b'doi': #if cite is doi type, grab number from expected second field and clean it
                        doi = ref.split(b'|')[1].rstrip().lstrip()
                    else: # otherwise, assume doi is unavailable
                        doi=b''
                else:
                    #remove end char
                    doi=doi[:-1]
                    #remove "doi =" heading
                    doi=re.sub(doi_sub,b'',doi)
                    
                #pull out dois from ref
                try:
                    isbn=isbn_pattern.findall(ref)[0]                    
                except IndexError:
                    if ref_type == b'isbn': #if cite is isbn type, grab number from expected second field and clean it
                        isbn = ref.split(b'|')[1].rstrip().lstrip().replace(b'-',b'') 
                    else: # otherwise, assume isbn is unavailable
                        isbn=b''
                else:
                    #remove end char
                    isbn=isbn[:-1]
                    #remove "isbn =" heading
                    isbn=re.sub(isbn_sub,b'',isbn)
                    #strip string of dashes
                    isbn=isbn.replace(b'-',b'')
                
                #pull out pmids from ref
                try:
                    pmid=pmid_pattern.findall(ref)[0]                    
                except IndexError:                    
                    if ref_type == b'pmid': #if cite is pmid type, grab number from expected second field and clean it
                        pmid = ref.split(b'|')[1].rstrip().lstrip()
                    else: # otherwise, assume pmid is unavailable
                        pmid=b''
                else:
                    #remove end char
                    pmid=pmid[:-1]                    
                    #remove "pmid =" heading
                    pmid=re.sub(pmid_sub,b'',pmid)
                    
                #pull out pmids from ref
                try:
                    pmc=pmc_pattern.findall(ref)[0]
                except IndexError:
                    pmc=b''
                else:
                    #remove end char
                    pmc=pmc[:-1]
                    #remove "pmc =" heading
                    pmc=re.sub(pmc_sub,b'',pmc)
                
                #get arXiv number from either eprint or arxiv parameter
                try: #get arxiv params from ref
                    refarxiv=arxiv_pattern.findall(ref)[0]
                except IndexError:
                    refarxiv=b''
                    
                try: #eprint params from list
                    refeprint=eprint_pattern.findall(ref)[0]
                except IndexError:
                    refeprint=b''
                
                if refarxiv:
                    arxiv=refarxiv
                elif ref_type.lower() == b'arxiv' and refeprint:
                    arxiv=refeprint
                else:
                    arxiv=b''
                
                #add to data to list ADD THIS TO EARLIER THING, CHECK FOR EMPTY MATRIX except for wiki title then add blank_page to info_type and append a dict if desired, check for ALTERNATE DOI SETTINGS 
                if len(free_cite_links)+len(isbn)+len(doi)+len(pmid)+len(pmc)+len(arxiv) > 0:
                    link_or_citation_list.append({'id':wiki_id,'title':title_text,'info_type':'free_ref','ref_type':ref_type,'links':free_cite_links,'isbn':isbn,'doi':doi,'pmid':pmid,'pmc':pmc,'arxiv':arxiv})
                
                    
                    
        if free_links:
            #remove free citations from wikitext
            wiki_text=re.sub(outline_pattern,b'',wiki_text)
            #get links from text
            extlinks=extlink_pattern.findall(wiki_text)
            #remove end character
            extlinks=[x[:-1] for x in extlinks if x]
            #add links to list
            for free_link in extlinks:
                link_or_citation_list.append({'id':wiki_id,'title':title_text,'info_type':'free_link','ref_type':b'','links':[free_link],'isbn':b'','doi':b'','pmid':b'','pmc':b'','arxiv':b''})
                              
           
           
        #create DataFrame to easily check if empty
        pagedf=pd.DataFrame(link_or_citation_list)
        # if dataframe is not empty or         
        if not pagedf.any().any() and include_nolinkpages:
            return [{'id':wiki_id,'title':title_text,'info_type':'no_links_refs','ref_type':b'','links':[b''],'isbn':b'','doi':b'','pmid':b'','pmc':b'','arxiv':b''}]
        elif pagedf.any().any(): 
            return link_or_citation_list
        else:
            return [{}] 
    else: # if not a standard wiki page, signal this by returning empty series
        return [{}]




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
def iter_parse_xml(xml_file, parse_func=page_parser_plus, nskey=''):
    #get appropriate namespace
    nsdict=namespace_grabber(xml_file, nskey=nskey)
    namespaces={'a':nsdict[nskey]} #create dictionary of namespaces for xpath calls later
    #create iterator for parsing xml file incrementally
    iter_tree=etree.iterparse(xml_file, events=('end',), tag=nstagger('', 'page', nsdict))
    #loop through pages in xml file, call parsing function, and clear parsed elements and related references from memory
    #iterparse method modified from: http://www.ibm.com/developerworks/xml/library/x-hiperfparse/ and answers to: http://stackoverflow.com/questions/7171140/using-python-iterparse-for-large-xml-files
    with open('temp_wiki_urls_plus.txt','wb') as urltempfile:
        #prepare csv files/headers
        ffull = []
        
        #compile all regular expression patterns (X_pattern is regex for returning X, X_sub is regex for cleaning returned X of unwanted characters such as 'url=')      
        comment_pattern=re.compile(b'<!--.*?-->',re.DOTALL) #pattern for comments, for removing comments (and thus deprecated links) from text
        inline_pattern=re.compile(b'<ref.*?>.*?</ref>',re.DOTALL) #pattern for finding standard inline citation s
        outline_pattern=re.compile(b'\{\{\s*cite.*?\}\}|\{\{\s*Cite.*?\}\}|\{\{\s*wikicite.*?\}\}|\{\{\s*Citation.*?\}\}|\{\{\s*citation.*?\}\}',re.DOTALL) #pattern for finding other common citation templates that might be outside <ref> tags
        #PERHAPS ADD ARCHIVE SCRIPT FROM EARLIER, OR AS A LATER ARCHIVE PARSING FUNCTION
        link_pattern=re.compile(b'(?<=\[)http://.*?[\s|\]"]|(?<=\[)https://.*?[\s|\"]]|(?<=\[)ftp://.*?[\s|\"]]|(?<=\[)//.*?[\s|\"]]|url\s*=\s*.*?[\s|}]', re.DOTALL) #pattern for finding any external links in citation template
        url_sub=re.compile(b'url\s*=\s*') #pattern to remove 'url=' heading from links
        type_pattern=re.compile(b'\{\{\s*cite.*?[|}]|\{\{\s*Cite.*?[|}]',re.DOTALL) #pattern to find potential type of citation label in template, i.e. "Cite web" or "Cite Book"
        type_sub=re.compile(b'^\{\{\s*cite|^\{\{\s*Cite') #pattern to clean above finds down to just label
        doi_pattern=re.compile(b'doi\s*=\s*.*?[|\s}]',re.DOTALL) #pattern to find dois in citation templates
        doi_sub=re.compile(b'doi\s*=\s*') # etc, see comment at top of this block
        pmid_pattern=re.compile(b'pmid\s*=\s*.*?[|\s}]',re.DOTALL)
        pmid_sub=re.compile(b'pmid\s*=\s*')
        pmc_pattern=re.compile(b'pmc\s*=\s*.*?[|\s}]',re.DOTALL)
        pmc_sub=re.compile(b'pmc\s*=\s*')
        arxiv_pattern=re.compile(b'arxiv\s*=\s*.*?[|\s}]',re.DOTALL)
        arxiv_sub=re.compile(b'arxiv\s*=\s*')
        eprint_pattern=re.compile(b'eprint\s*=\s*.*?[|\s}]',re.DOTALL)
        eprint_sub=re.compile(b'eprint\s*=\s*')         
        isbn_pattern=re.compile(b'isbn\s*=\s*.*?[|\s}]',re.DOTALL)
        isbn_sub=re.compile(b'isbn\s*=\s*')
        extlink_pattern=re.compile(b'(?<=\[)http://.*?[\s|\]"]|(?<=\[)https://.*?[\s|\"]]|(?<=\[)ftp://.*?[\s|\"]]|(?<=\[)//.*?[\s|\"]]',re.DOTALL) # pattern for finding external links not found in templates
        
        #depending on parse function, modify behavior of iter_parse_xml           
        if parse_func.__name__=='page_parser':
            #pass args appropriate for page_parser function
            parse_args=[namespaces, comment_pattern, inline_pattern, outline_pattern, link_pattern, url_sub, doi_pattern, doi_sub, isbn_pattern, isbn_sub, extlink_pattern]
            
            for event, elem in iter_tree: 
               #call parsing function on current page element
                parsed_page=parse_func(elem, *parse_args) 
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
            
        elif parse_func.__name__ == 'page_parser_plus':
            #pass args appropriate for page_parser_plus function
            parse_args=[namespaces, comment_pattern, inline_pattern, outline_pattern, link_pattern, url_sub, doi_pattern, doi_sub, isbn_pattern, isbn_sub, extlink_pattern, type_pattern,type_sub,pmid_pattern,pmid_sub,pmc_pattern,pmc_sub,arxiv_pattern,arxiv_sub,eprint_pattern,eprint_sub]        
            for event, elem in iter_tree: 
               #call parsing function on current page element
                parsed_page=parse_func(elem, *parse_args) 
               #if parsed page was not a non-standard page, add its data to list
                
                if len(parsed_page[0]) > 0:
                    #append data for template page
                    ffull.extend(parsed_page)                
                    
                    #go through list of URLs for page
                    for ref_or_link_dict in parsed_page:
                        for link in ref_or_link_dict['links']:
                        #write URL to txt file
                            urltempfile.write(link + b'\n')                            

                #clear element
                elem.clear()
               #clear refrences from root node to element
                for ancestor in elem.xpath('ancestor-or-self::*'):                
                    while ancestor.getprevious() is not None:
                        del ancestor.getparent()[0]                                           
                 
            
            textdf=pd.DataFrame(ffull)
            textdf.to_csv('doi_parse_extended.csv',sep='\t')                                
           
        
       
    #clear iterator
    del iter_tree
    
    #return list of data dictionaries for each page as a DataFrame
    return  textdf


#function to get count of certain item in dataframe returned by iter_wiki_xml using page_parser function (NOT page_parser_plus), keyed by column names:
def get_item_count(textdf,item='links',returnlist=False):
    #get flattened list from specified columns
    unpackedlist=list(itertools.chain.from_iterable(textdf[item]))
    #get size of list
    num_items=len(unpackedlist)
    ##approximate memory size of list (textdf.values.nbytes + textdf.index.nbytes + textdf.columns.nbytes)
    if returnlist: # if requested, return list and length of list
        return (num_items,unpackedlist)
    else: #otherwise just return number of items
        return num_items


#pass a comparison function from operator module as operator, and a dataframe of page_parser_plus type
def numlinks_filter(df, operator,number=1):
    #map len function to each row of links column, return if satisfies condition imposed by operator and number
    outdf=df[operator(df['links'].map(len),number)] 
    #return filtered dataframe
    return outdf


#keep only reasonable google domains in set of links (no random searches thank you) (will take DF, list or text file list)       
def google_filter():
    pass        

# get google book ids from list of links ((will take DF, list or text file list)
def google_book_grabber():
    pass    

def archive_filter():
    pass

def domain_parser():
    pass

def wiki_to_sql():
    pass





