#author: Marek Mikołajczyk
# Program do pozyskiwanie danych pogodowych, przetrzania nich, zapisywania i otwarzania we włąściwej formie

#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#------------------------Pozyskiwanie danych------------------------------------
class Pozyskiwane_dane(object):

    from lxml import html
    import requests
    import re


    def __init__(self):
        self.strony={'http://pruszkow.infometeo.pl':'/html/body/div/pre/text()'}

#--------Wariant_1-------
    def przeszukiwana_strona(self):
        for strona in self.strony:
            wybrana_strona=self.requests.get(strona)
            html_content=self.html.fromstring(wybrana_strona.content)
            stuktura_html=''.join(html_content.xpath(self.strony[strona]))
            return stuktura_html

    def akutualna_temp(self):
        try:
            temp=self.re.search(r"TEMPERATURA.+\b([0-9][0-9]?)",self.przeszukiwana_strona()).group(1)
            return temp
        except:
            temp='Brak danych'
            return temp


    def aktualne_opady(self):
        try:
            opady=self.re.search(r"WARUNKI[.]+.([\w.]*.[\w?.]*.[\w?.]*.[\w?.]*.[\w?.]*.[\w?.]*)",self.przeszukiwana_strona()).group(1)
            return opady
        except:
            opady='Brak danych'
            return opady

#--------Wariant_2-------
'''
Gdy nie pobiera danych to ma sobie je sam uzupełnić 
'''
#------------------Zapisywanie i otczytywanie pliku---------------------------
class Operacje_na_plikach(object):

    import csv
    from datetime import datetime

    def __init__(self):
        self.nazwy_kolumn=["TEMPERATURA","OPAD","DATA","CZAS"]

    def dopisanie_do_pliku(self,dane_1,dane_2):
        with open("pogoda_data.csv" , "a", newline="", encoding='utf-8') as csvfile:
            write =self.csv.DictWriter(csvfile, fieldnames=self.nazwy_kolumn)
            write.writerow({"TEMPERATURA": dane_1, "OPAD":dane_2,"DATA":self.datetime.now().strftime('%Y-%m-%d'),"CZAS":self.datetime.now().strftime('%H:%M:%S')})

    def oczytywanie_pliku(self):
        with open("pogoda_data.csv", "r") as csvfile:
            reader =self.csv.DictReader(csvfile)
            for row in reader:
                print(row)

    def odczyt_danych_z_kolumn(self,nr_kolumny):
        with open("pogoda_data.csv", "r") as csvfile:
            reader =self.csv.DictReader(csvfile)
            for row in reader:
                yield(row[self.nazwy_kolumn[nr_kolumny]])

#----------------------------------Główna zawartość---------------------------
from time import sleep
def main():
    pozyskiwane_dane = Pozyskiwane_dane()
    operacje_na_plikach = Operacje_na_plikach()
    while True:
        #wyświetla utualną temoeraturę i opady co 15min
        print(pozyskiwane_dane.akutualna_temp())
        print(pozyskiwane_dane.aktualne_opady())
        operacje_na_plikach.dopisanie_do_pliku(pozyskiwane_dane.akutualna_temp(),pozyskiwane_dane.aktualne_opady())
        sleep(900)
            #print(list(operacje_na_plikach.odczyt_danych_z_kolumn(0)))

main()
