'''This script opens a URL specified by the user,
prints the title and the description meta and
it also prints the URL into a .ini file.

Functions:
* fileWriter - writes a URL into a .ini file.
* tagSearcher - finds and prints the title
and the description meta of a webpage.

Packages to be installed:
* beautifulsoup4
* configparser

'''
from bs4 import BeautifulSoup
from configparser import ConfigParser
import requests


url = input("Enter a URL: ")
file='file.ini'

def fileWriter(url,file):
    '''Function that writes a URL into a .ini file.
    
    Parameters:
    url(string):The url of a webpage
    file(string):The name of a .ini file
    
    '''
    config=ConfigParser()
    config.add_section('links')
    config.set('links','URL',url)
    with open(file, 'w')as configfile:
       config.write(configfile)

def tagSearcher(url):
    '''Function that finds and prints the title
    and the description meta of a webpage.
     
    Parameters:
    url(string):The url of a webpage
     
    '''
    result=requests.get(url)
    soup = BeautifulSoup(result.text, 'html.parser')
    tag1=soup.title
    tag2=soup.meta
    print(tag1,tag2)

tagSearcher(url)
fileWriter(url,file)

#Terminal#
#Enter a URL: https://github.com/
#<title>GitHub: Let’s build from here · GitHub</title> <meta charset="utf-8"/>
