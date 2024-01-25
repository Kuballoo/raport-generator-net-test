#%%
'''
    Skrypt dziala tylko na platformie windows
    Nalezy zainstalowac potrzebne biblioteki (jezeli ich nie ma)
    pip install {lib_name}
'''
import subprocess, platform, csv, speedtest
from fpdf import FPDF
from datetime import datetime
from ping3 import ping

#%% Glowna funkcja
'''
    Glowna funkcja nie przyjmuje zadnych danych oraz nie zwraca.
    Wyswietla proste menu i wywoluje w sobie dwie glowne funkcje zapisu danych 
'''
def main():
    while True:
        print("--- Menu ---")
        print("1. Zapisz do pliku csv (tylko podstawowy zestaw danych)")
        print("2. Zapisz do pliku pdf (zestaw danych rozszerzony)")
        print("0. Wyjscie")
        choice = input("Wybierz opcje: ")
        
        match choice:
            case '1':
                print("Wykonuje potrzebne operacje...")
                save_to_csv(get_network_devices())
            case '2':
                print("Wykonuje potrzebne operacje...")
                save_to_pdf(get_network_devices(), "logo.jpg")
            case '0':
                return None

#%% Speed Test
'''
    Funkcja speed_test nie przyjmuje zadnych argumentow.
    Wynikiem jej dzialania jest tablica obiektow 'string'.
    Dzielimy przez 10**6, poniewaz funkcje zwracaja wartosci w bps, a my potrzebujemy predkosc pobierania w Mbps
'''
def speed_test():
    st = speedtest.Speedtest()
    final_data = ["", "Test predkosci"]
    
    # Zapis predkosci pobierania do tablicy
    download_speed = round(st.download()/10**6, 2);
    final_data.append(f"Pobieranie: {download_speed} Mbps")
    
    # Zapis predkosci wysylania do tablicy
    upload_speed = round(st.upload()/10**6, 2);
    final_data.append(f"Wysylanie: {upload_speed} Mbps")
    return final_data
    
#%% Ping
'''
    Input:
        web - adres strony
        count - ilosc pingow (pomiarow)
        timeout - czas oczekiwania na odpowiedz strony
    Return:
        final_data - ["data", "data", "data", ....]
    
    Funkcja wykonuje okreslona ilosc pomiarow (ping) dla podanej domeny. 
    Zwraca tablice string, pierwszy element jest informacja o tescie dla konkretnej strony, nastepne dane sa to poszczegolne wyniki, zas ostatni element to srednia pomiarow
'''
def ping_test(web, count, timeout):
    ping_times = []         # W tej zmiennej zapisujemy surowe liczby
    final_data = [f"Ping test dla strony {web}"]    # Tu bedziemy przechowywac finalne dane
    
    # W petli wykonujemy konkretna ilosc pomiarow
    for i in range(count):      
        response = ping(web, timeout=timeout)
        
       
        if response is None:        # Jezeli strona nie odpowiedziala dodajemy do surowych danych -1 bedzie to informacja dla administratora ze strona nie odpowiedziala przy tym wywolaniu
            ping_times.append(-1)
        else:                       # W przeciwnym wypadku mnozymy czas odpowiedzi razy 1000 (sekundy -> ms), zaokraglamy i konwertujemy czas do int'a zeby miec czysta odpowiedz w ms
            response *= 1000
            response = int(round(response))
            ping_times.append(response)
        
    ping_times.append(int(round(sum(ping_times)/count)))    # Po calej petli dodajemy srednia wszystkich pomiarow na koncu zwracanej tablicy
    
    
    # Petla ta generuje finalna tablice, ktora bedzie miala dopiski o sredniej pingow oraz o wyniku kazdego pomiaru
    for i in range(count+1):
        if i==count:
            final_data.append(f"Srednia pingow: {ping_times[i]} ms")
        else:
            final_data.append(f"Ping {i+1}: {ping_times[i]} ms")
        
    return final_data
    
    

#%% Wywoluje komendy systemowe
'''
    Funkcja wywoluje polecenia systemowe z poziomu skryptu
    Przyjmuje jeden argument - polecenie (string). 
    Po sprawdzeniu uzywanej platformy zwraca dane wyjsciowe (string), ktore system generuje po wywolaniu danego polecenia
'''
def run_command(command):
    if get_platform() == "Windows":
        result = subprocess.run(command, shell=True, capture_output=True, text=True, encoding='cp1252')
    else: 
        result = subprocess.run(command, shell=False, capture_output=True, text=True)

    return result.stdout

