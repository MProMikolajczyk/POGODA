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
        self.strona_n1={'http://pruszkow.infometeo.pl':'/html/body/div/pre/text()'}

#--------Wariant_1-------
    def przeszukiwana_strona(self):
        for strona in self.strona_n1:
            wybrana_strona=self.requests.get(strona)
            html_content=self.html.fromstring(wybrana_strona.content)
            stuktura_html=''.join(html_content.xpath(self.strona_n1[strona]))
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
    import datetime


    def __init__(self):
        self.nazwy_kolumn=["TEMPERATURA","OPAD","DATA","CZAS","ID"]
        self.link = list(self.odczyt_danych_z_wierszy())


    #dopisywanie
    def dopisanie_do_pliku_log(self,dane_1,dane_2):
        with open("pogoda_data.csv" , "a", newline="", encoding='utf-8') as csvfile:
            write =self.csv.DictWriter(csvfile, fieldnames=self.nazwy_kolumn)
            write.writerow({"TEMPERATURA": dane_1, "OPAD":dane_2,"DATA":self.datetime.datetime.now().strftime('%Y-%m-%d'),"CZAS":self.datetime.datetime.now().strftime('%H:%M:%S')})

    def dopisanie_do_pliku_sort(self):
        with open("pogoda_data_sort.csv", "a", newline="", encoding='utf-8') as csvfile:
            write = self.csv.DictWriter(csvfile, fieldnames=self.nazwy_kolumn)
            godz = self.datetime.timedelta(hours=0)
            while godz < self.datetime.timedelta(hours=24):
                for ID in range(0, 96):
                    write.writerow({"DATA": self.datetime.datetime.now().strftime('%Y-%m-%d'), "CZAS": godz, "ID": ID})
                    godz += self.datetime.timedelta(minutes=15)

    #wyswietlanie danych
    def wyswietlanie_danych(self):
        for wyswietl in self.link:
            print(wyswietl)

    #operacje na kolumnach
    def odczyt_danych_z_kolumn(self,nr_kolumny=True):
        with open("pogoda_data.csv", "r") as csvfile:
            reader =self.csv.DictReader(csvfile)
            for row in reader:
                yield(row[self.nazwy_kolumn[nr_kolumny]])


    def zakres_kolumn(self,start=0, finish=True,nr_kolumny=True): #wyniki od start do finish z dla nr kolumny
        zakres = list(self.odczyt_danych_z_kolumn(nr_kolumny))
        for wiersz in range(start, finish):
            yield zakres[wiersz]

    #operacje na wierszach
    def odczyt_danych_z_wierszy(self):
        with open("pogoda_data.csv", "r") as csvfile:
            reader =self.csv.DictReader(csvfile)
            for row in reader:
                    yield row

    def zakres_wierszy(self,start=0, finish=True): #wyniki od start do finish dla wszystkich wierszy
        zakres = list(self.odczyt_danych_z_wierszy())
        for wiersz in range(start, finish):
            yield zakres[wiersz]


#----------------------------------Główna zawartość---------------------------
from time import sleep
def main():
    pozyskiwane_dane = Pozyskiwane_dane()
    operacje_na_plikach = Operacje_na_plikach()
    while True:
        #wyświetla utualną temoeraturę i opady co 15min
        print(pozyskiwane_dane.akutualna_temp())
        print(pozyskiwane_dane.aktualne_opady())
        operacje_na_plikach.dopisanie_do_pliku_log(pozyskiwane_dane.akutualna_temp(),pozyskiwane_dane.aktualne_opady())
        operacje_na_plikach.dopisanie_do_pliku_sort()
        sleep(900)
            #print(list(operacje_na_plikach.odczyt_danych_z_kolumn(0)))

main()
