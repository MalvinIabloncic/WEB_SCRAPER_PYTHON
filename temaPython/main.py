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
import re

#url = input("Enter a URL: ")
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

#tagSearcher(url)
#fileWriter(url,file)

phone="iphone 14 pro max"
phone_list=phone.split()

url_name="olx.ro"
url=f"http://{url_name}/d/oferte/q"
for phn in phone_list:
    url=url+'-'+phn
url=url+'/'

page=requests.get(url).text
doc=BeautifulSoup(page,"html.parser")

first_page='1'
div=doc.find(class_="css-j8u5qq")
items=div.find_all('a',text=re.compile(first_page))
max_nr=int(items[0].parent.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.text)

items_found={}
counter=0
for pg in range(1,max_nr+1):
    if pg==1:
       url=f"http://{url_name}/d/oferte/q-iphone-14-pro-max/"
    else:
        url=f"http://{url_name}/d/oferte/q-iphone-14-pro-max/?page={pg}"
        page=requests.get(url).text
        doc=BeautifulSoup(page,"html.parser")

        div=doc.find(class_="css-pband8")
        items=div.find_all(text=re.compile(phone))
  
    
        for item in items:
            price=item.parent.next_sibling.text
            price_comp=price.split()
            price_list=[]
            for elm in price_comp:
                if elm.isalpha()!=1:
                    price_list.append(elm)
        
            price_string=''    
            for elm in price_list:
                price_string=price_string+elm
            counter=counter+1
        
            items_found[counter]={"title":item,"price":int(price_string.replace(",99",""))}

sorted_items = sorted(items_found.items(), key = lambda x: x[1]['price'])

for item in sorted_items:
    print(item[1]['title'])
    print(item[1]['price'])


