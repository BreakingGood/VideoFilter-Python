# VideoFilter-Python
Filters and sorts lecture videos for a lectuerer that did not provide those options.

# Purpose

This program is designed to scrape a particular website using the BeautifulSoup Python library https://www.crummy.com/software/BeautifulSoup/. 
It then parses the HTML in such a way that particular attributes regarding this lectuerer's videos could be more easily sorted and filtered.

Sorting options include filtering by video length, video file size, and the video size:length ratio. 

After the parsing is complete, the videos are displayed in a window using the PyGame library https://www.pygame.org.
This library is used to handle all mouse/keyboard inputs as well as reading and displaying .png image files. 
