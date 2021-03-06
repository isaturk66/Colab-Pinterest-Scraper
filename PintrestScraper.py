# Import necessary libraries
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.support import ui
from EnglishScraper import ScrapingEssentials
import threading
import argparse
import sys
from os.path import exists
import os

sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

doneURLs = []
def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(
        description='Webscraper for pinterest')
    parser.add_argument('--username',
                        dest='username_id', help='Username for pinterest account',
                        default='', type=str)
    parser.add_argument('--password',
                        dest='password_id', help='Password for pinterest account',
                        default='', type=str)
    parser.add_argument('--path',
                        dest='path_id', help='Path of the dataset directory',
                        default='', type=str)
    parser.add_argument('--search',
                        dest='search_id', help='The search text that will be searched in pinterest',
                        default='', type=str)

    args = parser.parse_args()
    return args



args = parse_args()


rootPath = args.path_id
search = args.search_id
username=args.username_id
pasw = args.password_id


try:
  fileList = os.listdir(rootPath+"/Pinterest/"+search)
  startIndex= int(fileList[-1][0:-4])+1
except:
  startIndex= 0

t = ScrapingEssentials("Pinterest",search,rootPath,startIndex)


# Determines if the page is loaded yet.
def page_is_loaded(driver):
    return driver.find_element_by_tag_name("body") != None


# Logs in to Pinterest.com to access the content
def login(driver, username, pasw):
    #if driver.current_url != "https://www.pinterest.com/login/?referrer=home_page":
    driver.get("https://www.pinterest.com/login/?referrer=home_page")
    wait = ui.WebDriverWait(driver, 10)
    wait.until(page_is_loaded)
    email = driver.find_element_by_xpath("//input[@type='email']")
    password = driver.find_element_by_xpath("//input[@type='password']")
    email.send_keys(username)
    password.send_keys(pasw)
    # driver.find_element_by_xpath("//div[@data-reactid='30']").click()
    password.submit()
    time.sleep(3)
    print("Teleport Successful!")


# Search for the product, this is the way to change pages later.
def search_for_product(driver, keyword):
    seeker = driver.find_element_by_xpath("//input[@placeholder='Search']")
    seeker.send_keys(keyword)
    seeker.submit()


# Finds the detailed product page of each "pin" for pinterest
def download_pages(driver, valid_urls):
    list_counter = 0
    try:
      with open(rootPath+"Pinterest/"+"/sources.txt",'r') as f: sourceList = f.read().splitlines()
    except:
      sourceList = []
    


    # Pinterest happens to change its HTML every once in a while to prevent botting.

    # This should account for all the differences
    # soup = BeautifulSoup(driver.page_source, "lxml")
    # for pinWrapper in soup.find_all("div", {"class": "pinWrapper"}):
    #     class_name = pinWrapper.get("class")
    #     print(class_name)
    #     if "_o" in class_name[0]:
    #         print(class_name)
    #         break
    #
    # #Finds the tags of the HTML and adjusts it
    # name = " ".join(class_name)
    # print(name)

    # Does this until you have 10000 items or the program has gone on for long enough, meaning that it reached the end of results
    beginning = time.time()
    end = time.time()
    while list_counter < 10000 and beginning - end < 30:
        beginning = time.time()
        
        # ----------------------------------EDIT THE CODE BELOW------------------------------#
        # Locate all the urls of the detailed pins
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # for c in soup.find_all("div", {"class": name}):
        
        for pinLink in soup.find_all("div", {"class": "XiG sLG zI7 iyn Hsu"}):
            for a in pinLink.find_all("a"):
            
                url = ("https://pinterest.com" + str(a.get("href")))
                # Checks and makes sure that the pin isn't there already and that random urls are not invited
                if len(url) < 60 and url not in valid_urls and "A" not in url and url not in sourceList:
                    # ---------------------------------EDIT THE CODE ABOVE-------------------------------#
                    valid_urls.append(url)
                   # print("found the detailed page of: " + str(list_counter))
                    list_counter += 1
                    end = time.time()
                time.sleep(.15)
                # Scroll down now
        driver.execute_script("window.scrollBy(0,300)")
    return


