import sys
import os 

if len(sys.argv) == 1:
    print("Please enter a name for your output file")
    sys.exit()

fileName = sys.argv[1]
fileRoot = fileName[:-4]

if fileName[-4:] != '.xml':
    print("Enter a file name that ends in .xml please")
    sys.exit()

#Open the template file
template = open("cref_cseTemplate",'r')

#Read the urls into urlList
urls = open("4urls.txt",'r')
urlList = urls.readlines()

#Create a new CSE file
newCSE = open(fileName,'a')

#Add the necessary template stuff to the top of the newCSE file
for line in template:
    newCSE.write(line)
template.seek(0)

i = 0 #Line/url counter
k = 0 #File counter
#Keep looping through the urlList as long as there are urls to loop through
while (1):
    #Adds lines to new file, ommiting the fisrt i files
    for line in urlList[i:]:
        #Add url as a new line to the file newCSE and increment the line counter i
        line = line[:-2] 
        line = line.replace("&","&amp;");
        newCSE.write("\n")
        newCSE.write("<Annotation about=\""+line+"\"> \n")
        newCSE.write("<label name=\"wiki_one\"/>\n")
        newCSE.write("</Annotation>\n")
        newCSE.write("\n")
        i = i + 1
        if i >= len(urlList): #This checks if we have added all the urls to break out of for loop
            break
        #Check file size
        newCSE.seek(0,2)
        fileSize = newCSE.tell()
        if fileSize > (1.03e7): #This is for 9.9MB
            #Add the final two lines to end the CSE          
            newCSE.write("</Annotations>\n")
            newCSE.write("</GoogleCustomizations>\n")
            #set newFile to a new name and set up the new file
            k = k+1
            fileName = fileRoot+str(k)+'.xml'
            #Close the old file and reset newCSE to the new fileName
            newCSE.close()
            newCSE = open(fileName,'a')
            #Add the necessary template stuff to the top of the newCSE file   
            for Line in template:
                newCSE.write(Line)
            template.seek(0)
            break
    if i >= len(urlList): #This checks if we have added all the links again to break out of while loop.
        break
        
#Add the urls and add the final two lines to end the CSE
newCSE.write("</Annotations>\n")
newCSE.write("</GoogleCustomizations>\n")
