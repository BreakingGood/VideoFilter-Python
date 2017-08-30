import sys, pygame, urllib.request
import os
import webbrowser
import requests
import math
import time
from bs4 import BeautifulSoup

#-This program is deprecated and no longer necessary-
#-A newer version is available using Python only for the web scraping and C++ for the UI-
#-That one is also deprecated-

#Author: Sam Wolfe
#Purpose: Scrape OSU lecturer website for videos and enable easier sorting. 

#Globals, the height and weidth of an image
IMAGE_WIDTH = 300
IMAGE_HEIGHT = 277

#Returns the total number of images that can fit on the page
def getTotalImagesPerPage(screen):
    global IMAGE_HEIGHT
    global IMAGE_WIDTH

    rows = math.floor(screen.get_height() / (IMAGE_HEIGHT + 60))
    columns = math.floor(screen.get_width() / (IMAGE_WIDTH + 70))

    return (rows * columns)

#Gets URLs for all of the images on the page
def getPageData(soup, imageList, attrList, linkList):
    #Locate all img tags and get their src (This is the image direct link)
    #Then add it to list
    for image in soup.find_all('img'):
        text = image.get('src')
        if(".jpg" in text):
            imageList.append(text)

    #Locate all the 'a' tags and get their href attribute (This will give all links on the page)
    #Some links are not needed and are filtered out.      
    for image in soup.find_all('a'):
        text = image.get('href')
        if(".bz" not in text) and ("dmca-form" not in text) and ("javascript" not in text) and (len(text) > 10):
            linkList.append(text)
    
    #Locate all paragraph tags, get all of the text, and add it to a list
    #This will effectively include all of the text under an image
    for page in soup.find_all('p'):
        if(len(page) > 1):
            attrList.append(page.getText())

def getTotalPages(pageHTML):
    #parse the raw HTML to calculate the total number of pages
    fullPageText = pageHTML
    firstNumIndex = (fullPageText.find("Page ") + 5)
    if(firstNumIndex != 4):
        while(fullPageText[firstNumIndex].isnumeric()):
            firstNumIndex = firstNumIndex + 1
        
        firstNumIndex = firstNumIndex + 4
        allNumChars = ""
        while(fullPageText[firstNumIndex].isnumeric() or fullPageText[firstNumIndex] == ","):
            if(fullPageText[firstNumIndex] != ","):
                allNumChars = allNumChars + fullPageText[firstNumIndex]
            firstNumIndex = firstNumIndex + 1
    else:
        allNumChars = ("1")

    return int(allNumChars)

#Break down the attrList into manageable parts
def parseAttrList(attrList, sizeList, durList):
    for idx, attr in enumerate(attrList): 
        curAttrString = attrList[idx]

        #Get the size
        sizeIndexStart = curAttrString.index("(")
        sizeIndexEnd = curAttrString.index(")")
        sizeSubstring = curAttrString[sizeIndexStart+1:sizeIndexEnd]
        sizeIndexStart = sizeSubstring.index(" ")
        sizeSubstring = sizeSubstring[:sizeIndexStart]
        sizeList.append(sizeSubstring)

        #Get the duration
        durIndexStart = curAttrString.index("duration")
        durIndexStart = durIndexStart + 10
        durIndexEnd = durIndexStart + 8
        durSubstring = curAttrString[durIndexStart:durIndexEnd]
        durList.append(durSubstring)

    del attrList[:]

def convertDurationToValue(dur):
    #dur is a string in the format 00:00:00
    #this returns a conversaion to seconds for raw comparison
    totalDur = 0
    durHour = dur[:2]
    durMin = dur[3:5]
    durSec = dur[6:8]
    totalDur += int(durHour)*3600 + int(durMin)*60 + int(durSec)
    return totalDur

def populateWindow(imageRectList, videoList, screen, pageNumber, totalImagesCollected):
    
    global IMAGE_WIDTH
    global IMAGE_HEIGHT
    spaceUnderImages = 50
    spaceBetweenImages = 70
    menuOffset = 50
    #Get the width of the window, divide it by the width of an image
    #This gives the total images per row
    screenWidth = screen.get_width()
    imagesPerRow = math.floor(screenWidth / IMAGE_WIDTH) - 1

    imagesDrawn = getTotalImagesPerPage(screen)

    rowsUsed = 0
    usedImages = 0

    for idx in range (0, imagesDrawn):
        #Once we fill up a row with the images, add one to row multiplier
        if(usedImages > imagesPerRow):
            usedImages = 0
            rowsUsed = rowsUsed + 1
        if(idx + (pageNumber * imagesDrawn)) < totalImagesCollected:
            imageRectList[idx + (pageNumber * imagesDrawn)].x = (usedImages * (IMAGE_WIDTH + spaceBetweenImages))
            imageRectList[idx + (pageNumber * imagesDrawn)].y = (rowsUsed * (IMAGE_HEIGHT + spaceUnderImages)) + menuOffset
        
        usedImages = usedImages + 1
        
    

