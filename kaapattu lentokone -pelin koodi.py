import mysql.connector
import random
from geopy import distance

yhteys = mysql.connector.connect(
    host='127.0.0.1',
    port=3306,
    database='flight_game',
    user='root',
    password='inajk270A',
    autocommit=True
)


# funktio hakee Euroopan suljettujen kenttien ICAOt, nimen, koordinaatit ja sijaintimaan:

def all_airports():
    sql = '''(SELECT ident, airport.name, latitude_deg, longitude_deg, country.name
    FROM airport, country
    WHERE airport.iso_country = country.iso_country and 
    airport.continent = 'EU' and airport.type ='closed');'''
    kursori = yhteys.cursor()
    kursori.execute(sql)
    tulos = kursori.fetchall()
    return tulos


# funktio pelaajan tietojen lisäämisee
def user_info(username, points, player_location):
    sql = '''insert into userinfo (user_name, points, location)
          values ("{}", "{}", "{}");'''.format(username, points, player_location)
    kursori = yhteys.cursor()
    kursori.execute(sql)


username = input('Syötä käyttäjänimesi (max 10 merkkiä):\n')

# käyttäjänimen rajotukset, pitää olla 1-10 merkkiä pitkä

while username == '' or len(username) > 10:
    if username == '':
        username = input('Käyttäjänimen täytyy sisältää vähintään yksi merkki, valitse uusi käyttäjänimi:\n')
    elif len(username) > 10:
        username = input('Käyttäjänimi on liian pitkä, valitse uusi käyttäjänimi:\n')

# peli alkaa helsinki-vantaalta ja alkupisteitä on 6kpl
player_location = 'EFHK'
points = 6

kursori = yhteys.cursor()
kursori.execute('''SELECT * FROM userinfo where user_name = "{}";'''.format(username))


if len(kursori.fetchall()) > 0:
    kursori.execute('''DELETE  FROM userinfo WHERE user_name = "{}";'''.format(username))
    user_info(username, points, player_location)
else:
    user_info(username, points, player_location)


# valitsee 15 random kenttää:
possible_locations = random.sample(all_airports(), 15)

# valitsee 15:sta kentästä sijainnit kaapatulle koneelle ja pahikselle:
airplane_loc, villain_loc = random.choice(possible_locations), random.choice(possible_locations)
# print(*airplane_loc, *villain_loc)

# pahis ja lentokone ei saa olla samalla kentällä, hakee siis patongille uuden sijainnin jos näin käy:
while villain_loc[0] == airplane_loc[0]:
    villain_loc = random.choice(possible_locations)


# funktio arpoo pahikselle uuden lokaation joka kerta kun koodin ajaa
def change_villainloc(villain_icao):
    sql = '''UPDATE pahis 
    SET location = "{}";'''.format(villain_icao)
    kursori = yhteys.cursor()
    kursori.execute(sql)
    yhteys.commit()
    return


villain = "Patonki"
villain_icao = villain_loc[0]

change_villainloc(villain_icao)

# sit alkuprintti ohjeineen, tätä nyt voi modailla ku kirjottelin vaan jotain
print(f'''
Hei {username}! Kuten jo varmasti tiedät, kaapattiin lentokone Euroopan yllä toissailtana.
Tietojemme mukaan lentokone on piilotettu jollekin Euroopan suljetuista lentokentistä. 
Koska omaat erityisen taidon jäljittää lentokoneita, olet ainoa toivomme.
Lähtiessäsi saat kuusi pistettä käyttöösi, jotka mahdollistavat lentämisen lentokentältä toiselle.
Yhteen lentomatkaan kuluu yksi piste, joten muista valita kohteesi tarkoin ennen kuin pisteesi loppuvat!
Matkasi alkaa Helsinki-Vantaan lentoasemalta.
''')

# Pistetuloste ja lentokenttävaihtoehdot:
print(f'Lähtöpisteesi: 6 kpl.\n')
print('Lentokenttävaihtoehdot: ')
for kentta in possible_locations:
    print(f'Nimi: {kentta[1]}, Maa: {kentta[4]}, ICAO-koodi: {kentta[0]}')


