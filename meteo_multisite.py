# 1 # 1 # 1 # 1 # 1 # 1 # 1 # 1 # 1 # 1 
import requests
import datetime
import ast
import math
import geocoder
import keyboard
from collections import namedtuple
from dataclasses import dataclass
#from datetime import datetime
import pandas as pd
import time
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with InfluxDBClient(url="your PLC", token="your token", org="pxc", verify_ssl=False) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)

# 2 # 2 # 2 # 2 # 2 # 2 # 2 # 2 # 2 # 2 
n=0
production_n=0
########################################################################################################
# 3 # 3 # 3 # 3 # 3 # 3 # 3 # 3 # 3 # 3 
@dataclass
class Meteo:

    localisation:str
    orientation:str
    inclinaison:str
    ##########################
    current_temperature:float
    temperature_felt:float
    current_humidity:float
    current_precipitations:float
    current_wind_speed:float
    wind_direction:float
    wind_gust:float
    rayonnement:float
    weather_id:int
    lat:float
    lon:float
    production:float
    icon:str
    weather_description:str
    production_n:float
    sunrise_time:int
    sunset_time:int
    #heure_leve:time
    #heure_couche:time
    
########################################################################################################

# 4 # 4 # 4 # 4 # 4 # 4 # 4 # 4 # 4 # 4 
def calcul_rayonnement_solaire(date, heure, latitude, longitude, orientation_capteur, inclinaison_capteur):

    # Conversion de la latitude et de la longitude en radians
    latitude_rad = math.radians(latitude)
    longitude_rad = math.radians(longitude)
    
    # Conversion de la date en jour de l'année
    jour_annee = int(date.strftime("%j"))
    
    # Calcul de l'angle horaire
    heure_solaire = heure.hour + heure.minute / 60.0 + heure.second / 3600.0
    declinaison_solaire = 23.45 * math.sin(math.radians(360.0 * (284 + jour_annee) / 365.0))
    angle_horaire = math.radians(15.0 * (heure_solaire - 12) + longitude)
    
    # Calcul de l'angle d'élévation
    angle_elevation = math.asin(math.sin(latitude_rad) * math.sin(declinaison_solaire) + math.cos(latitude_rad) * math.cos(declinaison_solaire) * math.cos(angle_horaire))
    
    # Calcul de l'angle d'azimut
    angle_azimut = math.acos((math.sin(declinaison_solaire) * math.cos(latitude_rad) - math.cos(declinaison_solaire) * math.sin(latitude_rad) * math.cos(angle_horaire)) / math.cos(angle_elevation))
    
    # Correction de l'angle d'azimut en fonction du quadrant
    if math.sin(angle_horaire) > 0:
        angle_azimut = 2 * math.pi - angle_azimut
    
    # Calcul de l'angle d'incidence
    angle_incidence = math.acos(math.sin(angle_elevation) * math.sin(math.radians(inclinaison_capteur)) * math.cos(angle_azimut - math.radians(orientation_capteur)) + math.cos(angle_elevation) * math.cos(math.radians(inclinaison_capteur)))
    
    # Calcul du rayonnement solaire extraterrestre (ETR)
    rayonnement_ETR = 1367  # Valeur moyenne du rayonnement solaire extraterrestre
    
    # Calcul du rayonnement solaire réellement reçu par le capteur
    facteur_correction = 0.75  # Facteur de correction arbitraire
    rayonnement_reel = rayonnement_ETR * math.cos(angle_incidence) * facteur_correction
    
    return rayonnement_reel