#%% Pobranie platformy
'''
    Funkcja nie pobiera zadnych danych. 
    Zwraca nazwe systemu operacyjnego, na ktorym uruchomiono skrypt
'''
def get_platform():
    return platform.system()

#%% Pobranie oraz zwraca nazwe interfejsu, adres mac oraz adres ip
'''
    Funkcja nie pobiera atrybutow, na podstawie wygenerowanego slownika selekcjonuje dane oraz zwraca wybrane elementy
'''
def get_network_devices():
    platform_name = get_platform()
    keys_to_find = ["PhysicalAddress", "IPv4Address"]           # Elementy do znalezienia w slowniku
    final_data = [["Name", "Physical Address", "Ipv4 Address"]] # Finalne dane z wprowadzonymi naglowkami kolum z danym
    if platform_name == "Windows":
        data = dictionary_generator(run_command("ipconfig /all"))   # Generujemy slownik z danymi
        temp_data = []                                              # Zmienna z tymczasowymi danymi pojedynczej komorki glownej zmiennej (["Name", "Mac", "IPv4"])
        for main_key, dictionary in data.items():                   # Pobieramy glowny klucz naszego slownika oraz dane (slownik)
            temp_data = []                              # Zerujemy slownik z tymczasowymi danymi
            temp_data.append(main_key)                  # Dodajemy do tymczasowego slownika nazwe interfejsu
            for key in keys_to_find:                    # Iterujemy po tablicy z elementami do znaleziania
                if key in dictionary:
                    temp_data.append(dictionary[key])
                else:
                    temp_data.append("")    
            final_data.append(temp_data)                # Dodajemy tymczasowa zmienna do finalnej zmiennej
    return final_data
        
