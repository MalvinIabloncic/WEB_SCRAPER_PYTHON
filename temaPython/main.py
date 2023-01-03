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
import requests, re, time, logging, ssl, smtplib, argparse
from email.message import EmailMessage


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
argParser = argparse.ArgumentParser()
argParser.add_argument("-log", "--logging",type=str, help="logging level")
args = argParser.parse_args()


if args.logging==None:
    args.logging='warning'

logging.basicConfig(level=args.logging.upper(),format="request time:%(message)s\n")


config=ConfigParser()
config.read(file)

phone=config['key_words']['phone']
phone_list='-'.join(phone.split())


url_name=config['key_words']['url']
url=f"http://{url_name}/d/oferte/q-{phone_list}/"

def get_time(function):
    def modification(url):
        start=time.time()
        func = function(url)
        end=time.time()
        request_time=end-start
        logging.info(request_time)
       
        return func
    return modification

@get_time
def get_request(url):
    return requests.get(url).text

if args.logging!='warning':
    print('The request for the page number:')
page=get_request(url)

doc=BeautifulSoup(page,"html.parser")

first_page='1'
div=doc.find(class_="css-j8u5qq")
items=div.find_all('a',text=re.compile(first_page))
max_nr=int(items[0].parent.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.next_sibling.text)

items_found={}
counter=0
for pg in range(1,max_nr+1):

    if pg==1:
       url=f"http://{url_name}/d/oferte/q-{phone_list}/"
    else:
        url=f"http://{url_name}/d/oferte/q-{phone_list}/?page={pg}"
    if args.logging!='warning':
        print(f'The request for page {pg}:')
    page=get_request(url)
   
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
        if price_string=='':
            continue
        
        counter=counter+1
        price_int=int(float(price_string.replace(",99","")))
        items_found[counter]={"title":item,"price":price_int}

sorted_items = sorted(items_found.items(), key = lambda x: x[1]['price'])

for item in sorted_items:
    print(item[1]['title'])
    print(f"{item[1]['price']} lei")
    print("")


target=config['prices']['target_price']


if int(target)<item[1]['price']:
    print(f"The item's ({item[1]['title']}) price ({item[1]['price']} lei) is bigger than {target} lei")
else:
    email_sender=config['email']['email']#an email(sender's email)
    email_password=''#a password

    email_receiver=''#an email(receiver's email)


    subject="Price change"
    body=f""" The phone's price is finally smaller then {target} lei"""

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
