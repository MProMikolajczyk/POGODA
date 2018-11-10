#author: Marek Mikołajczyk
# Program do pozyskiwanie danych pogodowych, przetrzania nich, zapisywania i otwarzania we właściwej formie

#!/usr/bin/env python3
#-*- coding: utf-8 -*-

#------------------------D1.Pozyskiwanie danych------------------------------------
class Pozyskiwane_dane():

    from lxml import html
    import requests
    import re

    def __init__(self):
        self.strona_n1 = {'http://pruszkow.infometeo.pl':'/html/body/div/pre/text()'}
        self.strona_n2 = {'https://pogoda.interia.pl/archiwum-pogody-{day}-{mc}-{year},cId,27670'.format(day=dzien, mc=miesiac, year=rok): \
                              '/html/body/div/div/div/section/div/div/div/div/div/div/span/span/text()'}
        self.strona_n3 = {'https://pogoda.interia.pl/archiwum-pogody-{day}-{mc}-{year},cId,27670'.format(day=dzien, mc=miesiac, year=rok): \
                              '/html/body/div/div/div/section/div/div/div/div/div/div/text()'}
        self.nr_strony = [self.strona_n1, self.strona_n2,self.strona_n3]

    #----------------------------Wariant_1-------------------------------------

    def przeszukiwana_strona(self, nr_strony=0):
        for strona in self.nr_strony[nr_strony]:
            wybrana_strona=self.requests.get(strona)
            html_content=self.html.fromstring(wybrana_strona.content)
            stuktura_html=''.join(html_content.xpath(self.nr_strony[nr_strony][strona]))
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

    #---------------------------Wariant_2------------------------------------

    def temeratura_archiwalna(self):
        try:
            temp_arch = self.re.findall(r"[0-9]°COdczuwalna.([0-9][0-9]?)", self.przeszukiwana_strona(1))
            return temp_arch
        except:
            temp_arch='Brak'
            return temp_arch

    def opad_archiwalny(self):
        try:
            opad_arch = self.re.findall(r"[0-9][0-9]?°COdczuwalna.[0-9][0-9]?°C.([A-Z][a-zżźćńółęąś]*\s?[a-zżźćńółęąś?]*)[\w]*",self.przeszukiwana_strona(1))
            wilgotnosc_arch = self.re.findall(r"([0-9][0-9])", self.przeszukiwana_strona(2))
            for nr_poz in range(len(opad_arch)):
                if opad_arch[nr_poz] == 'Zachmurzenie duże' and wilgotnosc_arch[nr_poz] >= '98':
                    opad_arch[nr_poz] = "słaby deszcz"
            return opad_arch
        except:
            opad_arch='Brak danych'
            return opad_arch

#------------------D2.Zapisywanie i otczytywanie plikow---------------------------
class Operacje_na_plikach(object):

    import csv
    import datetime


    def __init__(self):
        self.nazwy_kolumn=["TEMPERATURA","OPAD","DATA","CZAS","ID"]
        self.pliki = ["pogoda_data.csv","pogoda_data_sort.csv","pogoda_data_log_archiwalny.csv"]