def meteo_site(city_name,location,orientation_capteur,inclinaison_capteur,production_n):

    api_key = "your api key"  # Enter the API key you got from the OpenWeatherMap website
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    # 8 # 8 # 8 # 8 # 8 # 8 # 8 # 8 # 8 # 8 
    complete_url = base_url + "appid=" + 'd850f7f52bf19300a9eb4b0aa6b80f0d' + "&q=" + city_name  # This is to complete the base_url, you can also do this manually to checkout other weather data available

    # 11 # 11 # 11 # 11 # 11 # 11 # 11 # 11 
    response = requests.get(complete_url)
    x = response.json()

    # 12 # 12 # 12 # 12 # 12 # 12 # 12 # 12 
    # Obtention de la date actuelle
    date_actuelle = datetime.date.today()
    print("Date du jour :", date_actuelle)

    # Obtention de l'heure actuelle
    heure_actuelle = datetime.datetime.now().time()
    print("Heure actuelle :", heure_actuelle)
    #print(x)

    if x["cod"] != "404":
        y = x["main"]

        current_temperature = y["temp"]-273.15
        temperature_felt=y["feels_like"]-273.15

        z = x["weather"]
        weather_description = z[0]["description"]
        weather_id=x["weather"][0]["id"]

        current_pressure =y["pressure"] 
        current_wind_speed =x["wind"]["speed"]
        wind_gust =x['wind']['deg']

        current_humidity =x["main"]["humidity"]

        if "wind" in x and x["wind"].get("gust") is not None:
            wind_direction = x["wind"]["gust"]
        else:
            wind_direction = 0
        
        if "rain" in x and x["rain"].get("1h") is not None:
            current_precipitations = x["rain"]["1h"]
        else:
            current_precipitations = 0
        
        icon =z[0]["icon"]
        #print(icon)

        sunset_time =x['sys']['sunset']
        sunrise_time =x['sys']['sunrise']
        heure_leve = datetime.datetime.fromtimestamp(sunrise_time)
        heure_couche=datetime.datetime.fromtimestamp(sunset_time)

        # 13 # 13 # 13 # 13 # 13 # 13 # 13 # 13 
        rayonnement = calcul_rayonnement_solaire(date_actuelle, heure_actuelle, location.lat, location.lng, float(orientation_capteur), float(inclinaison_capteur))
        production=10*(rayonnement*25*0.2)*0.01 #on a 10m^2 de panneaux solaires avec un rendement de 20% | 0.007=25/3600   (on a une echelle de temps qui est 25s, et on avait des wh)
        production_n=production_n + production
        
        # 14 # 14 # 14 # 14 # 14 # 14 # 14 # 14 
        meteo=Meteo(str(city_name),int(orientation_capteur),int(inclinaison_capteur),float(current_temperature),float(temperature_felt),float(current_humidity),float(current_precipitations),float(current_wind_speed),float(wind_gust),float(wind_direction),float(rayonnement),float(weather_id),float(location.lat),float(location.lng),float(production), str(icon),str(weather_description), float(production_n),int(sunrise_time),int(sunset_time))
        print(meteo)

        # 15 # 15 # 15 # 15 # 15 # 15 # 15 # 15 
        write_api.write(bucket="meteo",
                record=meteo,
                record_measurement_name="meusures",
                record_tag_keys=["localisation", "orientation","inclinaison"],
                record_field_keys=["current_temperature","temperature_felt","current_humidity","current_precipitations","current_wind_speed","wind_gust","wind_direction","rayonnement","weather_id","lat","lon","production","icon","weather_description","production_n","sunrise_time","sunset_time"])


    return





print("--------------------------------------------------------------------")
print("Site n°1\n")
city_name1 = input("Enter city name : ")
location1 = geocoder.osm(city_name1)
orientation_capteur1 = input("Entrez l'orientation du capteur en degré :")  # Orientation du capteur solaire (en degrés)
inclinaison_capteur1 = input("Entrez l'inclinaison du capteur en degré :")  # Inclinaison du capteur solaire (en degrés)
print("--------------------------------------")
print("Site n°2\n")
city_name2 = input("Enter city name : ")
location2 = geocoder.osm(city_name2)
orientation_capteur2 = input("Entrez l'orientation du capteur en degré :")  # Orientation du capteur solaire (en degrés)
inclinaison_capteur2 = input("Entrez l'inclinaison du capteur en degré :")  # Inclinaison du capteur solaire (en degrés)


while True:
    print("--------------------------------------")
    print("Site n°1\n")
    meteo_site(city_name1,location1,orientation_capteur1,inclinaison_capteur1,production_n)
    print("--------------------------------------")
    print("Site n°2\n")
    meteo_site(city_name2,location2,orientation_capteur2,inclinaison_capteur2,production_n)

    time.sleep(40)