def populateImageAndRectList(imgList, imgRectList, numOfImages):
    idx = 0
    filename = ""
    while (idx < numOfImages):
        #Construct a file name in the format "imageX.jpg" where X is the index
        filename = "image" + str(idx)

        #Fill up a list with the actual images and a list with the image rects
        imgList.append(pygame.image.load("project/images/"+filename+".jpg"))
        imgRectList.append((imgList[idx]).get_rect())
        idx = idx + 1
        

#Fill the videoList with video objects containing all necessary attributes
def populateVideoList(videoList, imageListURLs, sizeList, durList, linkList):
    for idx, image in enumerate(imageListURLs):
        videoList.append(video(image,sizeList[idx],durList[idx], linkList[idx]))
    del imageListURLs[:]
    del sizeList[:]
    del durList[:]
    del linkList[:]

#Fill the textListDur and textListSize lists with font objects
def populateTextLists(videoList, textListDur, textListSize, myFont):
    color = (255,255,255)
    for video in videoList:
        textListDur.append(myFont.render(video.dur, 1, color))
        textListSize.append(myFont.render(video.size + " MB", 1, color))

#Draw the text lists to the screen.
def drawTextLists(textListDur, textListSize, screen, imgRectList, pageNumber, totalImagesCollected):
    global IMAGE_HEIGHT
    spaceBetweenText = 18
    imagesDrawn = getTotalImagesPerPage(screen)
    idx = 0

    textOffset = 120
    while (idx < imagesDrawn):
        if(idx + (pageNumber * imagesDrawn)) < totalImagesCollected:
            screen.blit(textListDur[idx + (pageNumber * imagesDrawn)], (imgRectList[idx + (pageNumber * imagesDrawn)].x + textOffset,imgRectList[idx].y + IMAGE_HEIGHT))
            screen.blit(textListSize[idx + (pageNumber * imagesDrawn)], (imgRectList[idx + (pageNumber * imagesDrawn)].x + textOffset,imgRectList[idx].y + IMAGE_HEIGHT + spaceBetweenText))
        idx = idx + 1

#Keeps the menu bar equal to the width of the window
def setupMenu(menuRect, menuRectDraw, screen):
    menuRect = pygame.Rect(0,0,screen.get_width(),40)
    menuRectDraw = pygame.draw.rect(screen, (50,50,50),menuRect)

def clickIndex(pos, imgRectList, screen, pageNumber, totalImagesCollected):

    imagesPerPage = getTotalImagesPerPage(screen)
    index = -1
    for idx in range(0, imagesPerPage):
        if(idx + (pageNumber * imagesPerPage)) < totalImagesCollected:
            if(imgRectList[idx + (imagesPerPage * pageNumber)].collidepoint(pos)):
                index = idx + (imagesPerPage * pageNumber)

    return index

#This is what will be done when an image is clicked. The index of the clicked image is passed
def processImageClicked(index, videoList):

    url = videoList[index].link
    webbrowser.open_new_tab(url)

    print("Video #"+str(index))

def generatePageLinks(totalPages, pageLinkURLs, name):
    for idx in range(2,totalPages+1):
        link = "http//-website not public-.org" + str(idx) + "/?s=" + name
        pageLinkURLs.append(link)

