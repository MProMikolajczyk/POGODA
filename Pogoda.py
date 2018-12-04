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
        self.strona_n2 =dict()
        self.strona_n3 =dict()
        for dzien in range(Daty.dzien,Daty.warunek_brzegowy_dzien):
            if dzien in range(0, 10):
                dzien = '0' + str(dzien)
            powtarzalna_strona_n2 = {
                'https://pogoda.interia.pl/archiwum-pogody-{day}-{mc}-{year},cId,27670'.format(day=dzien ,
                                                                                               mc=Daty.miesiac,
                                                                                               year=Daty.rok): \
                    '/html/body/div/div/div/section/div/div/div/div/div/div/span/span/text()'}
            powtarzalna_strona_n3 = {
                'https://pogoda.interia.pl/archiwum-pogody-{day}-{mc}-{year},cId,27670'.format(day=dzien,
                                                                                               mc=Daty.miesiac,
                                                                                               year=Daty.rok): \
                    '/html/body/div/div/div/section/div/div/div/div/div/div/text()'}
            self.strona_n2.update(powtarzalna_strona_n2)
            self.strona_n3.update(powtarzalna_strona_n3)
        self.nr_strony = [self.strona_n1, self.strona_n2,self.strona_n3]
        self.wyszukane_dane_strona_2 = list(self.przeszukiwana_strona(1))
        self.wyszukane_dane_strona_3 = list(self.przeszukiwana_strona(2))
        self.wyszukane_dane_arch_opad=[]
        self.wyszukane_dane_arch_wilogotosc=[]

    # ----------------------------Uzupelenienie stron -------------------------------------


    #----------------------------Wariant_1-------------------------------------

    def przeszukiwana_strona(self, nr_strony=0):
        for strona in self.nr_strony[nr_strony]:
            wybrana_strona=self.requests.get(strona)
            html_content=self.html.fromstring(wybrana_strona.content)
            stuktura_html=''.join(html_content.xpath(self.nr_strony[nr_strony][strona]))
            yield stuktura_html


    def akutualna_temp(self):
        try:
            for i in range(0,len(list(self.przeszukiwana_strona(0)))):
                temp=self.re.search(r"TEMPERATURA.+\s(.?[0-9][0-9]?)",list(self.przeszukiwana_strona(0))[i]).group(1)
                return temp
        except:
            temp='Brak danych'
            return temp

    def aktualne_opady(self):
        try:
            for i in range(0, len(list(self.przeszukiwana_strona(0)))):
                opady=self.re.search(r"WARUNKI[.]+.([\w.]*.[\w?.]*.[\w?.]*.[\w?.]*.[\w?.]*.[\w?.]*)",list(self.przeszukiwana_strona(0))[i]).group(1)
                return opady
        except:
            opady='Brak danych'
            return opady

    #---------------------------Wariant_2------------------------------------

    def temeratura_archiwalna(self):
        try:
            for i in range(0, len(self.wyszukane_dane_strona_2)):
                temp_arch = self.re.findall(r".?[0-9]°COdczuwalna.(.?[0-9][0-9]?)", self.wyszukane_dane_strona_2[i])
                yield temp_arch
        except:
            temp_arch='Brak'
            yield temp_arch

    def opad_archiwalny(self):
        try:
            self.wyszukane_dane_arch_opad.clear()
            self.wyszukane_dane_arch_wilogotosc.clear()
            for i in range(0, len(self.wyszukane_dane_strona_2)):
                opad_arch = self.re.findall(r".?[0-9][0-9]?°COdczuwalna..?[0-9][0-9]?°C.([A-Z][a-zżźćńółęąś]*\s?[a-zżźćńółęąś?]*)[\w]*",self.wyszukane_dane_strona_2[i])
                self.wyszukane_dane_arch_opad.append(opad_arch)
            for j in range(0, len(self.wyszukane_dane_strona_3)):
                wilgotnosc_arch = self.re.findall(r"(.?[0-9][0-9])", self.wyszukane_dane_strona_3[j])
                self.wyszukane_dane_arch_wilogotosc.append(wilgotnosc_arch)
            for nr_poz in range(len(self.wyszukane_dane_arch_opad)):
                if self.wyszukane_dane_arch_opad[nr_poz] == 'Zachmurzenie duże' and self.wyszukane_dane_arch_wilogotosc[nr_poz] >= '98':
                    self.wyszukane_dane_arch_opad[nr_poz] = "słaby deszcz"
            return self.wyszukane_dane_arch_opad
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

            koncowa_data_godzina_pobierania=self.datetime.datetime.combine(self.datetime.datetime.today().date(),
                                                         self.datetime.time(23, 59, 59))-self.datetime.timedelta(days=1)
            nastepny_dzien=0
            while godz <= koncowa_data_godzina_pobierania:
                if koncowa_data_godzina_pobierania.strftime('%Y-%m-%d') not in uzyta_data:
                    for ID in range(0, 24):
                        write.writerow({"TEMPERATURA": dane_1[nastepny_dzien][ID],
                                         "OPAD": dane_2[nastepny_dzien][ID],
                                         "DATA": godz.strftime('%Y-%m-%d'),
                                         "CZAS": godz.strftime('%H:%M:%S'),
                                         "ID": ID})
                        godz += self.datetime.timedelta(hours=1)
                    nastepny_dzien += 1
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
            godz = self.datetime.datetime(int(Daty.rok), int(Daty.miesiac), int(Daty.dzien), 0, 0)
            poz = 0
            while godz <= self.datetime.datetime(int(Daty.rok_recznie), int(Daty.miesiac_recznie), int(Daty.dzien_recznie), 23, 59) and poz <= 24:
                for data_plik_arch in range(len(lines)):
                    uzyta_data.add(lines[data_plik_arch][2])
                for ID in range(0, 24):
                    if '{year}-{mc}-{day}'.format(year=Daty.rok, mc=Daty.miesiac, day=Daty.dzien) not in uzyta_data:
                        write.writerow({"TEMPERATURA": dane_1[0][poz],
                                         "OPAD": dane_2[0][poz],
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
            max_dzien_z_uzyte_pojedyncze_daty = int(self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(3))
            max_miesiac_z_uzyte_pojedyncze_daty = int(self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(2))
            max_rok_z_uzyte_pojedyncze_daty = int(self.re.search(r'(\d*).(\d*).(\d*)', max(uzyte_pojedyncze_daty)).group(1))
            godz = self.datetime.datetime(max_rok_z_uzyte_pojedyncze_daty,
                                     max_miesiac_z_uzyte_pojedyncze_daty,
                                     max_dzien_z_uzyte_pojedyncze_daty,
                                     0, 0) + self.datetime.timedelta(days=1)
            miesiac_globalny = godz.strftime('%m')
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
            rok_globalny = godz.strftime('%Y')
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

    def odczyt_danych_z_kolumn(self,nr_kolumny=1,nr_plik=0,ID=4):
        with open(self.pliki[nr_plik], "r") as csvfile:
            reader =self.csv.DictReader(csvfile)
            for row in reader:
                yield(row[self.nazwy_kolumn[nr_kolumny]], row[self.nazwy_kolumn[ID]])

    def zakres_kolumn(self,start=0, finish=0,nr_kolumny=1,nr_plik=0,ID=4): #wyniki od start do finish z dla nr kolumny
        zakres = list(self.odczyt_danych_z_kolumn(nr_kolumny, nr_plik,ID))
        for wiersz in range(start, finish):
            yield zakres[wiersz]

    #operacje na wierszach
    def odczyt_danych_z_wierszy(self,nr_plik=0):
        with open(self.pliki[nr_plik], "r") as csvfile:
            reader =self.csv.DictReader(csvfile)
            for row in reader:
                    yield row

    def zakres_wierszy(self,start=0, finish=0, nr_plik=0): #wyniki od start do finish dla wszystkich wierszy
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

    def srednia_art_temp_calodobowa(self,dzien_spr,miesiac_spr,rok_spr):
        poz_start = 0
        poz_finish = 24
        godz = 0
        dzien_range = [self.zbior_dni_w_mc[day] for day in range(dzien_spr - 1, dzien_spr)]
        mc_range = [self.zbior_mc_typu_int[month] for month in range(miesiac_spr - 1, miesiac_spr)]
        rok_range = [self.zbior_lat[rok] for rok in range(rok_spr - 1, rok_spr)]
        dane_podmienione=list(self.tymczasowe_dane_podmienione_temperatura_opad('TEMPERATURA'))
        dane_miesiac_temp = [int(dane_podmienione[0][i]) for i in range(len(self.dane))\
                             if self.dane[i]['DATA'] == '{year}-{mc}-{day}'.format(year=rok_range[0],
                                                                                          mc=mc_range[0],
                                                                                          day=dzien_range[0])]
        try:
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
        except:
            print('Brak danych w zbiorze')

    def srednia_temp_w_podanym_przedziale(self,data_dzien_pocz,data_dzien_koncowa,data_mc_pocz,
                                    data_mc_koncowa,data_rok_pocz,data_rok_koncowa):
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
        try:
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
        except:
            print('Brak danych w zbiorze')

    # ----------------------------OPAD -----------------------------------------------------
    #zbior_deszczy = ['słaby deszcz', 'słaby: deszcz opad przelotny ', 'deszcz ', 'słaby: deszcz ']
    # zbior należy co jakiś czas zauktualizować

    def deszcz_w_ciagu_dnia(self,dzien_spr,miesiac_spr,rok_spr):
        poz_start = 0
        poz_finish = 24
        godz = 0
        dzien_range = [self.zbior_dni_w_mc[day] for day in range(dzien_spr - 1, dzien_spr)]
        mc_range = [self.zbior_mc_typu_int[month] for month in range(miesiac_spr - 1, miesiac_spr)]
        rok_range = [self.zbior_lat[rok] for rok in range(rok_spr - 1, rok_spr)]
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
            elif dane_podmienione[0][deszcz] == 'Lekkie opady':
                dane_podmienione[0][deszcz] = '47'
            elif dane_podmienione[0][deszcz] == 'Przelotne opady':
                dane_podmienione[0][deszcz] = '42'
            else:
                dane_podmienione[0][deszcz] = '0'
        dane_miesiac_opad = [int(dane_podmienione[0][i]) for i in range(len(self.dane)) \
                             if self.dane[i]['DATA'] == '{year}-{mc}-{day}'.format(year=rok_range[0],
                                                                                          mc=mc_range[0],
                                                                                          day=dzien_range[0])]
        try:
            while poz_finish <= len(dane_miesiac_opad):
                dane_6_godzine = [dane_miesiac_opad[data_w_mc] for data_w_mc in range(poz_start, poz_finish)]
                srednia_art_6_godzinna = sum(dane_6_godzine) / len(dane_6_godzine)
                print('Średni opad od godz: ' + str(godz) + ' do godz ' + str(godz + 6) + \
                      ' wynosi: ' + str(round(srednia_art_6_godzinna, 2))+' mm/1m^2')
                poz_start += 24
                poz_finish += 24
                godz += 6
            srednia_art_calo_dniowa = sum(dane_miesiac_opad) / 24
            print('Średni opad dla {year}-{mc}-{day} wynosi: '.format(year=rok_range[0],
                                                                       mc=mc_range[0],
                                                                       day=dzien_range[0]) \
                  + str(round(srednia_art_calo_dniowa, 2))+' mm/1m^2')
        except:
            print('Brak danych w zbiorze')

    def deszcz_w_podanym_przedziale(self,data_dzien_pocz,data_dzien_koncowa,data_mc_pocz,
                                    data_mc_koncowa,data_rok_pocz,data_rok_koncowa):
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
            elif dane_podmienione[0][deszcz] == 'Lekkie opady':
                dane_podmienione[0][deszcz] = '47'
            elif dane_podmienione[0][deszcz] == 'Przelotne opady':
                dane_podmienione[0][deszcz] = '42'
            else:
                dane_podmienione[0][deszcz] = '0'
        try:
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
        except:
            print('Brak danych w zbiorze')

#----------------------------------D5.DATY-----------------------------------------------------

class Daty(object):
    import datetime
    #------------daty do pozyskania danych archiwalnych---------------------------------------------------
    dzien = int(Operacje_na_plikach().dzien_pozyskiwanie_danych_plik_log_archiwalny())
    warunek_brzegowy_dzien=int(datetime.datetime.today().strftime('%d'))
    miesiac = int(Operacje_na_plikach().miesiac_pozyskiwanie_danych_plik_log_archiwalny())
    rok = int(Operacje_na_plikach().rok_pozyskiwanie_danych_plik_log_archiwalny())

    #------------wprowadź daty do pozyskania danych archiwalnych ręcznie jakby automat nie działał---------
    dzien_recznie='16' #od 1 do 9 nalezy prowadzić przed liczbą 0
    miesiac_recznie = '11'
    rok_recznie = '2018'

    #dzien=dzien_recznie
    #miesiac=miesiac_recznie
    #rok=rok_recznie


#----------------------------------D6.Nawigacja(Panel główny)-----------------------------------------------------
class Nawigacja(object):

    from sys import exit
    #zebrane wszystkie mozliwe wybory znawigacji na wszystkich poziomach

    def wybory(self):
        wybor = ''
        while wybor != 'q':
            wybor = input('Wpisz: ').lower()
            if wybor == 'dp':
                self.panel_dane_pogodowe_poziom_0()
                break
            elif wybor == 'op':
                self.panel_operacje_na_plikach_poziom_0()
                break
            elif wybor == 'b':
                self.panel_startowy()
                break
            elif wybor == 'w':
                main()
            elif wybor == 'q':
                self.exit()
            elif wybor == 'std':
                self.panel_dane_pogodowe_srednia_dobowa_temperatura_poziom_1()
                break
            elif wybor == 'io':
                self.panel_dane_pogodowe_intesywnosc_opadow_poziom_1()
                break
            elif wybor == 'stp':
                self.panel_dane_pogodowe_srednia_temperatura_w_przedziale_poziom_1()
                break
            elif wybor == 'iop':
                self.panel_dane_pogodowe_intesywnosc_opadow_w_przedziale_poziom_1()
                break
            elif wybor == 'odw':
                self.panel_operacje_na_plikach_odczyt_danych_z_wierszy_poziom_1()
                break
            elif wybor == 'odk':
                self.panel_operacje_na_plikach_odczyt_danych_z_kolumn_poziom_1()
                break
            elif wybor == 'odwz':
                self.panel_operacje_na_plikach_zakres_wierszy_poziom_1()
                break
            elif wybor == 'odkz':
                self.panel_operacje_na_plikach_zakres_kolumn_poziom_1()
                break
            elif wybor == 'res':
                print('potwierdź znakiem "t"')
                if input('Czy na pewno') == 't':
                    self.panel_operacje_na_plikach_reset_plik_sort_czyszczenie_zawartosci_poziom_1()
                    break
                else:
                    self.panel_operacje_na_plikach_poziom_0()
                    break

    #panel startowy, możliwe warianty wyboru

    def panel_startowy(self):
        print('\nAktualna temperatuta wynosi: ' + str(pozyskiwane_dane.akutualna_temp()) + ' C')
        print('Aktualne warunki atmosferyczne: ' + str(pozyskiwane_dane.aktualne_opady()))
        print('\nDostępne komendy: ')
        print('\nDane pogodowe: DP')
        print('Operacje na plikach: OP')
        print('Wróć do pozyskiwania danych: W')
        print('Koniec: Q')
        self.wybory()

    # Dane pogodowe poziom 0

    def panel_dane_pogodowe_poziom_0(self):
        print('\nŚrednia dobowa temperatura wpisz: STD')
        print('Itensywność opdaów w ciągu dnia wpisz: IO')
        print('Średnia temperatura w przedziale: STP')
        print('Itensywność opadów w przedziale: IOP')
        print('Wróc do panelu głównego: B')
        print('Wróć do pozyskiwania danych: W')
        print('Koniec: Q')
        self.wybory()

    # Średnia dobowa temperatura
    def panel_dane_pogodowe_srednia_dobowa_temperatura_poziom_1(self):
        dzien_spr = int(input('\nPodaj dzien: '))
        miesiac_spr = int(input('Podaj miesiac: '))
        rok_spr = int(input('Podaj rok: '))
        przetwarzanie_danych.srednia_art_temp_calodobowa(dzien_spr, miesiac_spr, rok_spr)
        self.panel_dane_pogodowe_poziom_0()

    # Itensywność opdaów w ciągu dnia
    def panel_dane_pogodowe_intesywnosc_opadow_poziom_1(self):
        dzien_spr = int(input('\nPodaj dzien: '))
        miesiac_spr = int(input('Podaj miesiac: '))
        rok_spr = int(input('Podaj rok: '))
        przetwarzanie_danych.deszcz_w_ciagu_dnia(dzien_spr, miesiac_spr, rok_spr)
        self.panel_dane_pogodowe_poziom_0()

    # Średnia dobowa temperatura w przedziale
    def panel_dane_pogodowe_srednia_temperatura_w_przedziale_poziom_1(self):
        data_dzien_pocz = int(input('\nPodaj dzien poczatkowy: '))
        data_dzien_koncowa = int(input('Podaj dzien końcowy: '))
        data_mc_pocz = int(input('Podaj miesiac poczatkowy: '))
        data_mc_koncowa = int(input('Podaj miesiac końcowy: '))
        data_rok_pocz = int(input('Podaj rok poczatkowy: '))
        data_rok_koncowa = int(input('Podaj rok końćowy: '))
        przetwarzanie_danych.srednia_temp_w_podanym_przedziale(data_dzien_pocz,data_dzien_koncowa,data_mc_pocz,
                                    data_mc_koncowa,data_rok_pocz,data_rok_koncowa)
        self.panel_dane_pogodowe_poziom_0()

    # intensywnosc_opadow_w_przedziale
    def panel_dane_pogodowe_intesywnosc_opadow_w_przedziale_poziom_1(self):
        data_dzien_pocz = int(input('\nPodaj dzien poczatkowy: '))
        data_dzien_koncowa = int(input('Podaj dzien końcowy: '))
        data_mc_pocz = int(input('Podaj miesiac poczatkowy: '))
        data_mc_koncowa = int(input('Podaj miesiac końcowy: '))
        data_rok_pocz = int(input('Podaj rok poczatkowy: '))
        data_rok_koncowa = int(input('Podaj rok końćowy: '))
        przetwarzanie_danych.deszcz_w_podanym_przedziale(data_dzien_pocz,data_dzien_koncowa,data_mc_pocz,
                                    data_mc_koncowa,data_rok_pocz,data_rok_koncowa)
        self.panel_dane_pogodowe_poziom_0()

    # Operacje na plikach (rest + odczyt danych) poziom 0

    # odczyt danych:
    def panel_operacje_na_plikach_poziom_0(self):
        print('\nOdczyt danych wszytskich wierszy z pliku wpisz: ODW')
        print('Odczyt danych pojedynczej kolumny z pliku wpisz: ODK')
        print('Odczyt danych z ustalonego zkresu wierszy wpisz: ODWZ')
        print('Odczyt danych z ustanogo zakresu kolumn  wpisz: ODKZ')
        print('Reset pliku  wpisz: RES')
        print('Wróc do panelu głównego: B')
        print('Wróć do pozyskiwania danych: W')
        print('Koniec: Q')
        self.wybory()

    #Odczyt danych z wierszy i kolumn
    def panel_operacje_na_plikach_odczyt_danych_z_wierszy_poziom_1(self):
        for wiersz in list(operacje_na_plikach.odczyt_danych_z_wierszy(1)):
            print(wiersz)
        self.panel_operacje_na_plikach_poziom_0()

    def panel_operacje_na_plikach_odczyt_danych_z_kolumn_poziom_1(self):
        print('\nTEMPERATURA wpisz: 0')
        print('OPAD wpisz: 1')
        print('DATA wpisz: 2')
        print('CZAS wpisz: 3')
        nr_kolumny = ''
        while nr_kolumny != '0' or nr_kolumny != '1' or nr_kolumny != '2' or nr_kolumny != '3':
            nr_kolumny = input('Podaj nr kolumny: ')
            if nr_kolumny == '0' or nr_kolumny == '1' or nr_kolumny == '2' or nr_kolumny == '3':
                for wiersz in list(operacje_na_plikach.odczyt_danych_z_kolumn(int(nr_kolumny), 1)):
                    print([wiersz])
                self.panel_operacje_na_plikach_poziom_0()
                break

        # Zakres wierszy i kolumn

    def panel_operacje_na_plikach_zakres_wierszy_poziom_1(self):
        print('\nDostępny zakres od 0 do {0}'.format(len(list(operacje_na_plikach.odczyt_danych_z_wierszy()))))
        start = -1
        finish = len(list(operacje_na_plikach.odczyt_danych_z_wierszy())) + 1
        while int(start)<= 0 or int(finish) >= len(list(operacje_na_plikach.odczyt_danych_z_wierszy())):
            start = input('Podaj początek: ')
            finish = input('Podaj koniec: ')
            if int(start) >= 0 and int(finish) <= len(list(operacje_na_plikach.odczyt_danych_z_wierszy())):
                for wiersz in list(operacje_na_plikach.zakres_wierszy(int(start), int(finish), 1)):
                    print([wiersz])
                break
        self.panel_operacje_na_plikach_poziom_0()


    def panel_operacje_na_plikach_zakres_kolumn_poziom_1(self):
        print('\nDostępny zakres od 0 do {0}'.format(len(list(operacje_na_plikach.odczyt_danych_z_wierszy()))))
        start = -1
        finish = len(list(operacje_na_plikach.odczyt_danych_z_wierszy())) + 1
        nr_kolumny = ''
        while int(start) <= 0 or int(finish) >= len(list(operacje_na_plikach.odczyt_danych_z_wierszy())):
            start = input('Podaj początek: ')
            finish = input('Podaj koniec: ')
            if int(start) >= 0 and int(finish) <= len(list(operacje_na_plikach.odczyt_danych_z_wierszy())):
                while nr_kolumny != '0' or nr_kolumny != '1' or nr_kolumny != '2' or nr_kolumny != '3':
                    nr_kolumny = input('Podaj nr kolumny: ')
                    if nr_kolumny == '0' or nr_kolumny == '1' or nr_kolumny == '2' or nr_kolumny == '3':
                        for wiersz in list(operacje_na_plikach.zakres_kolumn(int(start), int(finish),int(nr_kolumny), 1, 4)):
                            print([wiersz])
                        break
        self.panel_operacje_na_plikach_poziom_0()


    # reset pliku Pogoda_data_sort
    def panel_operacje_na_plikach_reset_plik_sort_czyszczenie_zawartosci_poziom_1(self):
        operacje_na_plikach.reset_plik_sort_czyszczenie_zawartosci()
        self.panel_operacje_na_plikach_poziom_0()

#---------------------------D7.PRZYPISANIE KLAS------------------------------------------------

pozyskiwane_dane = Pozyskiwane_dane()
operacje_na_plikach = Operacje_na_plikach()
przetwarzanie_danych = Przetwarzanie_danych()
nawigacja = Nawigacja()

#----------------------------------D8.KONTENER-----------------------------------------------------

def main():
    from time import sleep

    panel_glowny =set()
    while 't' not in panel_glowny or 'n' not in panel_glowny:
        panel_glowny.add(input('Czy uruchomic panel główny po załadowaniu danych(t/n)?'))
        if 't' in panel_glowny:
            break
        elif 'n' in panel_glowny:
            break

    while True:
        print('Poczekaj aż się załaduje (do 5)')
        operacje_na_plikach.dopisanie_do_pliku_log(pozyskiwane_dane.akutualna_temp(),pozyskiwane_dane.aktualne_opady())
        print('1')
        operacje_na_plikach.dopisanie_do_pliku_log_archiwalny(list(pozyskiwane_dane.temeratura_archiwalna()), pozyskiwane_dane.opad_archiwalny())
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
        #załdaowanie nawigacji tylko raz podczas dziłania programu
        if 't' in panel_glowny:
            nawigacja.panel_startowy()
        sleep(900)
main()