#%% Zapis do pliku CSV
"""
    Zapisuje dane do pliku CSV.
    
    Parameters:
        dane (list): Tablica tablic do zapisania.
        sciezka_do_pliku (str): Ścieżka do pliku CSV.
    
    Returns:
        None
"""
def save_to_csv(dane):
    current_datetime = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
    with open(current_datetime + ".csv", mode='w', newline='', encoding="utf-8") as plik_csv:
        writer = csv.writer(plik_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # Zapisz datę i godzinę jako pojedynczy element listy
        writer.writerow([current_datetime])

        # Zapisz pozostałe wiersze
        for wiersz in dane:
            writer.writerow(wiersz)

    print(f'Dane zostały zapisane do pliku: {current_datetime}')


#%% Zapis do pdf
'''
    Zbior funkcji do generowania pelnego raportu pdf
'''
'''
    save_to_pdf
    Input:
        table - lista danych urzadzen sieciowych, ktora bedzie w postaci prostej tabeli dodana do pdfu
        logo_path - sciezka do logo uzytego przy generowaniu raportu
'''

def save_to_pdf(table, logo_path):
    # Tworzymy obiekt pdf, dodajemy pierwsza strone i ustawiamy podstawowe dane
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('Arial', '', 'arial.ttf', uni=True)
    pdf.set_font("Arial", size=8)
    
    
    current_datetime = add_topic(pdf, logo_path)                    # Dodajemy naglowek i zapisujemy czas generowania raportu, aby pozniej nadac nazwe naszemu raportowi
    add_tests(pdf, ping_test("www.google.com", 4, 2), speed_test()) # Dodajemy test predkosci oraz ping test do naszego pdfu
    
    
    # Określ szerokość kolumn dla danych urzadzen sieciowych
    column_width = pdf.w / 3

    # Dodajemy dane ze zmiennej table
    for row in table:
        for item in row:
            # Sprawdź czy wystarczy miejsca na kolejny wiersz, jeśli nie, dodaj nową stronę
            if pdf.get_y() + 10 > pdf.h:
                pdf.add_page()

            # Wyrównaj do środka i dodaj do kolumny
            pdf.cell(column_width, 10, txt=str(item), align='C')
        pdf.ln(h=10)  # Nowa linia po każdym wierszu, zwiększ wysokość linii (h) na 10
    
    name = current_datetime + ".pdf"
    print(f"Dane zostały zapisane do pliku: {name}")
    pdf.output(name)

##%
'''
    Funkcja dodaje naglowek w postaci loga oraz ponizej date i godzine
    Zwraca date i godzine ktore pozniej mozna wykorzystac jako nazwe pliku
'''
def add_topic(pdf, logo_path):
    page_width = pdf.w  # Określ szerokość strony i logo
    logo_width = 30     # Dostosuj szerokość logo

    # Ustaw logo na środku strony
    logo_x = (page_width - logo_width) / 2
    logo_y = pdf.get_y()
    pdf.image(logo_path, x=logo_x, y=logo_y, w=logo_width)
    
    pdf.ln(logo_width)  # Przesuń kursor niżej
    
    # Dodajemy date i godzine
    current_datetime = datetime.now().strftime("%d-%m-%Y %H-%M-%S")
    pdf.cell(0, 10, txt=f"DD-MM-RRRR HH-MM-SS: {current_datetime}", ln=True, align='C')
    
    return current_datetime

'''
    Input:
        pdf - obiekt pdf do ktorego dodamy dane
        ping_test_data/speed_test_data - tablica string z danymi do dodania
'''
def add_tests(pdf, ping_test_data, speed_test_data):
    data = ping_test_data + speed_test_data
    # Dodaj dane z tablicy
    for item in data:
       pdf.cell(0, 5, txt=item, ln=True) 

#%% Obrabianie danych
'''
    Funkcja przyjmuje surowe dane w postaci string'a, nastepnie wykonuje na nim operacje przez co generuje slownik w postaci:
        {
            key1: {key11: dane, key12: dane, key13: dane, ...},
            nazwa_interfejsu: {atrybut: dane, atrybut: dane},
            ...
        }
    Powyzszy slownik jest zwracany
'''
def dictionary_generator(raw_data):
    splited_data = raw_data.split('\n')                             # Dzielimy dane na oddzielnie linie
    splited_data = [data for data in splited_data if data != '']    # Usuwamy puste linie
    final_data = {}         # Finalne dane ktore beda zwrocone np. {main_key1: {key11: data, key12: data}, main_key2: {key21: data, key22: data}, ...} 
    main_key = ""           # Zmienna przechowujaca nazwe interfejsu, ta zmienna bedzie kluczem w glownym slowniku
    temp_dictionary = {}    # Zmienna przechowujaca tymczasowe pomniejsze slowniki np. {atrybut1: dane, atrybut2: dane, ...}
    for data in splited_data:
        if data[0] != ' ': # Przed nazwami interfejsow nie ma spacji 
            if main_key != "":
                final_data[main_key] = temp_dictionary      # Zapisujemy po pierwszym pelnym przebiegu przypisujemy wygenerowany slownik z atrybutami interfejsu do klucza (nazwa interfejsu)
            temp_dictionary = {}        # Czyscimy dane slownik atrybutow
            main_key = data
        else:
            data = [d for d in data if d != ' ']    # Usuwamy wszystkie spacje i tworzymy tablice CHAR'ow, ktore wystepuja przed atrybutami danego interfejsu (np. "    Host name . . . . : XXXX")
            data = ''.join(data)                    # Laczymy tablice charow ponownie w string otrzymujemy np. "HostName...............:XXXXXXXXX"
            data = data.split('.', 1)               # Dzielimy kazdy atrybut na dwa tylko po pierwszej napotkanej kropce (np. ["HostName", "...........:XXXXXXX"])
            if data[0].isdigit():                   # Jakies dane atrybutu byly przedluzeniem poprzedniej nazwy to sklejamy przypadkowe rozciecia (np. ["192", "100.1.1"])
                data[1] = data[0] + "." + data[1]
                data[0] = ""
            if len(data) == 1:                      # Sprawdzamy czy dane dane maja nazwe atrybutu w przeciwnym przypadku dodajemy pusta nazwe przed dane
                data.insert(0, "")
            if ":" in data[1]:
                data[1] = data[1].split(":",1)[1]   # Z danych kazdego atrybuta usuwamy kropki przed danymi oraz dwukropek (np. ["Nazwa atrybutu", "Dane_atrybutu"])
            temp_dictionary[data[0]] = data[1]
    final_data[main_key] = temp_dictionary
    return final_data


#%%

main()
