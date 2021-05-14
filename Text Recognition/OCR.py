import pytesseract
import cv2
#import pandas as pd
from PIL import Image
from bs4 import BeautifulSoup
import requests
import re
from csv import DictWriter
import os
import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText

def ocr():
    font_scale = 1.5
    font = cv2.FONT_HERSHEY_PLAIN

    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise IOError('No webcam found')

    cntr = 0
    while True:
        ret,frame = cap.read()
        cntr += 1
        if((cntr%20) == 0):
            imgH,imgW,_ = frame.shape
            x1,y1,w1,h1 = 0,0,imgH,imgW

            img1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            file = open("recognized.txt", "w")
            imgchar = pytesseract.image_to_string(Image.fromarray(img1))
            imgboxes = pytesseract.image_to_boxes(frame)
            for boxes in imgboxes.splitlines():
                boxes = boxes.split(' ')
                x,y,w,h = int(boxes[1]),int(boxes[2]),int(boxes[3]),int(boxes[4])
                cv2.rectangle(frame,(x,imgH-y),(w,imgH-h),(0,0,225),3)

            cv2.putText(frame, imgchar, (x1 + int(w1/50), y + int(h1/50)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (225,0,0), 3)
            font = cv2.FONT_HERSHEY_SIMPLEX
            file.write(imgchar)
            file.close

            cv2.imshow('Text Detection', frame)
            if cv2.waitKey(2) & 0XFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
ocr()

with open('recognized.txt', 'r') as txt:
  li = txt.readlines()
res1 = []
res = []
product_string = ''
for ele in li:
  if ele.strip():
    res += ele.split(' ')
    #res.append(ele)
alpha  = 'QWERTYUIOPASDFGHJKLZXCVBNMqwertyuiopasdfghjklzxcvbnm'
for i in res:
  if i[0] in alpha and len(i) > 3:
    res1.append(i.rstrip())
print(res1)
  

if os.path.exists("productlist.csv"):
  os.remove("productlist.csv")
else:
  print("")
if os.path.exists("productlistone.csv"):
  os.remove("productlistone.csv")
else:
  print("")


def edamam_food_api():       
    url = "https://edamam-food-and-grocery-database.p.rapidapi.com/parser"
    for i in range(0, len(res1)):
        querystring = {}
        querystring['ingr'] = res1[i]

        headers = {
            'x-rapidapi-key': "19b3910850msheea1657a388e270p168743jsn232d02dddfa9",
            'x-rapidapi-host': "edamam-food-and-grocery-database.p.rapidapi.com"
            }

        r = requests.request("GET", url, headers=headers, params=querystring)
        products = r.json()
        if(products['hints'] == []):
                continue
        else:
            print('\n')
            name = products['hints'][0]['food']['label']
            print(f'Name : {name} \n')
            nutrients = products['hints'][0]['food']['nutrients']
            for nutri in nutrients:
                print(f'{nutri} : {nutrients[nutri]}')

            key_to_lookup = 'foodContentsLabel'
            if key_to_lookup in products['hints'][0]['food']:
                contents = products['hints'][0]['food']['foodContentsLabel']
                print(f'Contents : {contents}')
            else:
                print("")

def calories_ninja():
    for i in range(0,len(res1)):
        url = "https://calorieninjas.p.rapidapi.com/v1/nutrition"

        querystring = {}
        querystring['query'] = res1[i].lower().title()

        headers = {
            'x-rapidapi-key': "19b3910850msheea1657a388e270p168743jsn232d02dddfa9",
            'x-rapidapi-host': "calorieninjas.p.rapidapi.com"
            }

        response = requests.request("GET", url, headers=headers, params=querystring)
        product = response.json()
        if product['items'] == []:
            continue
        else:
            item = product['items'][0]
            print('\n')
            item1 = item['name']
            print(f'Product = {item1} \n')
            for pro in item:
                print(f'{pro} : {item[pro]}')
            print('\n')


def wiki_translate():
    import urllib as url
    from googletrans import Translator

    translator = Translator()
    lan = input("Enter language : ")

    for i in range(0,len(res1)):
        print(res1[i])
        try:
            link = ("https://en.wikipedia.org/wiki/{}".format(res1[i].lower()))
            page = url.request.urlopen(link).read() 
            soup = BeautifulSoup(page, 'lxml')
            text = ''
            for para in soup.find_all('p'):
                text += para.text
                text = re.sub(r'\[[0-9]*\]',' ',text)
                text = re.sub(r'\s+',' ',text)
                txt = text.split('.')
                deets = txt[:5]

            if lan == "english": 
                print(deets,'\n')
            else:
                if lan == "hindi": 
                    translations = translator.translate(deets, dest='hi')

                if lan == "spanish": 
                    translations = translator.translate(deets, dest='es')

                if lan == "french": 
                    translations = translator.translate(deets, dest='fr')

                if lan == "german": 
                    translations = translator.translate(deets, dest='ge')

                if lan == "japanese": 
                    translations = translator.translate(deets, dest='ja')

                for translation in translations:
                        print(translation.text)
                print('\n')
        except:
            print("")


edamam_food_api()
calories_ninja()
wiki_translate()


#for i in range(0, len(res1)):
link = ("https://www.flipkart.com/search?q={}".format(res1[0].lower()))
response = requests.get(link)
soup = BeautifulSoup(response.text, 'lxml')
cards = soup.find_all('div', {"class":"_4ddWXP"})

product_list = []
for card in cards:
    data_dict = {}
    data_dict['PRODUCTS'] = card.find('a',{"class":"s1Q9rs"}).text.strip()
    data_dict['PRICE'] = card.find('div',{"class":"_30jeq3"}).text.replace('₹','').strip()
    if card.find('div',{"class":"_3LWZlK"}) == None:
        continue
    else:
        data_dict['RATING'] = card.find('div',{"class":"_3LWZlK"}).text.strip()
        product_list.append(data_dict)
    with open('productlist.csv', 'a') as f_object:
        field_names = ['PRODUCTS','PRICE','RATING']
        dictwriter_object = DictWriter(f_object, fieldnames = field_names)
        dictwriter_object.writerow(data_dict)
        f_object.close()

try:
  link = ("https://www.flipkart.com/search?q={}".format(res1[1].lower()))
  response = requests.get(link)
  soup = BeautifulSoup(response.text, 'lxml')
  cards = soup.find_all('div', {"class":"_4ddWXP"})
  
  product_list = []
  for card in cards:
      data_dict = {}
      data_dict['PRODUCTS'] = card.find('a',{"class":"s1Q9rs"}).text.strip()
      data_dict['PRICE'] = card.find('div',{"class":"_30jeq3"}).text.replace('₹','').strip()
      if card.find('div',{"class":"_3LWZlK"}) == None:
          continue
      else:
          data_dict['RATING'] = card.find('div',{"class":"_3LWZlK"}).text.strip()
          product_list.append(data_dict)
      with open('productlistone.csv', 'a') as f_object:
          field_names = ['PRODUCTS','PRICE','RATING']
          dictwriter_object = DictWriter(f_object, fieldnames = field_names)
          dictwriter_object.writerow(data_dict)
          f_object.close()
except:
  print(" ")
  
#mailing the .csv files  
emailfrom = "productlistt@gmail.com"
emailto = input("Enter email address: ")
fileToSendOne = "productlist.csv"
fileToSendTwo = "productlistone.csv"
username = "productlistt@gmail.com"
password = "qwerty!@#123"

msg = MIMEMultipart()
msg["From"] = emailfrom
msg["To"] = emailto
msg["Subject"] = "Similar Products"
msg.preamble = "Hey User! Here is the list of products you searched: "
body = 'Hey User! Here is the list of products you searched:'
body = MIMEText(body)
msg.attach(body)

ctype, encoding = mimetypes.guess_type(fileToSendOne)
if ctype is None or encoding is not None:
    ctype = "application/octet-stream"

maintype, subtype = ctype.split("/", 1)

if maintype == "text":
    fp = open(fileToSendOne)
    attachment = MIMEText(fp.read(), _subtype=subtype)
    fp.close()
else:
    fp = open(fileToSendOne, "rb")
    attachment = MIMEBase(maintype, subtype)
    attachment.set_payload(fp.read())
    fp.close()
    encoders.encode_base64(attachment)
attachment.add_header("Content-Disposition", "attachment", filename=fileToSendOne)
msg.attach(attachment)

if os.path.exists("productlistone.csv"):
  ctype, encoding = mimetypes.guess_type(fileToSendTwo)
  if ctype is None or encoding is not None:
      ctype = "application/octet-stream"
  
  maintype, subtype = ctype.split("/", 1)
  
  if maintype == "text":
      fp = open(fileToSendTwo)
      attachment = MIMEText(fp.read(), _subtype=subtype)
      fp.close()
  else:
      fp = open(fileToSendTwo, "rb")
      attachment = MIMEBase(maintype, subtype)
      attachment.set_payload(fp.read())
      fp.close()
      encoders.encode_base64(attachment)
  attachment.add_header("Content-Disposition", "attachment", filename=fileToSendTwo)
  msg.attach(attachment)
else:
  print("")

server = smtplib.SMTP("smtp.gmail.com:587")
server.starttls()
server.login(username,password)
server.sendmail(emailfrom, emailto, msg.as_string())
server.quit()