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
    import re


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
                try:
                    self.dopisanie_do_pliku_log_archiwalny_append_automatycznie(dane_1, dane_2)
                except:
                    self.dopisanie_do_pliku_log_archiwalny_append_recznie(dane_1, dane_2)
            else:
                try:
                    self.dopisanie_do_pliku_log_archiwalny_append_automatycznie(dane_1,dane_2)
                except:
                    self.dopisanie_do_pliku_log_archiwalny_append_recznie(dane_1, dane_2)

    def dopisanie_do_pliku_log_archiwalny_append_automatycznie(self,dane_1,dane_2,nr_pliku=2):
        with open(self.pliki[nr_pliku], 'r') as readfile:
            reader = self.csv.reader(readfile)
            lines = list(reader)
            uzyta_data=set()
        with open(self.pliki[nr_pliku], "a", newline="", encoding='utf-8') as csvfile:
            write = self.csv.DictWriter(csvfile, fieldnames=self.nazwy_kolumn)
            for data_plik_sort in range(1,len(lines)):
                uzyta_data.add(lines[data_plik_sort][2])
            uzyte_pojedyncze_daty = list(uzyta_data)
            uzyte_pojedyncze_daty.sort()
            max_dzien_z_uzyte_pojedyncze_daty = int(self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(3))
            max_miesiac_z_uzyte_pojedyncze_daty = int(self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(2))
            max_rok_z_uzyte_pojedyncze_daty = int(self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(1))
            godz = self.datetime.datetime(max_rok_z_uzyte_pojedyncze_daty,
                                          max_miesiac_z_uzyte_pojedyncze_daty,
                                          max_dzien_z_uzyte_pojedyncze_daty,
                                          0, 0) + self.datetime.timedelta(days=1)
            poz = 0
            koncowa_data_godzina_pobierania=self.datetime.datetime.combine(self.datetime.datetime.today().date(),
                                                         self.datetime.time(23, 59, 59))-self.datetime.timedelta(days=1)
            while godz <= koncowa_data_godzina_pobierania:
                for ID in range(0, 24):
                    if koncowa_data_godzina_pobierania.strftime('%Y-%m-%d') not in uzyta_data:
                        write.writerow({"TEMPERATURA": dane_1[poz],
                                         "OPAD": dane_2[poz],
                                         "DATA": godz.strftime('%Y-%m-%d'),
                                         "CZAS": godz.strftime('%H:%M:%S'),
                                         "ID": ID})
                        godz += self.datetime.timedelta(hours=1)
                        poz += 1
                    else:
                        return readfile

    def dopisanie_do_pliku_log_archiwalny_append_recznie(self,dane_1,dane_2,nr_pliku=2):
        with open(self.pliki[nr_pliku], 'r') as readfile:
            reader = self.csv.reader(readfile)
            lines = list(reader)
            uzyta_data=set()
        with open(self.pliki[nr_pliku], "a", newline="", encoding='utf-8') as csvfile:
            write = self.csv.DictWriter(csvfile, fieldnames=self.nazwy_kolumn)
            for data_plik_sort in range(1,len(lines)):
                uzyta_data.add(lines[data_plik_sort][2])
            godz = self.datetime.datetime(int(rok), int(miesiac), int(dzien), 0, 0)
            poz = 0
            while godz <= self.datetime.datetime(int(rok_recznie), int(miesiac_recznie), int(dzien_recznie), 23, 59) and poz <= 24:
                for data_plik_arch in range(len(lines)):
                    uzyta_data.add(lines[data_plik_arch][2])
                for ID in range(0, 24):
                    if '{year}-{mc}-{day}'.format(year=rok, mc=miesiac, day=dzien) not in uzyta_data:
                        write.writerow({"TEMPERATURA": dane_1[poz],
                                         "OPAD": dane_2[poz],
                                         "DATA": godz.strftime('%Y-%m-%d'),
                                         "CZAS": godz.strftime('%H:%M:%S'),
                                         "ID": ID})
                        godz += self.datetime.timedelta(hours=1)
                        poz += 1
                    else:
                        return readfile

    def dzien_pozyskiwanie_danych_plik_log_archiwalny(self,nr_pliku=2):
        with open(self.pliki[nr_pliku], 'r') as readfile:
            reader = self.csv.reader(readfile)
            lines = list(reader)
            uzyta_data=set()
            for data_plik_sort in range(1, len(lines)):
                uzyta_data.add(lines[data_plik_sort][2])
            uzyte_pojedyncze_daty = list(uzyta_data)
            uzyte_pojedyncze_daty.sort()
            max_dzien_z_uzyte_pojedyncze_daty = int(
                self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(3))
            max_miesiac_z_uzyte_pojedyncze_daty = int(
                self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(2))
            max_rok_z_uzyte_pojedyncze_daty = int(self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(1))
            godz = self.datetime.datetime(max_rok_z_uzyte_pojedyncze_daty,
                                     max_miesiac_z_uzyte_pojedyncze_daty,
                                     max_dzien_z_uzyte_pojedyncze_daty,
                                     0, 0) + self.datetime.timedelta(days=1)
            dzien_globalny = godz.strftime('%d')
        return dzien_globalny

    def miesiac_pozyskiwanie_danych_plik_log_archiwalny(self,nr_pliku=2):
        with open(self.pliki[nr_pliku], 'r') as readfile:
            reader = self.csv.reader(readfile)
            lines = list(reader)
            uzyta_data=set()
            for data_plik_sort in range(1, len(lines)):
                uzyta_data.add(lines[data_plik_sort][2])
            uzyte_pojedyncze_daty = list(uzyta_data)
            uzyte_pojedyncze_daty.sort()
            max_dzien_z_uzyte_pojedyncze_daty = int(
                self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(3))
            max_miesiac_z_uzyte_pojedyncze_daty = int(
                self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(2))
            max_rok_z_uzyte_pojedyncze_daty = int(self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(1))
            godz = self.datetime.datetime(max_rok_z_uzyte_pojedyncze_daty,
                                     max_miesiac_z_uzyte_pojedyncze_daty,
                                     max_dzien_z_uzyte_pojedyncze_daty,
                                     0, 0) + self.datetime.timedelta(days=1)
            miesiac_globalny = godz.strftime('%d')
        return miesiac_globalny

    def rok_pozyskiwanie_danych_plik_log_archiwalny(self,nr_pliku=2):
        with open(self.pliki[nr_pliku], 'r') as readfile:
            reader = self.csv.reader(readfile)
            lines = list(reader)
            uzyta_data=set()
            for data_plik_sort in range(1, len(lines)):
                uzyta_data.add(lines[data_plik_sort][2])
            uzyte_pojedyncze_daty = list(uzyta_data)
            uzyte_pojedyncze_daty.sort()
            max_dzien_z_uzyte_pojedyncze_daty = int(
                self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(3))
            max_miesiac_z_uzyte_pojedyncze_daty = int(
                self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(2))
            max_rok_z_uzyte_pojedyncze_daty = int(self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(1))
            godz = self.datetime.datetime(max_rok_z_uzyte_pojedyncze_daty,
                                     max_miesiac_z_uzyte_pojedyncze_daty,
                                     max_dzien_z_uzyte_pojedyncze_daty,
                                     0, 0) + self.datetime.timedelta(days=1)
            rok_globalny = godz.strftime('%d')
        return rok_globalny

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
                self.dopisanie_do_pliku_sort_append_kolejna_data()

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

    def dopisanie_do_pliku_sort_append_kolejna_data(self,nr_pliku=1):
        with open(self.pliki[nr_pliku], 'r') as readfile:
            reader = self.csv.reader(readfile)
            lines = list(reader)
            uzyta_data = set()
        with open(self.pliki[nr_pliku], "a", newline="", encoding='utf-8') as csvfile:
            write = self.csv.DictWriter(csvfile, fieldnames=self.nazwy_kolumn)
            for data_plik_sort in range(1,len(lines)):
                uzyta_data.add(lines[data_plik_sort][2])
            uzyte_pojedyncze_daty = list(uzyta_data)
            uzyte_pojedyncze_daty.sort()
            max_dzien_z_uzyte_pojedyncze_daty = int(self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(3))
            max_miesiac_z_uzyte_pojedyncze_daty = int(self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(2))
            max_rok_z_uzyte_pojedyncze_daty = int(self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(1))
            godz = self.datetime.datetime(max_rok_z_uzyte_pojedyncze_daty,
                                          max_miesiac_z_uzyte_pojedyncze_daty,
                                          max_dzien_z_uzyte_pojedyncze_daty,
                                          0, 0) + self.datetime.timedelta(days=1)
            while godz <= self.datetime.datetime.now().combine(self.datetime.datetime.today().date(),
                                                               self.datetime.time(23, 59, 59)):
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

