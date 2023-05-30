# 1 # 1 # 1 # 1 # 1 # 1 # 1 # 1 # 1 # 1
from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import time
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import urllib3
# 2 # 2 # 2 # 2 # 2 # 2 # 2 # 2 # 2 # 2
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 

# 3 # 3 # 3 # 3 # 3 # 3 # 3 # 3 # 3 # 3
df = pd.read_csv('your csv file', sep=';') 

# 4 # 4 # 4 # 4 # 4 # 4 # 4 # 4 # 4 # 4
n=0                                                             

# 5 # 5 # 5 # 5 # 5 # 5 # 5 # 5 # 5 # 5
@dataclass              
class Empro:
    
    nom: str
    type: str
    voltage_U12: float
    voltage_U23: float
    voltage_U31 :float

# 6 # 6 # 6 # 6 # 6 # 6 # 6 # 6 # 6 # 6
with InfluxDBClient(url="your PLC", token="your influx token", org="pxc", verify_ssl=False) as client:
    # 7 # 7 # 7 # 7 # 7 # 7 # 7 # 7 # 7 # 7
    write_api = client.write_api(write_options=SYNCHRONOUS)

    
# 8 # 8 # 8 # 8 # 8 # 8 # 8 # 8 # 8 # 8
while True:
    # 9 # 9 # 9 # 9 # 9 # 9 # 9 # 9 # 9 # 9
    for i in range(460):    
        
        # 10 # 10 # 10 # 10 # 10 # 10 # 10 # 10
        n=n+1

        # 11 # 11 # 11 # 11 # 11 # 11 # 11 # 11
        voltage_U12=df.at[n,'EMpro1.Voltage_U12']
        voltage_U23=df.at[n,'EMpro1.Voltage_U23']
        voltage_U31=df.at[n,'EMpro1.Voltage_U31']

        # 12 # 12 # 12 # 12 # 12 # 12 # 12 # 12
        empro = Empro('Capteur', 'Empro', float(voltage_U12), float(voltage_U23), float(voltage_U31))
        
        # 13 # 13 # 13 # 13 # 13 # 13 # 13 # 13 
        print('\n',empro,' n = ',n,'\n')

        # 14 # 14 # 14 # 14 # 14 # 14 # 14 # 14
        write_api.write(bucket="louis_bucket",
                        record=empro,
                        record_measurement_name="meusures",
                        record_tag_keys=["nom", "type"],
                        record_field_keys=["voltage_U12","voltage_U23","voltage_U31"])
        
        # 15 # 15 # 15 # 15 # 15 # 15 # 15 # 15 
        time.sleep(1)
