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
        temp=int(self.re.search(r"TEMPERATURA.+\b([0-9][0-9]?)",self.przeszukiwana_strona()).group(1))
        return temp

    def aktualne_opady(self):
        opady=self.re.search(r"CHMURY[.]+.([\w.]*.[\w?.]*)",self.przeszukiwana_strona()).group(1)
        return opady

#--------Wariant_2-------
'''
Gdy nie pobiera danych to ma sobie je sam uzupełnić 
'''

#----------------------------------Główna zawartość---------------------------
def main():
    pozyskiwane_dane = Pozyskiwane_dane()
main()
