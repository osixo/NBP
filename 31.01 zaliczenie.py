import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import requests
from PIL import Image, ImageTk
from tkcalendar import *
from datetime import datetime
from datetime import timedelta
import pandas as pd


def odwroc_wartosci_walut():
    x = y = 0
    for i in tabela_wszystkich_walut:
        y = 0
        for j in i:
            tabela_wszystkich_walut[x][y] = round(1 / j, 4)
            y += 1
        x += 1


def narysuj_wykres(tabela_dat):
    if status_odwrotnosci.get():
        # tabela_wszystkich_walut = np.reciprocal(tabela_wszystkich_walut)
        odwroc_wartosci_walut()

    tytul_ze_skrotami = ""

    for i in pole_z_wyborem_walut.curselection():
        tytul_ze_skrotami += skroty_nazw_walut[i] + ", "

    for i in tabela_wszystkich_walut:
        if status_zlota.get():
            plt.title(f"Wartość złota\n"
                      f"{kalendarz_poczatek.get_date()} - {kalendarz_koniec.get_date()}")
            plt.bar(x=tabela_dat, height=i)

        else:
            plt.title(f"Wykresy walut: {tytul_ze_skrotami}\n"
                      f"    {kalendarz_poczatek.get_date()}  -  {kalendarz_koniec.get_date()}    ")
            plt.plot(tabela_dat, i)

    if status_zlota.get():
        pass
    else:
        lista_wykresow = []
        for i in pole_z_wyborem_walut.curselection():
            lista_wykresow.append(skroty_nazw_walut[i])
        plt.legend(lista_wykresow, loc="best")

    if status_odwrotnosci.get():
        plt.ylabel("za 1 złotego")
    else:
        plt.ylabel("złotych")

    plt.xticks(np.arange(0, len(tabela_dat) + 1, 1 + int(len(tabela_dat) / 20)), rotation=45, size=6)
    plt.savefig('wykres.png')
    plt.show()

    wykres = tk.Label(root)
    image = Image.open("wykres.png")
    width, height = image.size
    new_width = width * 0.8
    new_height = height * 0.8
    image = image.resize((int(new_width), int(new_height)), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(image)
    wykres.configure(image=image)
    wykres.image = image
    wykres.place(relx=0.5, rely=0.485, anchor='n')


def tylko_zloto():
    if status_zlota.get():
        klawisz_odwrotnosc_wartosci.deselect()
        klawisz_odwrotnosc_wartosci.configure(state="disabled")
        pole_z_wyborem_walut.configure(state="disabled")
    else:
        klawisz_odwrotnosc_wartosci.configure(state="active")
        pole_z_wyborem_walut.configure(state="normal")


def wykresy_walut():
    wybrane_waluty = pole_z_wyborem_walut.curselection()
    for i in wybrane_waluty:

        # tytul_wykresu_waluty += skroty_nazw_walut[i] + " "
        freq = 365
        poczatek = datetime.strptime(kalendarz_poczatek.get_date(), '%Y-%m-%d')
        koniec = datetime.strptime(kalendarz_koniec.get_date(), '%Y-%m-%d')
        zakresy_dat = pd.date_range(start=poczatek, end=koniec, freq=f'{freq}D').to_pydatetime().tolist()

        tabelaDat = []
        tabelaWartosci = []

        for z in zakresy_dat:
            koniec_okresu = min(z + timedelta(days=freq - 1), koniec)

            adresCaly = "http://api.nbp.pl/api/exchangerates/rates/a/" + skroty_nazw_walut[i] + "/" + z.strftime(
                '%Y-%m-%d') + "/" + koniec_okresu.strftime('%Y-%m-%d') + "/"
            response = requests.get(adresCaly)
            responseBody = response.json()

            # tabela dat jedna dla wszystkich walut
            for j in responseBody['rates']:
                tabelaDat.append(j['effectiveDate'])

            # tabela z wartościami walut
            for k in responseBody['rates']:
                tabelaWartosci.append(k['mid'])

        tabela_wszystkich_walut.append(tabelaWartosci)

    narysuj_wykres(tabelaDat)


def wykres_zlota():
    tabela_wszystkich_walut.clear()

    freq = 365
    poczatek = datetime.strptime(kalendarz_poczatek.get_date(), '%Y-%m-%d')
    koniec = datetime.strptime(kalendarz_koniec.get_date(), '%Y-%m-%d')
    zakresy_dat = pd.date_range(start=poczatek, end=koniec, freq=f'{freq}D').to_pydatetime().tolist()

    tabelaDat = []
    tabelaWartosci = []

    for z in zakresy_dat:
        koniec_okresu = min(z + timedelta(days=freq - 1), koniec)

        adresCaly = "http://api.nbp.pl/api/cenyzlota/" + z.strftime('%Y-%m-%d') + "/" + koniec_okresu.strftime('%Y-%m-%d') + "/"
        response = requests.get(adresCaly)
        responseBody = response.json()

        # tabela z wartościami i datami
        for i in responseBody:
            tabelaDat.append(i['data'])
            tabelaWartosci.append(i['cena'])

        tabela_wszystkich_walut.append(tabelaWartosci)

    narysuj_wykres(tabelaDat)


def aktualizuj_wykres():
    tabela_wszystkich_walut.clear()

    # sprawdzam czy wybrano walutę
    if pole_z_wyborem_walut.curselection():
        pole_z_wyborem_walut.configure(background="#CBD6D6")
        # sprawdzam czy day są w dobrej kolejności
        if (kalendarz_koniec.get_date() > kalendarz_poczatek.get_date()):
            opis_kalendarza_poczatek.configure(bg="#95AFAF")
            opis_kalendarza_koniec.configure(bg="#95AFAF")
            if status_zlota.get():
                wykres_zlota()
            else:
                wykresy_walut()
        else:
            # kolor czerwony jeśli daty są złe
            opis_kalendarza_poczatek.configure(bg="#ff0000")
            opis_kalendarza_koniec.configure(bg="#ff0000")
    else:
        pole_z_wyborem_walut.configure(background="#ff0000")


tabela_wszystkich_walut = []
lista_nazw_walut = ["bat (Tajlandia)", "dolar amerykański", "dolar australijski", "dolar Hongkongu", "dolar kanadyjski",
                    "dolar nowozelandzki", "dolar singapurski", "euro", "forint (Węgry)", "frank szwajcarski",
                    "funt szterling", "hrywna (Ukraina)*)", "jen (Japonia)", "korona czeska", "korona duńska",
                    "korona islandzka", "korona norweska", "korona szwedzka", "lej rumuński", "lew (Bułgaria)",
                    "lira turecka", "nowy izraelski zekel", "peso chilijskie", "peso filipińskie", "peso meksykańskie",
                    "rand (Republika Południowej Afryki)", "real (Brazylia)", "ringgit (Malezja)", "rupia indonezyjska",
                    "rupia indyjska", "won południowokoreański", "yuan renminbi (Chiny)", "SDR (MFW)"]
skroty_nazw_walut = ["THB", "USD", "AUD", "HKD", "CAD", "NZD", "SGD", "EUR", "HUF", "CHF", "GBP", "UAH", "JPY", "CZK",
                     "DKK", "ISK", "NOK", "SEK", "RON", "BGN", "TRY", "ILS", "CLP", "PHP", "MXN", "ZAR", "BRL", "MYR",
                     "IDR", "INR", "KRW", "CNY", "XDR"
                     ]

root = tk.Tk()
root.title('Kursy walut i złota NBP.')

# Utworzenie obiektu canvas, który będzie zawierał wszystkie elementy GUI
canvas = tk.Canvas(root, width=1000, height=800)
canvas.pack()

ramka = tk.Frame(canvas, bg="#CBD6D6")
ramka.place(relx=0.5, rely=0.48, relwidth=0.9, relheight=0.5, anchor='n')

# wyświetlam opis kalenrarza z początkiem zakresu
kalendarz_poczatek = Calendar(canvas, selectmode="day", year=2023, month=1, day=10, date_pattern='y-mm-dd',
                              bg="#00ff00")
kalendarz_poczatek.place(relx=0.03, rely=0.05, relwidth=0.3, relheight=0.3)
# wyświetlam kalendarz z początkiem zakresu
opis_kalendarza_poczatek = tk.Label(canvas,
                                    bg="#95AFAF")  # Utworzenie obiektu Label, który będzie zawierał tekst, który będzie wyświetlany na ekranie
opis_kalendarza_poczatek.place(relx=0.03, rely=0.01, relwidth=0.3, relheight=0.03)
opis_kalendarza_poczatek.configure(text="Data początkowa")

# wyświetlam kalendarz z końcem zakresu
kalendarz_koniec = Calendar(canvas, selectmode="day", year=2023, month=1, day=13, date_pattern='y-mm-dd', bg="#00ff00")
kalendarz_koniec.place(relx=0.6, rely=0.05, relwidth=0.3, relheight=0.3)
# wyświetlam opis kalenrarza z końcem zakresu
opis_kalendarza_koniec = tk.Label(canvas, bg="#95AFAF")
opis_kalendarza_koniec.place(relx=0.6, rely=0.01, relwidth=0.3, relheight=0.03)
opis_kalendarza_koniec.configure(text="Data końcowa")

# pole wieloktortnego wyboru walut
pole_z_wyborem_walut = tk.Listbox(canvas, bg="#CBD6D6", height=3, selectmode='multiple')

a = 0
for i in lista_nazw_walut:
    pole_z_wyborem_walut.insert(a, i)
    a += 1

pole_z_wyborem_walut.place(relx=0.35, rely=0.05, relwidth=0.23, relheight=0.25)

# czekboks tylko zoto
status_zlota = tk.IntVar()
klawisz_tylko_zloto = tk.Checkbutton(canvas, text='Tylko zloto', variable=status_zlota, onvalue=True, offvalue=False,
                                     command=tylko_zloto)
klawisz_tylko_zloto.place(relx=0.25, rely=0.35, relwidth=0.3, relheight=0.05)
# czekboks odwrotność wartości
status_odwrotnosci = tk.IntVar()
klawisz_odwrotnosc_wartosci = tk.Checkbutton(canvas, text='Odwrotność wartości', variable=status_odwrotnosci, onvalue=1,
                                             offvalue=0)
klawisz_odwrotnosc_wartosci.place(relx=0.55, rely=0.35, relwidth=0.3, relheight=0.05)

# klawisz zaktualizuj wykres
klawisz_zaktualizuj_wykres = tk.Button(canvas, text="Zaktualizuj wykres.", command=aktualizuj_wykres, bg="#95AFAF")
klawisz_zaktualizuj_wykres.place(relx=0.25, rely=0.41, relwidth=0.5, relheight=0.05)

canvas.mainloop()