#---------------------------------Przetwarzanie danych --------------------------------------------

class Przetwarzanie_danych(object):

    # ----------------------------Wspólne -----------------------------------------------------

    def __init__(self):
        self.dane = list(operacje_na_plikach.odczyt_danych_z_wierszy(1))
        # ilość dni w miesiącu 1-31
        self.zbior_dni_w_mc=['0'+str(i) for i in range(1,10)]+[str(y) for y in range(10,32)]
        # ilość misięcy w roku
        self.zbior_mc_typu_int=[str(i) for i in range(1,13)]
        # ilość lat
        self.zbior_lat = [str(i) for i in range(1, 2100)]

        # wyszukuje dane temepratury dla calej kolumny Temperatura
    def dane_temp_opad(self,wariant_z_kolumn_TEMPERATURA_or_OPAD):
        for i in range(len(self.dane)):
            yield self.dane[i][wariant_z_kolumn_TEMPERATURA_or_OPAD]

    # podmienia pozycje 'Brak danych' i '' na poz wyżej
    def tymczasowe_dane_podmienione_temperatura_opad(self, wariant_z_kolumn_TEMPERATURA_or_OPAD):
        dane_podmienione = list(self.dane_temp_opad(wariant_z_kolumn_TEMPERATURA_or_OPAD))
        for poz_pusta in range(0, len(dane_podmienione)):
            if dane_podmienione[poz_pusta] == 'Brak danych' or dane_podmienione[poz_pusta] == '':
                dane_podmienione[poz_pusta] = dane_podmienione[poz_pusta - 1]
        yield dane_podmienione

    #----------------------------Temperaura -----------------------------------------------------

    def srednia_art_temp_calodobowa(self):
        poz_start = 0
        poz_finish = 24
        godz = 0
        dzien_range = [self.zbior_dni_w_mc[day] for day in range(dzien_spr - 1, dzien_spr)]
        mc_range = [self.zbior_mc_typu_int[month] for month in range(data_mc_pocz - 1, data_mc_koncowa)]
        rok_range = [self.zbior_lat[rok] for rok in range(data_rok_pocz - 1, data_rok_koncowa)]
        dane_podmienione=list(self.tymczasowe_dane_podmienione_temperatura_opad('TEMPERATURA'))
        dane_miesiac_temp = [int(dane_podmienione[0][i]) for i in range(len(self.dane))\
                             if self.dane[i]['DATA'] == '{year}-{mc}-{day}'.format(year=rok_range[0],
                                                                                          mc=mc_range[0],
                                                                                          day=dzien_range[0])]
        while poz_finish <= len(dane_miesiac_temp):
            dane_6_godzine = [dane_miesiac_temp[data_w_mc] for data_w_mc in range(poz_start, poz_finish)]
            srednia_art_6_godzinna = sum(dane_6_godzine) / len(dane_6_godzine)
            print('Średnia temperaura od godz: ' + str(godz) + ' do godz ' + str(godz + 6) + \
                  ' wynosi: ' + str(round(srednia_art_6_godzinna, 2))+' C')
            poz_start += 24
            poz_finish += 24
            godz += 6
        srednia_art_calo_dniowa=sum(dane_miesiac_temp) / len(dane_miesiac_temp)
        print('Średnia temperatura dla {year}-{mc}-{day} wynosi: '.format(year=rok_range[0],
                                                                                          mc=mc_range[0],
                                                                                          day=dzien_range[0])\
              + str(round(srednia_art_calo_dniowa, 2))+' C')

    def srednia_temp_w_podanym_przedziale(self):
        kolejny_dzien = 0
        kolejny_mc = 0
        kolejny_rok = 0
        srednia_art_range = 0
        # Podany przez użytkownika dzień / miesiąc / rok
        dzien_range = [self.zbior_dni_w_mc[day] for day in range(data_dzien_pocz - 1, data_dzien_koncowa)]
        mc_range = [self.zbior_mc_typu_int[month] for month in range(data_mc_pocz - 1, data_mc_koncowa)]
        rok_range = [self.zbior_lat[rok] for rok in range(data_rok_pocz - 1, data_rok_koncowa)]
        # Podmienia dane i mieli
        dane_podmienione = list(self.tymczasowe_dane_podmienione_temperatura_opad('TEMPERATURA'))
        while kolejny_rok < len(rok_range):
            while kolejny_mc < len(mc_range):
                while kolejny_dzien < len(dzien_range):
                    dane_miesiac_temp = [int(dane_podmienione[0][i]) for i in range(len(self.dane)) \
                                         if self.dane[i]['DATA'] == '{year}-{mc}-{day}'.format(year=rok_range[kolejny_rok],
                                                                                          mc=mc_range[kolejny_mc],
                                                                                          day=dzien_range[kolejny_dzien])]
                    srednia_art_dniowa = sum(dane_miesiac_temp) / len(dane_miesiac_temp)
                    print('Średnia temperatura dla {year}-{mc}-{day} wynosi: '.format(year=rok_range[kolejny_rok],
                                                                                      mc=mc_range[kolejny_mc],
                                                                                      day=dzien_range[kolejny_dzien]) \
                          + str(round(srednia_art_dniowa, 2)) + ' C')
                    kolejny_dzien += 1
                    srednia_art_range += srednia_art_dniowa
                kolejny_mc += 1
            kolejny_rok += 1
        print('Średnia temperatura dla podanego przedziału wynosi: ' + str(round(srednia_art_range / kolejny_dzien,2)) + ' C')

    # ----------------------------OPAD -----------------------------------------------------
    #zbior_deszczy = ['słaby deszcz', 'słaby: deszcz opad przelotny ', 'deszcz ', 'słaby: deszcz ']
    # zbior należy co jakiś czas zauktualizować

    def deszcz_w_ciagu_dnia(self):
        poz_start = 0
        poz_finish = 24
        godz = 0
        dzien_range = [self.zbior_dni_w_mc[day] for day in range(dzien_spr - 1, dzien_spr)]
        mc_range = [self.zbior_mc_typu_int[month] for month in range(data_mc_pocz - 1, data_mc_koncowa)]
        rok_range = [self.zbior_lat[rok] for rok in range(data_rok_pocz - 1, data_rok_koncowa)]
        dane_podmienione = list(self.tymczasowe_dane_podmienione_temperatura_opad('OPAD'))
        for deszcz in range(0, len(dane_podmienione[0])):
            if dane_podmienione[0][deszcz] == 'słaby deszcz':
                dane_podmienione[0][deszcz] = '35'
            elif dane_podmienione[0][deszcz] == 'słaby: deszcz opad przelotny ':
                dane_podmienione[0][deszcz] = '18'
            elif dane_podmienione[0][deszcz] == 'deszcz ':
                dane_podmienione[0][deszcz] = '55'
            elif dane_podmienione[0][deszcz] == 'słaby: deszcz ':
                dane_podmienione[0][deszcz] = '35'
            else:
                dane_podmienione[0][deszcz] = '0'
        dane_miesiac_opad = [int(dane_podmienione[0][i]) for i in range(len(self.dane)) \
                             if self.dane[i]['DATA'] == '{year}-{mc}-{day}'.format(year=rok_range[0],
                                                                                          mc=mc_range[0],
                                                                                          day=dzien_range[0])]
        while poz_finish <= len(dane_miesiac_opad):
            dane_6_godzine = [dane_miesiac_opad[data_w_mc] for data_w_mc in range(poz_start, poz_finish)]
            srednia_art_6_godzinna = sum(dane_6_godzine) / len(dane_6_godzine)
            print('Średnia opad od godz: ' + str(godz) + ' do godz ' + str(godz + 6) + \
                  ' wynosi: ' + str(round(srednia_art_6_godzinna, 2))+' mm/1m^2')
            poz_start += 24
            poz_finish += 24
            godz += 6
        srednia_art_calo_dniowa = sum(dane_miesiac_opad) / 24
        print('Średnia opad dla {year}-{mc}-{day} wynosi: '.format(year=rok_range[0],
                                                                   mc=mc_range[0],
                                                                   day=dzien_range[0]) \
              + str(round(srednia_art_calo_dniowa, 2))+' mm/1m^2')

    def deszcz_w_podanym_przedziale(self):
        kolejny_dzien = 0
        kolejny_mc = 0
        kolejny_rok = 0
        srednia_art_range = 0
        # Podany przez użytkownika dzień / miesiąc / rok
        dzien_range = [self.zbior_dni_w_mc[day] for day in range(data_dzien_pocz - 1, data_dzien_koncowa)]
        mc_range = [self.zbior_mc_typu_int[month] for month in range(data_mc_pocz - 1, data_mc_koncowa)]
        rok_range = [self.zbior_lat[rok] for rok in range(data_rok_pocz - 1, data_rok_koncowa)]
        # Podmienia dane i mieli
        dane_podmienione = list(self.tymczasowe_dane_podmienione_temperatura_opad('OPAD'))
        for deszcz in range(0, len(dane_podmienione[0])):
            if dane_podmienione[0][deszcz] == 'słaby deszcz':
                dane_podmienione[0][deszcz] = '35'
            elif dane_podmienione[0][deszcz] == 'słaby: deszcz opad przelotny ':
                dane_podmienione[0][deszcz] = '18'
            elif dane_podmienione[0][deszcz] == 'deszcz ':
                dane_podmienione[0][deszcz] = '55'
            elif dane_podmienione[0][deszcz] == 'słaby: deszcz ':
                dane_podmienione[0][deszcz] = '35'
            else:
                dane_podmienione[0][deszcz] = '0'
        while kolejny_rok < len(rok_range):
            while kolejny_mc < len(mc_range):
                while kolejny_dzien < len(dzien_range):
                    dane_miesiac_opad = [int(dane_podmienione[0][i]) for i in range(len(self.dane)) \
                                         if self.dane[i]['DATA'] == '{year}-{mc}-{day}'.format(year=rok_range[kolejny_rok],
                                                                                          mc=mc_range[kolejny_mc],
                                                                                          day=dzien_range[kolejny_dzien])]
                    srednia_art_dniowa = sum(dane_miesiac_opad) / 24
                    print('Średni opad dla {year}-{mc}-{day} wynosi: '.format(year=rok_range[kolejny_rok],
                                                                                      mc=mc_range[kolejny_mc],
                                                                                      day=dzien_range[kolejny_dzien]) \
                          + str(round(srednia_art_dniowa, 2)) + ' mm/m2')
                    kolejny_dzien += 1
                    srednia_art_range += srednia_art_dniowa
                kolejny_mc += 1
            kolejny_rok += 1
        print('Sumaryczny opad dla podanego przedziału wynosi: ' + str(round(srednia_art_range, 2)) + ' mm/m^2')