#Produces filtered lists, longest duration first
def filterLists(rectList, videoList, rectListFiltered, videoListFiltered, imgList, imgListFiltered, textListDur, textListDurFiltered, textListSize, textListSizeFiltered):
    tempVideoList = videoList[:]
    tempRectList = rectList[:]
    tempImgList = imgList[:]
    tempTextListDur = textListDur[:]
    tempTextListSize = textListSize[:]

    maxDur = 0
    maxDurIndex = 0
    while(len(tempVideoList) > 0):
        for idx, video in enumerate(tempVideoList):
            if convertDurationToValue(video.dur) > maxDur:
                maxDur = convertDurationToValue(video.dur)
                maxDurIndex = idx
        videoListFiltered.append(tempVideoList[maxDurIndex])
        rectListFiltered.append(tempRectList[maxDurIndex])
        imgListFiltered.append(tempImgList[maxDurIndex])
        textListDurFiltered.append(tempTextListDur[maxDurIndex])
        textListSizeFiltered.append(tempTextListSize[maxDurIndex])
        del tempVideoList[maxDurIndex]
        del tempRectList[maxDurIndex]
        del tempImgList[maxDurIndex]
        del tempTextListDur[maxDurIndex]
        del tempTextListSize[maxDurIndex]
        maxDur = 0
        maxDurIndex = 0

class video:
    def __init__(self, imageURL, size, dur, link):
        self.image = imageURL
        self.size = size
        self.dur = dur
        self.link = link

########### START GAME INITIALIZATION ##################################################################################
profName = input("Input Professor Name \n")
downloaded = input("Pictures already downloaded? (y/n)") #This option saves time if you're querying the same professor later

pygame.init()
size = width, height = 750, 700

screen = pygame.display.set_mode(size, pygame.RESIZABLE)
myFont = pygame.font.SysFont("timesnewroman", 18)

menuRect = pygame.Rect(0,0,screen.get_width(),40)
menuRectDraw = pygame.draw.rect(screen, (90,90,90),menuRect)

menuInfo = myFont.render("Left Arrow - Prev Page | 1 - Filter By Longest | 2 - Big | Right Arrow - Next Page", 1, (255,255,255))


landingPage = "http://website not public.org/?s=" + profName
pageRequest = requests.get(landingPage)
pageHTML = pageRequest.text
soup = BeautifulSoup(pageHTML, 'html.parser')

pageLinkURLs = []   #List of links to each page

totalPages = getTotalPages(pageHTML) #Total number of pages in the given search

choice = 0
if(totalPages > 5):
    choice = input(str(totalPages) + " Pages found. How many should be searched (0 for all): ")
    choice = int(choice)
    if(choice != 0):
        totalPages = choice

imageListURLs = []  #List of the IMAGE URLs
attrList = []       #List of the unformatted lines of attribute text
linkList = []       #List of all of the actual page links for videos
sizeList = []       #List of the video sizes (Format: XX.XX as a string)
durList = []        #List of the video durations (Format: XX:XX:XX as a string)
videoList = []      #Formatted container of Image URLs, (Format: Siz)

imgList = []        #List of the actual image files
imgRectList = []    #List of the image rects
textListDur = []    #List of the text duration for each video
textListSize = []   #List of the text size for each video

imgRectListFiltered = []    #Sorted version of rectList
videoListFiltered = []      #Sorted version of videoList
imgListFiltered = []        #Sorted version of imgList
textListDurFiltered = []    #Sorted version of textListDur
textListSizeFiltered = []   #Sorted version of textListDur

#Fill a list with links to all pages, excludes the landing page
generatePageLinks(totalPages, pageLinkURLs, profName)

#These variables are used to monitor whether or not inaccurate data was received
#If they are not all equal at the end of the coming loop, something went wrong
totalCountAttr = 0
totalCountSize = 0
totalCountDur = 0
totalCountVideo = 0
totalCountLink = 0
totalCountList = 0

#Parse the landing page first
getPageData(soup, imageListURLs, attrList, linkList)
totalCountAttr += len(attrList)
totalCountLink += len(linkList)
totalCountList += len(imageListURLs)

#Get the attributes of the landing page
parseAttrList(attrList, sizeList, durList)
totalCountSize += len(sizeList)
totalCountDur += len(durList)

#Build first set of video objects
populateVideoList(videoList, imageListURLs, sizeList, durList, linkList)

completePages = 0
currentPage = ""
while(completePages < totalPages - 1):
    print("PAGE PARSED")
    currentPage = pageLinkURLs[completePages]
    pageRequest = requests.get(currentPage)
    pageHTML = pageRequest.text
    soup = BeautifulSoup(pageHTML, 'html.parser')

    #Generate lists of images and attributes using a given HTML container (soup)
    getPageData(soup, imageListURLs, attrList, linkList)
    #Get the counts of these lists for comparison later
    totalCountAttr += len(attrList)
    totalCountLink += len(linkList)
    totalCountList += len(imageListURLs)

    #Turn the raw attrList data into sizeList and durList lists
    parseAttrList(attrList, sizeList, durList)
    #Get the counts of these lists for comparison later
    totalCountSize += len(sizeList)
    totalCountDur += len(durList)

    #Fill the videoList with info from several containers
    populateVideoList(videoList, imageListURLs, sizeList, durList, linkList)
    completePages = completePages + 1