# Downloads the image files from the img urls
def get_pic(valid_urls, driver):
    sourceFilePath =rootPath+"Pinterest/"+"/sources.txt"
    try:
      if(not exists(sourceFilePath)):
        os.makedirs(rootPath+"Pinterest/"+search)
        tempFile = open(sourceFilePath, "w")
        tempFile.close()
    except:
      print("Path creation exception")
    sourceFile = open(sourceFilePath, "a")  # append mode

    get_pic_counter = 0
    while (get_pic_counter < len(valid_urls)-1):
        print("Restarting Iteration")
        # Now, we can just type in the URL and pinterest will not block us
        for urls in valid_urls:
            if(urls in doneURLs):
              break
            driver.get(urls)

            # Wait until the page is loaded
            if driver.current_url == urls:
                wait = ui.WebDriverWait(driver, 10)
                wait.until(page_is_loaded)
                loaded = True
            # -----------------------------------EDIT THE CODE BELOW IF PINTEREST CHANGES---------------------------#
            # Extract the image url
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            try:
              imgs = soup.findAll('img')
              img_link = False
              for img in imgs:
                img_l = img.get("src")
                if("originals" in img_l or "564x" in img_l):
                  img_link = img_l
                  break
              if(img_link != False):
                print(str(get_pic_counter) + "  Downloading the image "+ str(img_link))
                get_pic_counter += 1
                t.download_image(img_link)
              else:
                print("No image with originals or 564x in "+str(urls))
              doneURLs.append(urls)
              sourceFile.write(urls+"\n")
              sourceFile.flush()

            except Exception as e:
              print("Parse Exeption")
              print(e.args)
              print(driver.page_source)
            # ---------------------------------EDIT THE CODE ABOVE IF PINTEREST CHANGES-----------------------------#


def main():
    global t
    driver1 = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
    driver2 = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
    driver1.get("https://www.pinterest.com/login/?referrer=home_page")
    driver2.get("https://www.pinterest.com/login/?referrer=home_page")
    # Log in to Pinterest.com




    login(driver1, username, pasw)
    login(driver2, username, pasw)
    # Make sure it's loaded before doing anything
    
    time.sleep(5)

    loaded1 = False
    while loaded1 == False:
        print(driver1.current_url)
        if driver1.current_url != "https://www.pinterest.com/login/?referrer=home_page":
            loaded1 = True
        else:
            print("Waiting 45 seconds")
            time.sleep(45)
            login(driver1, username, pasw)
            time.sleep(5)

    loaded2 = False
    while loaded2 == False:
        print(driver1.current_url)
        if driver1.current_url != "https://www.pinterest.com/login/?referrer=home_page":
            loaded2 = True
        else:
            print("Waiting 45 seconds")
            time.sleep(45)
            login(driver2,  username, pasw)
            time.sleep(5)



    print("Starting threads...")
    keyword = search
    valid_urls = []
    url = "https://pinterest.com/search/pins/?q="

    keyList = keyword.split()

    if(len(keyList)!= 1):
      for i in range(0,len(keyList)):
        element = keyList[i]
        url += element
        if(i != len(keyList)-1):
          url+="%20"
    else:
      url+= keyList[0]

    url+= "&rs=typed&term_meta[]="

    if(len(keyList)!= 1):
      for i in range(0,len(keyList)):
        element = keyList[i]
        url += element
        if(i != len(keyList)-1):
          url+="%7Ctyped&term_meta[]="
        else:
          url+="%7Ctyped"
    else:
      url+= keyList[0] + "%7Ctyped"

        
    driver1.get(url)

    time.sleep(3)

    print("Fetching search results...")
    t1 = threading.Thread(target=download_pages, args=(driver1, valid_urls,))
    t1.setDaemon(True)
    t1.start()
    
    time.sleep(15)
    print("Downloading pictures...")

    t2 = threading.Thread(target=get_pic, args=(valid_urls, driver2,))
    t2.setDaemon(True)
    t2.start()
    #
    t2.join()

    print("Done")


if __name__ == "__main__":
    main()

else:
    main()