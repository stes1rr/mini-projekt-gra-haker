import os
import random
import time

os.system("")  # włącza kolory w starszych terminalach Windows

ZIELONY = "\033[92m"
CZERWONY = "\033[91m"
ZOLTY = "\033[93m"
CYJAN = "\033[96m"
SZARY = "\033[90m"
RESET = "\033[0m"

MAX_ALARM = 100
LICZBA_PROB = 6
KARY = {3: 4, 4: 5, 5: 6}

BANER = r"""
 ____  ____  _____    _    ____ _   _
| __ )|  _ \| ____|  / \  / ___| | | |
|  _ \| |_) |  _|   / _ \| | | | |_| |
| |_) |  _ <| |___ / ___ \ |___|  _  |
|____/|_| \_\_____/_/   \_\____|_| |_|
"""


def pisz_wolno(tekst, kolor=RESET, opoznienie=0.03):
    for znak in tekst:
        print(kolor + znak + RESET, end="", flush=True)
        time.sleep(opoznienie)
    print()


def pasek(opis, kroki=20):
    for i in range(kroki + 1):
        print(f"\r{opis} [{'#' * i}{'.' * (kroki - i)}] {i * 100 // kroki}%", end="", flush=True)
        time.sleep(0.08)
    print()


def wskaznik_alarmu(alarm):
    dlugosc = 20
    alarm = min(alarm, MAX_ALARM)
    ile = alarm * dlugosc // MAX_ALARM
    if alarm < 40:
        kolor = ZIELONY
    elif alarm < 70:
        kolor = ZOLTY
    else:
        kolor = CZERWONY
    return f"{kolor}[{'#' * ile}{'.' * (dlugosc - ile)}] {alarm}%{RESET}"


def intro():
    print(CYJAN + BANER + RESET)
    pisz_wolno(">>> SYSTEM BREACH v2.0 <<<", ZIELONY)
    nick = input("Pseudonim: ").strip()
    if nick == "":
        nick = "anonim"
    pisz_wolno(f"Witaj, {nick}. Łączę z siecią...", CYJAN)
    pasek("Omijanie firewalla")
    return nick


def cyfra(liczba, pozycja, dlugosc):
    return liczba // 10 ** (dlugosc - 1 - pozycja) % 10


def pomoc():
    print("Dostępne komendy:")
    print("  help            lista komend")
    print("  scan            skanuj sieć")
    print("  connect <nr>    połącz z węzłem")
    print("  crack           złam zabezpieczenie węzła")
    print("  status          punkty i poziom alarmu")
    print("  exit            zakończ grę")


siec = [
    {"nazwa": "kamera-wejscie", "ip": "192.168.0.11", "dlugosc": 3, "nagroda": 50},
    {"nazwa": "drukarka-hr", "ip": "192.168.0.23", "dlugosc": 3, "nagroda": 60},
    {"nazwa": "serwer-poczty", "ip": "192.168.0.40", "dlugosc": 4, "nagroda": 100},
    {"nazwa": "skarbiec", "ip": "10.0.0.99", "dlugosc": 5, "nagroda": 250},
]

KOMENDY = ("help", "scan", "connect", "crack", "exit", "status")


def nowy_gracz(nick):
    return {
        "nick": nick,
        "punkty": 0,
        "alarm": 0,
        "polaczony": None,
        "zhakowane": set(),
    }


def scan(gracz):
    pisz_wolno("Skanowanie sieci...", CYJAN)
    pasek("Skan portów", 15)
    print(f"{'NR':<4}{'NAZWA':<18}{'IP':<15}{'ZABEZPIECZENIE':<20}STATUS")
    for i in range(len(siec)):
        wezel = siec[i]
        if i in gracz["zhakowane"]:
            status_wezla = ZIELONY + "[ZHAKOWANY]" + RESET
        else:
            status_wezla = CZERWONY + "[ZABLOKOWANY]" + RESET
        print(f"{i + 1:<4}{wezel['nazwa']:<18}{wezel['ip']:<15}{'kod ' + str(wezel['dlugosc']) + '-cyfrowy':<20}{status_wezla}")


def polacz(gracz, czesci):
    komunikat = "Użycie: connect <numer węzła>"
    if len(czesci) < 2 or not czesci[1].isdigit():
        print(CZERWONY + komunikat + RESET)
        return
    numer = int(czesci[1])
    if numer < 1 or numer > len(siec):
        print(CZERWONY + f"Nie ma węzła o numerze {numer}." + RESET)
        return
    wezel = siec[numer - 1]
    gracz["polaczony"] = numer - 1
    pisz_wolno(f"Połączono z {wezel['nazwa']} ({wezel['ip']})", CYJAN)


