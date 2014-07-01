# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 15:31:52 2014

@author: Reed
"""
import os
import re
os.chdir("C://Users//Reed//Documents//Github//wikiplus1")
infile='testbooks.txt'

#function to parse textfile (LATER LIST OR SOMETHING) of google books URLs for book ids
def idgrab(infile='testbooks.txt'):
    with open(infile, 'r') as bookfile:
        booklist=bookfile.readlines()
    
    ids=[]
    
    pattern=re.compile(b'(?<=books\?id=).*?\Z')
    for book in booklist:
        bookid=pattern.findall(book.split(b'&')[0].rstrip())
        ids.append(bookid[0])
        
    with open('bookids.txt', 'wt') as outfile:
        for bookid in ids:
            outfile.write(bookid + '\n')
            
    return ids