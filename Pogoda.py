#author: Marek Mikołajczyk
# Program do pozyskiwanie danych pogodowych, przetrzania nich, zapisywania i otwarzania we włąściwej formie

#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#------------------------Pozyskiwanie danych------------------------------------
from lxml import html
import requests
import re

#Wariant I- Akutualnie pobierane dane
przeszukiwana_strona_1 = requests.get('http://pruszkow.infometeo.pl')
tree_strukura_html = html.fromstring(przeszukiwana_strona_1.content)
wyszukany_zboir_danych =''.join(tree_strukura_html.xpath('/html/body/div/pre/text()'))

                    #wyszukiwane zmienne
temp=int(re.search(r"TEMPERATURA.+\b([0-9][0-9]?)",wyszukany_zboir_danych).group(1))
opady=re.search(r"CHMURY[.]+.([\w.]*.[\w?.]*)",wyszukany_zboir_danych).group(1)

