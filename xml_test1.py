from lxml import etree
import os
import re
os.chdir("C:\\Users\\Reed\\Desktop\\wiki_xml")


# get wiki article text and title
#CHECK IF NOT CATEGORY/REDIRECT/DISAMBIGUATION PAGE??????
fn1="train_notemp.xml"

def dump_parser(file=fn1):
    tree=etree.parse(fn1)
    root=tree.getroot()
    prefix='{' + root.nsmap[None] + '}'
    page=root.find(prefix + 'page') #how to make this cleaner??
    title_text = page.find(prefix + 'title').text
    wikitext = page.find(prefix + 'revision').find(prefix + 'text').text
    
    # a very rough parsing of wiki links 
    re_links=re.findall("\[\[.*?\]\]",wikitext) #get list of all non overlapping [[..]] patterns
    wikilinks=[] #list of wiki links
    for link in re_links:
        nopiclink=link.split("[[")[-1][:-2] # remove initial '[[', and any picture/file text, and remove final ']]'
        no_alias=nopiclink.split("|")[0] # take only the actual link, not what is displayed
        if (no_alias[:5] != 'File:' and no_alias[:6] != 'Image:'):
            wikilinks.append(no_alias) #still leaves categories, pics/files with no wikilinks in caption, and subsections. Pics at least can be parsed out
    
    re_footnote_refs=re.findall("<ref>.*?</ref>",wikitext) 
    #JUST IGNORE WEB ARCHIVES PERHAPS? NO, NON ARCHIVES WILL BE BROKEN. TRY TAKING JUST LAST LINK
    foot_links=[] #list of footnote links, or archives if those exist
    for ref in re_footnote_refs:
        try:
            link=re.findall("http://.*?(?=[|\s\]])|https://.*?(?=[|\s\]])",ref)[-1]
             #finds list of things after http:// or https:// and up to but not including either a space or "|" or "]", and only takes final such item, assuming that this will be the archive copy if it exists, and the normal link if not. Hopefully these are good assumtions 
            foot_links.append(link)
        except IndexError:
            pass
        
    

#NOW GET OTHERTYPES OF LINKS: EXTERNAL, ADDITIONAL FOOT NOTES, ETC. OTHER DATA? REDIRECTS?
#GET JUST DOMAINS OF LINKS ALSO? PROBABLY WAIT UNTIL FINAL ANALYSIS
    
    #stick data into dictionary
    wiki_dict={'title': title_text, 'wikilinks': wikilinks, 'footnotes':foot_links, 'numfeet': len(foot_links)}    
    
    return wiki_dict
    
foo=dump_parser()

with open('plusoneBALLs.txt', 'wt') as thefile:        
    for item in foo['footnotes']:
      thefile.write("%s\n" % item)
'''
&lt;ref&gt;


&lt;/ref&gt;



<ref name=name>content</ref>


URLs must begin with a supported URI scheme. http:// and https:// will be supported by all browsers;



'''