# Pelaajan ensimmäinen lentokenttävalinta:
destination = input('\nMiltä lentokentältä haluat aloittaa etsimisen? Syötä valitsemasi lentokentän ICAO-koodi:\n').upper()


# funktio etsii tietokannasta pelaajan syöttämää ICAO-koodia vastaavan kentän ja palauttaa kentän nimen ja koordinaatit
def travel(destination):
    tuple = (destination,)
    sql = '''(SELECT name, latitude_deg, longitude_deg
    FROM airport
    WHERE ident = %s)'''
    kursori = yhteys.cursor()
    kursori.execute(sql, tuple)
    tulos = kursori.fetchone()
    return tulos


#kysyy käyttäjältä icaota uudestaan niin pitkään että se on syötetty oikein
while destination:
    if any(destination in i for i in possible_locations):
        travel(destination)
        break
    elif destination == '':
        destination = input('Et syöttänyt ICAO-koodia, yritä uudelleen: \n').upper()
    else:
        destination = input('ICAO-koodi on virheellinen, syötä uudestaan: \n').upper()


# pelaajan sijainnin päivittäminen tietokantaan matkustamisen jälkeen
def location_update(destination):
    sql = '''UPDATE userinfo
    SET userinfo.location = ("{}") where user_name = ("{}")'''.format(destination, username)
    kursori = yhteys.cursor()
    kursori.execute(sql)
    tulos = kursori.fetchone()
    return tulos


# pisteiden päivitys matkustamisen jälkeen
def points_update():
    sql = '''update userinfo
    set points = points-1 where user_name = ("{}")'''.format(username)
    kursori = yhteys.cursor()
    kursori.execute(sql)
    tulos = kursori.fetchone()
    return tulos


# pisteiden haku tietokannasta
def points_now():
    sql = '''select points
    from userinfo where user_name = "{}";'''.format(username)
    kursori = yhteys.cursor()
    kursori.execute(sql)
    tulos = kursori.fetchone()
    return tulos




# looppi pyörittää peliä, lopettaa pelin jos pisteet loppuu, törmätään pahikseen tai löydetään kone
points = 6
attempts = 0
while not destination == airplane_loc[0] or destination == villain_loc[0] or points >= attempts:
    if (attempts < 5):

        if destination == villain_loc[0]:
            print('Laskeutuessasi et huomannut kiitoradalla makaavaa jättiläispatonkia, törmäsit siihen ja kuolit.')
            break

        elif destination == airplane_loc[0]:
            print('Onnittelut, löysit kaapatun lentokoneen ja voitit pelin!')
            break

    else:
        print('Pisteesi loppuivat etkä voi jatkaa etsintää, hävisit pelin.')

    attempts += 1

    # päivittää pelaajan sijainnin ja pisteet tietokantaan
    location_update(destination)
    airport = travel(destination)
    points_update()

    #print(geodesic(newport_ri, cleveland_oh).miles)
    # laske etäisyyden pelaajan nykyisen sijainnin ja kadonneen lentokoneen välillä
    etaisyys = distance.distance(airport[1:], airplane_loc[2:4]).km


    print(
        f'Matkustit onnistuneesti kentälle {airport[0]}, mutta valitettavasti kaapattu lentokone ei ole sijainnissasi.')
    print(f'Erityisten jäljitystaitojesi takia tiedät kuitenkin, että etäisyys lentokoneeseen on {round(etaisyys)} km.')
    print(f'Matkustuspisteitä sinulla on vielä jäljellä {points_now()[0]} kpl.')
    destination = input('\nMistä haluat etsiä kaapattua konetta seuraavaksi? Syötä valitsemasi lentokentän ICAO-koodi:\n').upper()

    while destination:
        if any(destination in i for i in possible_locations):
            travel(destination)
            break
        elif destination == '':
            destination = input('Et syöttänyt ICAO-koodia, yritä uudelleen: \n').upper()
        else:
            destination = input('ICAO-koodi on virheellinen, syötä uudestaan: \n').upper()