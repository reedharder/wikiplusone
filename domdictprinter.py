# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 15:35:08 2014

@author: Reed
"""
#import sys

from collections import Counter

aggCount=Counter(lists[1])
with open('dom_count_full.txt', 'w', encoding='utf-8') as outf:
    for label,value in aggCount.most_common():
        try:
            outf.write(label.decode('utf-8') + "\t" +str(value) +"\n")
        except UnicodeEncodeError as e:
            print(label)
            print(value)
            print(e)
     
     
bookCount=Counter(lists[0])
with open('book_count_full.txt', 'w', encoding='utf-8') as outf:
    for label,value in bookCount.most_common():
        try:
            outf.write(label.decode('utf-8') + "\t" +str(value) +"\n")
        except UnicodeEncodeError as e:
            print(label)
            print(value)
            print(e)    
'''       
b'//www.town.\xc5\x8ctaki.chiba.jp'
1
'charmap' codec can't encode character '\u014c' in position 11: character maps to <undefined>

In [116]: b'//www.town.\xc5\x8ctaki.chiba.jp'.decode('utf-8')
Out[116]: '//www.town.Ōtaki.chiba.jp'

In [117]: 
'''