#---------------Tworzenie plikuów + uzupełnianie podstawowymi danymi--------------

    #---------------------plik log------------------------------------------------

    def dopisanie_do_pliku_log(self,dane_1,dane_2,nr_pliku=0,):
        with open(self.pliki[nr_pliku], 'r') as readfile:
            reader = self.csv.reader(readfile)
            lines = list(reader)
            if lines == []:
                with open(self.pliki[nr_pliku], "w", newline="", encoding='utf-8') as csvfile:
                    write = self.csv.DictWriter(csvfile, fieldnames=self.nazwy_kolumn)
                    write.writeheader()
                self.dopisanie_do_pliku_log_append(dane_1,dane_2)
            else:
                self.dopisanie_do_pliku_log_append(dane_1,dane_2)

    def dopisanie_do_pliku_log_append(self,dane_1,dane_2,nr_pliku=0):
        with open(self.pliki[nr_pliku], "a", newline="", encoding='utf-8') as csvfile:
            write = self.csv.DictWriter(csvfile, fieldnames=self.nazwy_kolumn)
            write.writerow({"TEMPERATURA": dane_1,
                             "OPAD": dane_2,
                             "DATA": self.datetime.datetime.now().strftime('%Y-%m-%d'),
                             "CZAS": self.datetime.datetime.now().strftime('%H:%M:%S')})

    # ---------------------plik log archiwalny------------------------------------------------

    def dopisanie_do_pliku_log_archiwalny(self,dane_1,dane_2,nr_pliku=2):
        with open(self.pliki[nr_pliku], 'r') as readfile_empty:
            reader_empty = self.csv.reader(readfile_empty)
            lines_empty = list(reader_empty)
            if lines_empty == []:
                with open(self.pliki[nr_pliku], "w", newline="", encoding='utf-8') as csvfile:
                    write = self.csv.DictWriter(csvfile, fieldnames=self.nazwy_kolumn)
                    write.writeheader()
                self.dopisanie_do_pliku_log_archiwalny_append(dane_1, dane_2)
            else:
                self.dopisanie_do_pliku_log_archiwalny_append(dane_1,dane_2)

    def dopisanie_do_pliku_log_archiwalny_append(self,dane_1,dane_2,nr_pliku=2):
        with open(self.pliki[nr_pliku], 'r') as readfile:
            reader = self.csv.reader(readfile)
            lines = list(reader)
            uzyta_data=set()
        with open(self.pliki[nr_pliku], "a", newline="", encoding='utf-8') as csvfile:
            write = self.csv.DictWriter(csvfile, fieldnames=self.nazwy_kolumn)
            godz = self.datetime.datetime(int(rok), int(miesiac), int(dzien), 0, 0)
            poz = 0
            while godz <= self.datetime.datetime(int(rok), int(miesiac), int(dzien), 23, 59) and poz <= 24:
                for data_plik_arch in range(len(lines)):
                    uzyta_data.add(lines[data_plik_arch][2])
                for ID in range(0, 24):
                    if '{year}-{mc}-{day}'.format(year=rok, mc=miesiac, day=dzien) not in uzyta_data:
                        write.writerow({"TEMPERATURA": dane_1[poz],
                                         "OPAD": dane_2[poz],
                                         "DATA": godz.strftime('%Y-%m-%d'),
                                         "CZAS": godz.strftime('%H:%M:%S'), "ID": ID})
                        godz += self.datetime.timedelta(hours=1)
                        poz += 1
                    else:
                        return readfile

    # ---------------------plik sort------------------------------------------------

    def dopisanie_do_pliku_sort(self,nr_pliku=1):
        with open(self.pliki[nr_pliku], 'r') as readfile_empty:
            reader_empty = self.csv.reader(readfile_empty)
            lines_empty = list(reader_empty)
            if lines_empty == []:
                with open(self.pliki[nr_pliku], "w", newline="", encoding='utf-8') as csvfile:
                    write = self.csv.DictWriter(csvfile, fieldnames=self.nazwy_kolumn)
                    write.writeheader()
                self.dopisanie_do_pliku_sort_append()
            else:
                self.dopisanie_do_pliku_sort_append()

    def dopisanie_do_pliku_sort_append(self,nr_pliku=1):
        with open(self.pliki[nr_pliku], 'r') as readfile:
            reader = self.csv.reader(readfile)
            lines = list(reader)
            uzyta_data = set()
        with open(self.pliki[nr_pliku], "a", newline="", encoding='utf-8') as csvfile:
            write = self.csv.DictWriter(csvfile, fieldnames=self.nazwy_kolumn)
            godz = self.datetime.datetime(2018, 11, 5, 0, 0)
            while godz <= self.datetime.datetime.now().combine(self.datetime.datetime.today().date(),
                                                               self.datetime.time(23, 59, 59)):
                for data_plik_sort in range(len(lines)):
                    uzyta_data.add(lines[data_plik_sort][2])
                for ID in range(0, 96):
                    if self.datetime.datetime.today().strftime('%Y-%m-%d') not in uzyta_data:
                        write.writerow({"DATA": godz.strftime('%Y-%m-%d'),
                                        "CZAS": godz.strftime('%H:%M:%S'),
                                        "ID": ID})
                        godz += self.datetime.timedelta(minutes=15)
                    else:
                        return readfile

    def reset_plik_sort_czyszczenie_zawartosci(self,nr_pliku=1):
        with open(self.pliki[nr_pliku], "w", newline="", encoding='utf-8') as csvfile:
            write = self.csv.DictWriter(csvfile, fieldnames=self.nazwy_kolumn)
            write.writeheader()

