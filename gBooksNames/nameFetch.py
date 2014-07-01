import urllib.request
import sys

#Define this function latter that takes a txt file pointer and takes the title out of it!
#def extractTitle():
    

txtFileName = sys.argv[1]
bookIds = open(txtFileName, 'r')
outFile = open('outFile','a')
bookIdList = bookIds.readlines()

for id in bookIdList:
    response = urllib.request.urlopen('https://www.googleapis.com/books/v1/volumes/'+id)
    txt  = response.readlines()
    titleLine = txt[6]
    title = titleLine[12:-3]
    title = title.decode("UTF-8")
    outFile.write(title+"\n")