#-------------------------------------------------------------------------------------#
totalCountVideo = len(videoList)

if(totalCountSize != totalCountVideo):
    print("WARNING, VIDEO SIZES POTENTIALLY INCORRECT" + str(totalCountSize) +" vs " + str(totalCountVideo))
if(totalCountDur != totalCountVideo):
    print("WARNING, VIDEO DURATIONS POTENTIALLY INCORRECT")
if(totalCountAttr != totalCountVideo):
    print("WARNING, ATTRIBUTES POTENTIALLY INCORRECT")
if(totalCountLink != totalCountVideo):
    print("WARNING, LINKS POTENTIALLY INCORRECT")
if(totalCountList != totalCountVideo):
    print("WARNING, IMAGES POTENTIALLY INCORRECT")

totalImagesCollected = totalCountList

if(downloaded != "y"):
    for videoNum, video in enumerate(videoList):
        path = "-image directory-" + str(videoNum) +".jpg"
        urllib.request.urlretrieve(video.image,path)
        print(str(videoNum) + "/" + str(totalImagesCollected - 1))

#Fill the imgList and imgRectList containers with information regarding images
populateImageAndRectList(imgList, imgRectList, totalImagesCollected)

#Fill text lists with font elements
populateTextLists(videoList, textListDur, textListSize, myFont)

#Organize the x and y attributes of each image
populateWindow(imgRectList, videoList, screen, 0, totalImagesCollected)

filterLists(imgRectList, videoList, imgRectListFiltered, videoListFiltered, imgList, imgListFiltered, textListDur, textListDurFiltered, textListSize, textListSizeFiltered)

currentPage = 0
while 1:
############### EVENTS ############# EVENTS ################################
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

        elif event.type == pygame.VIDEORESIZE: 
            #Update the width and height of the window, and call populateWindow to update image locations
            widthUpdate, heightUpdate = event.size
            screen = pygame.display.set_mode((widthUpdate,heightUpdate), pygame.RESIZABLE)
            populateWindow(imgRectList, videoList, screen, currentPage, totalImagesCollected)
        elif event.type == pygame.MOUSEBUTTONUP: #Mouse clicked, call the processImageClicked function
            pos = event.pos
            imageClicked = clickIndex(pos, imgRectList, screen, currentPage, totalImagesCollected) #Returns the index of the clicked rectangle, -1 if none
            if(imageClicked != -1):
                processImageClicked(imageClicked, videoList)
        elif event.type == pygame.KEYDOWN: #On key down, increment or decrement the page

            if (event.key == pygame.K_LEFT):
                if(currentPage != 0):
                    currentPage = currentPage - 1
                    populateWindow(imgRectList, videoList, screen, currentPage, totalImagesCollected)

            elif(event.key == pygame.K_RIGHT):
                currentPage = currentPage + 1
                populateWindow(imgRectList, videoList, screen, currentPage, totalImagesCollected)

            elif(event.key == pygame.K_1):
                videoList = list(videoListFiltered)
                imgRectList = list(imgRectListFiltered)
                imgList = list(imgListFiltered)
                textListDur = list(textListDurFiltered)
                textListSize = list(textListSizeFiltered)
                populateWindow(imgRectList, videoList, screen, currentPage, totalImagesCollected)
            
            elif(event.key == pygame.K_2):
                screen = pygame.display.set_mode((1490,1025), pygame.RESIZABLE)
                populateWindow(imgRectList, videoList, screen, currentPage, totalImagesCollected)

############### RENDERING ############# RENDERING ################################
    screen.fill((102,102,102)) #Fill the screen background with grey
   
    imagesPerPage = getTotalImagesPerPage(screen)

    #This prints the actual images
    for idx in range (0, imagesPerPage):
        if(idx + (currentPage * imagesPerPage)) < totalImagesCollected:
            screen.blit(imgList[idx + (imagesPerPage * currentPage)], imgRectList[idx + (imagesPerPage * currentPage)])

    setupMenu(menuRect, menuRectDraw, screen)
    screen.blit(menuInfo, (20, 5))
    drawTextLists(textListDur, textListSize, screen, imgRectList, currentPage, totalImagesCollected)

    pygame.display.flip()