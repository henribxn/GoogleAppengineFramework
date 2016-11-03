from bs4 import BeautifulSoup as bs
import requests
import re

r= requests.get('https://www.operadeparis.fr/billetterie/recherche?date=2016-11-11&price=1&genre=0&venue=0')
#print r
#print r.text

markup = r.text
soup = bs(markup,"html.parser")
#f = open("example.txt", "w")
#f.write(soup.get_text())
#f.close()

mydivs = soup.findAll("p", { "class" : "light-text" })
re.findall(mydivs,)

