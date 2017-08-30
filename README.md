# VideoFilter-Python
Filters and sorts lecture videos for a lectuerer that did not provide those options.

# Purpose

This program is designed to scrape a particular website using the BeautifulSoup Python library https://www.crummy.com/software/BeautifulSoup/. 
It then parses the HTML in such a way that particular attributes regarding this lectuerer's videos could be more easily sorted and filtered.

Sorting options include filtering by video length, video file size, and the video size:length ratio. 

After the parsing is complete, the videos are displayed in a window using the PyGame library https://www.pygame.org.
This library is used to handle all mouse/keyboard inputs as well as reading and displaying .png image files. 

PyGame was found to be insufficient to complete my end goal for this project and so a newer version of this project was produced
using C++ to display the UI and handle inputs, while leaving the original Python script and BeautifulSoup up to scraping and parsing the 
website HTML. The new version is available here https://github.com/BreakingGood/VideoFilter-CppFrontEnd
