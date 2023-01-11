'''This script:
 *It opens a URL specified by the user,
  prints the title and the meta description and
  it also prints the URL into a .ini file. 

 *It prints the title and the price of all
  OLX announcements containing the keyword "iphone 14 pro max",
  in ascending order by price.

 *If the "python <filename> -log info" command
  is written in the terminal the program
  also prints the time it takes for each request.

 *It sends an email to "an.email@gmail.com"
  if the price of a specific item gets reduced
  under a target price. 

Functions:
* fileWriter - writes an URL into a .ini file.
* tagSearcher - finds and prints the title
and the description meta of a webpage.
Packages to be installed:
* beautifulsoup4
* configparser
'''
from bs4 import BeautifulSoup
from configparser import ConfigParser
from email.message import EmailMessage
import requests, re, time, logging, ssl, smtplib, argparse



url = input("Enter an URL: ")
file='file.ini'#the .ini file name
config=ConfigParser()
config.read(file)

def fileWriter(url,file):
    '''Function that writes a URL into a .ini file.
    
    Parameters:
    url(string):The url of a webpage
    file(string):The name of a .ini file
    
    '''
    config.set('links','url',url)

    with open(file, 'w')as configfile:
        config.write(configfile)

    
def tagSearcher(url):
    '''Function that finds and prints the title
    and the meta description of a webpage.
     
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


argParser = argparse.ArgumentParser()
argParser.add_argument("-log", "--logging",type=str, help="logging level")#creating a new inline argument for setting the logging level
args = argParser.parse_args()
if args.logging==None:#if there isn't any inline argument specified the logging level is 'warning'
    args.logging='warning'
logging.basicConfig(level=args.logging.upper(),format="request time:%(message)s\n")


config.read(file)
phone=config['key_words']['phone']#extracting the keyword
phone_list='-'.join(phone.split())

url_name=config['key_words']['url']#extracting the url
url=f"http://{url_name}/d/oferte/q-{phone_list}/"


###defining a decorator in order to obtain the time each request needs
def get_time(function):
    def modification(url):
        start=time.time()
        func = function(url)
        end=time.time()
        request_time=end-start#measuring the request time
        logging.info(request_time)
       
        return func
    return modification


@get_time
def get_request(url):#function that sends a request to a sepecific url in order to get the page's html script
    return requests.get(url).text

if args.logging!='warning':#the text is printed only if the logging level is 'info'
    print('The request for the page number:')


###request the first page's html script in order to extract the number of the last page of announcements
page=get_request(url)
doc=BeautifulSoup(page,"html.parser")#containts the page's html script
first_page='1'
div=doc.find(class_="css-j8u5qq")
items=div.find_all('a',text=re.compile(first_page))
max_nr=int(items[0].parent.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.text)#the number of the last page of announcements



####finding and sorting the announcements
items_found={}
counter=0
for pg in range(1,max_nr+1):#this for loop  loops trough all announcements pages 
    if pg==1:
       url=f"http://{url_name}/d/oferte/q-{phone_list}/"
    else:
        url=f"http://{url_name}/d/oferte/q-{phone_list}/?page={pg}"

    if args.logging!='warning':#the text is printed only if the logging level is 'info'
        print(f'The request for page {pg}:')
    page=get_request(url)
   
    doc=BeautifulSoup(page,"html.parser")#finding the announcements that contain the keyword
    div=doc.find(class_="css-pband8")
    items=div.find_all(text=re.compile(phone))
  
    
    for item in items:#this for loop loops trough a list of suitable announcements
        price=item.parent.next_sibling.text#the text containing the price
        price_comp=price.split()
        price_list=[]
        for elm in price_comp:
            if elm.isalpha()!=1:
                price_list.append(elm)#creating a list that contains only the numeric text from 'price'
        
        price_string=''    
        for elm in price_list:
            price_string=price_string+elm
        if price_string=='':#if the price is an empty string it jumps to the next item
            continue
        
        counter=counter+1
        price_int=int(float(price_string.replace(",99","")))#replacing the unwanted parts of the price
        items_found[counter]={"title":item,"price":price_int}#creating a dictionary containing the item's title and price

sorted_items = sorted(items_found.items(), key = lambda x: x[1]['price'])#sorting the dictionary

for item in sorted_items:#printing the results
    print(item[1]['title'])
    print(f"{item[1]['price']} lei\n")
    

###implementing a functionality that sends an email if the price of a specific item is reduced under a target price
target=config['prices']['target_price']#a target price extracted from a .ini file
wished_phone=input('Which phone do you want?(enter a title from the list above) ')

for item in sorted_items:
    if wished_phone==item[1]['title'].text:#condition to find the right item
        wished_phone_price=item[1]['price']

       
if int(target)<wished_phone_price:
    print(f"The item's ({wished_phone}) price ({wished_phone_price} lei) is higher than {target} lei")
else:
    email_sender=config['email']['email']#an email(sender's email)
    email_password=''#a password

    email_receiver=''#an email(receiver's email)


    subject="Price change"
    body=f""" The phone's price is finally lowwer than {target} lei"""

    em=EmailMessage()
    em['Form']=email_sender
    em['To']=email_receiver
    em['subject']=subject
    em.set_content(body)

    context=ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com',465, context=context) as smtp:
        smtp.login(email_sender,email_password)
        smtp.sendmail(email_sender,email_receiver,em.as_string())
    
    print("An email has been sent to 'an.email@gmail.com'.")