#----------------------------------D5.KONTENER-----------------------------------------------------

from time import sleep

#------------daty do pozyskania danych archiwalnych---------------------------------------------------
dzien = Operacje_na_plikach().dzien_pozyskiwanie_danych_plik_log_archiwalny()
miesiac = Operacje_na_plikach().miesiac_pozyskiwanie_danych_plik_log_archiwalny()
rok = Operacje_na_plikach().rok_pozyskiwanie_danych_plik_log_archiwalny()

#------------wprowadź daty do pozyskania danych archiwalnych ręcznie jakby automat nie działał---------
dzien_recznie='15' #od 1 do 9 nalezy prowadzić przed liczbą 0
miesiac_recznie = '11'
rok_recznie = '2018'
#dzien=dzien_recznie
#miesiac=miesiac_recznie
#rok=rok_recznie


#-----------------wprowadź date do pozyskania danych podsumujwujacych w przedziale--------------------------
data_dzien_pocz = 5
data_dzien_koncowa = 5
data_mc_pocz = 11
data_mc_koncowa = 11
data_rok_pocz = 2018
data_rok_koncowa = 2018


#---------------------------przypisanie klas--------------------
pozyskiwane_dane = Pozyskiwane_dane()
operacje_na_plikach = Operacje_na_plikach()
przetwarzanie_danych=Przetwarzanie_danych()