# ---------------------Nadpisywanie plików danymi ---------------------------------

        #--------------------------plik sort--------------------------------------------

    def nadpisywanie_aktualnym_danymi_plik_sort(self,nr_pliku=1):
        with open(self.pliki[nr_pliku], 'r') as readfile:
            reader = self.csv.reader(readfile)
            lines = list(reader)
            index_pusty = [i[0] for i in lines]
            for pozycja_plik_log in range(len(list(self.odczyt_danych_z_wierszy()))):
                temp = list(self.odczyt_danych_z_wierszy())[pozycja_plik_log]['TEMPERATURA']
                opad = list(self.odczyt_danych_z_wierszy())[pozycja_plik_log]['OPAD']
                time=list(self.odczyt_danych_z_wierszy())[pozycja_plik_log]['CZAS']
                date=list(self.odczyt_danych_z_wierszy())[pozycja_plik_log]['DATA']
                for pozycja_plik_sort in range(index_pusty.index('')+1,len(lines)):
                    if time >= lines[pozycja_plik_sort-1][3] and time < lines[pozycja_plik_sort][3] \
                            and date==lines[pozycja_plik_sort][2] and lines[pozycja_plik_sort][4]<='95': #dla wszytkich par
                        lines[pozycja_plik_sort-1][0] = temp
                        lines[pozycja_plik_sort - 1][1] = opad
                    elif time >= lines[pozycja_plik_sort-1][3] and date==lines[pozycja_plik_sort][2] \
                            and lines[pozycja_plik_sort][4] == '95': #ID pozycji pliku_sort
                        lines[pozycja_plik_sort][0] = temp
                        lines[pozycja_plik_sort][1] = opad
        with open(self.pliki[nr_pliku], 'w') as writefile:
            writer = self.csv.writer(writefile)
            writer.writerows(lines)

    def nadpisywanie_aktualnym_danymi_plik_sort_calosc(self,nr_pliku=1):
        with open(self.pliki[nr_pliku], 'r') as readfile:
            reader = self.csv.reader(readfile)
            lines = list(reader)
            for pozycja_plik_log in range(len(list(self.odczyt_danych_z_wierszy()))):
                temp = list(self.odczyt_danych_z_wierszy())[pozycja_plik_log]['TEMPERATURA']
                opad = list(self.odczyt_danych_z_wierszy())[pozycja_plik_log]['OPAD']
                time=list(self.odczyt_danych_z_wierszy())[pozycja_plik_log]['CZAS']
                date=list(self.odczyt_danych_z_wierszy())[pozycja_plik_log]['DATA']
                for pozycja_plik_sort in range(2,len(lines)):
                    if time >= lines[pozycja_plik_sort-1][3] and time < lines[pozycja_plik_sort][3] \
                            and date==lines[pozycja_plik_sort][2] and lines[pozycja_plik_sort][4]<='95': #dla wszytkich par
                        lines[pozycja_plik_sort-1][0] = temp
                        lines[pozycja_plik_sort - 1][1] = opad
                    elif time >= lines[pozycja_plik_sort-1][3] and date==lines[pozycja_plik_sort][2] \
                            and lines[pozycja_plik_sort][4] == '95': #ID pozycji pliku_sort
                        lines[pozycja_plik_sort][0] = temp
                        lines[pozycja_plik_sort][1] = opad
        with open(self.pliki[nr_pliku], 'w') as writefile:
            writer = self.csv.writer(writefile)
            writer.writerows(lines)

        # --------------------------plik archiwalny--------------------------------------

    def nadpisywanie_archiwum_plik_sort(self,nr_pliku=1):
                            #Nadpisywanie pliku sort aktualnymi danymi
        with open(self.pliki[nr_pliku], 'r') as readfile:
            reader = self.csv.reader(readfile)
            lines = list(reader)
            index_pusty = [i[0] for i in lines]
            for pozycja_plik_log in range(len(list(self.odczyt_danych_z_wierszy(2)))):
                temp = list(self.odczyt_danych_z_wierszy(2))[pozycja_plik_log]['TEMPERATURA']
                opad = list(self.odczyt_danych_z_wierszy(2))[pozycja_plik_log]['OPAD']
                time = list(self.odczyt_danych_z_wierszy(2))[pozycja_plik_log]['CZAS']
                date = list(self.odczyt_danych_z_wierszy(2))[pozycja_plik_log]['DATA']
                for pozycja_plik_sort in range(index_pusty.index('')+1,len(lines)):
                    if time >= lines[pozycja_plik_sort - 1][3] and time < lines[pozycja_plik_sort][3] \
                            and date == lines[pozycja_plik_sort][2] :  # dla wszytkich par
                        for czterech_powielonych_pozycji in range(-1,3):
                            if lines[pozycja_plik_sort + czterech_powielonych_pozycji][0] == '' \
                                    and lines[pozycja_plik_sort + czterech_powielonych_pozycji][1] == '': #if temeperaura i opad dla każdej kolejnej pozycji są równe
                                lines[pozycja_plik_sort + czterech_powielonych_pozycji][0] = temp
                                lines[pozycja_plik_sort + czterech_powielonych_pozycji][1] = opad
        with open(self.pliki[nr_pliku], 'w') as writefile:
            writer = self.csv.writer(writefile)
            writer.writerows(lines)

    def nadpisywanie_archiwum_plik_sort_calosc(self,nr_pliku=1):
                            #Nadpisywanie pliku sort aktualnymi danymi
        with open(self.pliki[nr_pliku], 'r') as readfile:
            reader = self.csv.reader(readfile)
            lines = list(reader)
            for pozycja_plik_log in range(len(list(self.odczyt_danych_z_wierszy(2)))):
                temp = list(self.odczyt_danych_z_wierszy(2))[pozycja_plik_log]['TEMPERATURA']
                opad = list(self.odczyt_danych_z_wierszy(2))[pozycja_plik_log]['OPAD']
                time = list(self.odczyt_danych_z_wierszy(2))[pozycja_plik_log]['CZAS']
                date = list(self.odczyt_danych_z_wierszy(2))[pozycja_plik_log]['DATA']
                for pozycja_plik_sort in range(2, len(lines)):
                    if time >= lines[pozycja_plik_sort - 1][3] and time < lines[pozycja_plik_sort][3] \
                            and date == lines[pozycja_plik_sort][2] :  # dla wszytkich par
                        for czterech_powielonych_pozycji in range(0,4):
                            if lines[pozycja_plik_sort + czterech_powielonych_pozycji][0] == '' \
                                    and lines[pozycja_plik_sort + czterech_powielonych_pozycji][1] == '': #if temeperaura i opad dla każdej kolejnej pozycji są równe
                                lines[pozycja_plik_sort + czterech_powielonych_pozycji][0] = temp
                                lines[pozycja_plik_sort + czterech_powielonych_pozycji][1] = opad
        with open(self.pliki[nr_pliku], 'w') as writefile:
            writer = self.csv.writer(writefile)
            writer.writerows(lines)

