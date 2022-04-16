#Import necessary libraries
from urllib.request import urlretrieve
import os.path
import os


#Creates a class that contains the scraping essentials
class ScrapingEssentials(object):

    #Necessaary Class Variables
    categories = []
    #Initializing a directory for the pictures to come in
    def __init__(self, source,currentI,rpath,startIndex):
        self.number = startIndex
        self.source = source
        self.currentItem = currentI
        self.path = rpath
        file_path_string = rpath + source
        if not os.path.exists(file_path_string):
            os.makedirs(file_path_string)    
    #Convert the file from a url to an actual image file and store it on the commputer
    def download_image(self, link):
        try:
            done = False
          
            #Make a requests object
            #Make a folder name
            folder_name =  self.currentItem 
          
            #Make the directory of the folder
            file_path_string =  self.path + self.source + "/" + folder_name
            file_path = os.path.join(file_path_string, (str(self.number) + ".jpg"))

            if not os.path.exists(file_path_string):
                os.makedirs(file_path_string)
            #Download it on the computer
          
            self.number += 1

            urlretrieve(link, file_path)

            print
        except Exception:
            pass