# reset plik sort
    #operacje_na_plikach.reset_plik_sort_czyszczenie_zawartosci()



# Średnia temperatura w przedziale
    #przetwarzanie_danych.srednia_temp_w_podanym_przedziale()
# Średni opad w przedziale
    #przetwarzanie_danych.deszcz_w_podanym_przedziale()

#odczyt danych:
    #operacje_na_plikach.odczyt_danych_z_wierszy()
    #operacje_na_plikach.zakres_wierszy()
    #operacje_na_plikach.odczyt_danych_z_kolumn()
    #operacje_na_plikach.zakres_kolumn()
while True:
    print('Poczekaj do 5')
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

    print('\n'*50)

    #wyświetla utualną temoeraturę i opady co 15min
    print('Aktualna temperatuta wynosi: ' + str(pozyskiwane_dane.akutualna_temp()) + ' C')
    print('Aktualne warunki atmosferyczne: ' + str(pozyskiwane_dane.aktualne_opady()))
    print('\nWpisz żeby uzusykać: ')
    print('\nInformacje dniowe: sd ')
    wybor_panel_glowny = input().lower()
    if wybor_panel_glowny == 'sd':
        print('\nWpisz: ')
        print('\nŚrednia dobowa temperatura wpisz: std: ')
        print('Itensywność opdaów w ciągu dnia wpisz: io ')
        Informacje_dniowe = input().lower()
        if Informacje_dniowe == 'std':
            print('\n Wybrałeś srednią dobową temperaturę')
            print('Podaj dzien: ')
            dzien_spr = int(input())
            print('Podaj miesiac: ')
            miesiac_spr = int(input())
            print('Podaj rok: ')
            rok_spr = int(input())
            przetwarzanie_danych.srednia_art_temp_calodobowa()
        elif Informacje_dniowe == 'io':
            print('\n Wybrałeś itensywność opdaów w ciągu dnia')
            print('Podaj dzien: ')
            dzien_spr = int(input())
            print('Podaj miesiac: ')
            miesiac_spr = int(input())
            print('Podaj rok: ')
            rok_spr = int(input())
            przetwarzanie_danych.deszcz_w_ciagu_dnia()
    sleep(900)