#---------------------------------operacje na kolumnach---------------------------------------------

    def odczyt_danych_z_kolumn(self,nr_kolumny=True,nr_plik=0):
        with open(self.pliki[nr_plik], "r") as csvfile:
            reader =self.csv.DictReader(csvfile)
            for row in reader:
                yield(row[self.nazwy_kolumn[nr_kolumny]])

    def zakres_kolumn(self,start=0, finish=True,nr_kolumny=True,nr_plik=0): #wyniki od start do finish z dla nr kolumny
        zakres = list(self.odczyt_danych_z_kolumn(nr_kolumny,nr_plik))
        for wiersz in range(start, finish):
            yield zakres[wiersz]

    #operacje na wierszach
    def odczyt_danych_z_wierszy(self,nr_plik=0):
        with open(self.pliki[nr_plik], "r") as csvfile:
            reader =self.csv.DictReader(csvfile)
            for row in reader:
                    yield row

    def zakres_wierszy(self,start=0, finish=True,nr_plik=0): #wyniki od start do finish dla wszystkich wierszy
        zakres = list(self.odczyt_danych_z_wierszy(nr_plik))
        for wiersz in range(start, finish):
            yield zakres[wiersz]

#----------------------------------D4.KONTENER-----------------------------------------------------

from time import sleep

#wprowadź date do pozyskania danych archiwalnych
dzien = '09'
miesiac = '11'
rok = '2018'

def main():
    pozyskiwane_dane = Pozyskiwane_dane()
    operacje_na_plikach = Operacje_na_plikach()

# reset plik sort
    #operacje_na_plikach.reset_plik_sort_czyszczenie_zawartosci()

    while True:
        #wyświetla utualną temoeraturę i opady co 15min
        print(pozyskiwane_dane.akutualna_temp())
        print(pozyskiwane_dane.aktualne_opady())

        operacje_na_plikach.dopisanie_do_pliku_log(pozyskiwane_dane.akutualna_temp(),pozyskiwane_dane.aktualne_opady())
        print('1')
        operacje_na_plikach.dopisanie_do_pliku_log_archiwalny(pozyskiwane_dane.temeratura_archiwalna(), pozyskiwane_dane.opad_archiwalny())
        print('2')
        operacje_na_plikach.dopisanie_do_pliku_sort()
        print('3')
        try:
            operacje_na_plikach.nadpisywanie_aktualnym_danymi_plik_sort()
            print("4a")
        except:
            operacje_na_plikach.nadpisywanie_aktualnym_danymi_plik_sort_calosc()
            print("4b")
        try:
            operacje_na_plikach.nadpisywanie_archiwum_plik_sort()
            print("5a")
        except:
            operacje_na_plikach.nadpisywanie_archiwum_plik_sort_calosc()
            print("5b")
        sleep(900)
            #print(list(operacje_na_plikach.odczyt_danych_z_kolumn(0)))
main()