def sprawdz(kod, proba, dlugosc):
    trafione = 0
    znaczniki = []
    for pozycja in range(dlugosc):
        szukana = cyfra(kod, pozycja, dlugosc)
        podana = cyfra(proba, pozycja, dlugosc)
        if podana == szukana:
            znaczniki.append(ZIELONY + "[#]" + RESET)
            trafione += 1
        elif podana < szukana:
            znaczniki.append(ZOLTY + "[+]" + RESET)
        else:
            znaczniki.append(ZOLTY + "[-]" + RESET)
    return trafione, "".join(znaczniki)


def lamanie_kodu(wezel, gracz):
    dlugosc = wezel["dlugosc"]
    kod = random.randint(10 ** (dlugosc - 1), 10 ** dlugosc - 1)
    pozostalo = LICZBA_PROB
    uzyte = set()
    historia = []
    print(f"Zabezpieczenie: kod {dlugosc}-cyfrowy.  [#] trafiona   [+] szukana cyfra większa   [-] mniejsza")
    while pozostalo > 0:
        tekst = input(f"Kod ({pozostalo} prób) > ").strip()
        if not tekst.isdigit() or len(tekst) != dlugosc:
            print(CZERWONY + f"Wpisz dokładnie {dlugosc} cyfr." + RESET)
            continue
        proba = int(tekst)
        if proba in uzyte:
            print(ZOLTY + "Ten kod był już sprawdzany. Próba nie została zużyta." + RESET)
            continue
        uzyte.add(proba)
        historia.append(proba)
        trafione, wiersz = sprawdz(kod, proba, dlugosc)
        print("            " + wiersz)
        if trafione == dlugosc:
            return True
        pozostalo -= 1
        gracz["alarm"] += KARY[dlugosc]
        print("Alarm:  " + wskaznik_alarmu(gracz["alarm"]))
        if gracz["alarm"] >= MAX_ALARM:
            return False
    print(CZERWONY + f"Zabezpieczenie się zresetowało. Kod brzmiał: {kod}" + RESET)
    print("Twoje próby:", historia)
    return False


def crack(gracz):
    if gracz["polaczony"] is None:
        print(CZERWONY + "Brak połączenia. Użyj: connect <nr>" + RESET)
        return
    numer = gracz["polaczony"]
    wezel = siec[numer]
    if numer in gracz["zhakowane"]:
        print(ZOLTY + "Ten węzeł jest już Twój." + RESET)
        return
    wygrana = lamanie_kodu(wezel, gracz)
    if wygrana:
        gracz["zhakowane"].add(numer)
        gracz["punkty"] += wezel["nagroda"]
        pisz_wolno("ACCESS GRANTED", ZIELONY)
        print(f"+{wezel['nagroda']} pkt")
    else:
        pisz_wolno("ACCESS DENIED", CZERWONY)


def status(gracz):
    print(f"Haker: {gracz['nick']}    Punkty: {gracz['punkty']}")
    print("Alarm:  " + wskaznik_alarmu(gracz["alarm"]))
    print(f"Zhakowane węzły: {len(gracz['zhakowane'])}/{len(siec)}")
    pozostale = set(range(len(siec))) - gracz["zhakowane"]
    if len(pozostale) > 0:
        nazwy = []
        for indeks in sorted(pozostale):
            nazwy.append(siec[indeks]["nazwa"])
        print("Do zhakowania:  " + ", ".join(nazwy))
    if gracz["polaczony"] is None:
        print("Połączenie: brak")
    else:
        print("Połączenie: " + siec[gracz["polaczony"]]["nazwa"])


def main():
    nick = intro()
    gracz = nowy_gracz(nick)
    pisz_wolno("Wpisz help, aby zobaczyć komendy.", SZARY)
    while True:
        if gracz["polaczony"] is None:
            miejsce = "siec"
        else:
            miejsce = siec[gracz["polaczony"]]["nazwa"]
        komenda = input(ZIELONY + nick + RESET + "@" + miejsce + "> ")
        komenda = komenda.strip().lower()
        czesci = komenda.split()
        if not czesci:
            continue
        if czesci[0] not in KOMENDY:
            print(CZERWONY + f"Nieznana komenda: {czesci[0]}. Wpisz help." + RESET)
            continue
        if czesci[0] == "help":
            pomoc()
        elif czesci[0] == "scan":
            scan(gracz)
        elif czesci[0] == "connect":
            polacz(gracz, czesci)
        elif czesci[0] == "crack":
            crack(gracz)
        elif czesci[0] == "status":
            status(gracz)
        elif czesci[0] == "exit":
            pisz_wolno("Rozłączono.", CYJAN)
            break
        if gracz["alarm"] >= MAX_ALARM:
            pisz_wolno("ALARM! Koniec gry.", CZERWONY)
            break
        if len(gracz["zhakowane"]) == len(siec):
            pisz_wolno("*** SIEĆ PRZEJĘTA ***", ZIELONY)
            break
    print(f"Wynik końcowy: {gracz['punkty']} pkt")


if __name__ == "__main__":
    main()
