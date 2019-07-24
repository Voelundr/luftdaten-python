#!/usr/bin/env python3

import sys
import os
import time
import datetime
import socket
import requests
from phpserialize import *
from threading import Thread
import numpy as np

# Import-Pfade setzen
sys.path.append(os.path.join(sys.path[0],"sds011"))
sys.path.append(os.path.join(sys.path[0],"bme280"))

from sds011 import SDS011
import Adafruit_DHT
from Adafruit_BME280 import *

# Logging
import logging
logging.basicConfig(level=logging.ERROR)
# logging.basicConfig(level=logging.DEBUG)

# Create an instance of your bme280
dusty = SDS011('/dev/ttyUSB0')
# Set dutycyle to nocycle (permanent)
dusty.dutycycle = 0

bme280 = BME280(
    address=0x77,
    t_mode=BME280_OSAMPLE_8,
    p_mode=BME280_OSAMPLE_8,
    h_mode=BME280_OSAMPLE_8,
)

data_array = []

def getSerial():
    with open('/proc/cpuinfo','r') as f:
        for line in f:
            if line[0:6]=='Serial':
                return(line[10:26])
    raise Exception('CPU serial not found')

def pushLuftdaten(url, pin, values):
    try:
        requests.post(url,
            json={
                "software_version": "python-dusty 0.0.2",
                "sensordatavalues": [{"value_type": key, "value": val} for key, val in values.items()],
            },
            headers={
                "X-PIN":    str(pin),
                "X-Sensor": sensorID,
            },
            timeout=10
        )
    except:
        pass       

def push2opensense():
    senseBox_ID = "" # your senseBox ID
    pm10_ID = "" # your senseBox PM10 sensor ID
    pm25_ID = "" # your senseBox PM25 sensor ID
    temperature_ID = "" # your senseBox temperature sensor ID
    humidity_ID = "" #  senseBox humidity sensor ID
    pressure_ID = "" # your senseBox pressure sensor ID
    ts = datetime.datetime.utcnow().isoformat("T")+"Z" # RFC 3339 Timestamp # optional # requires import datetime
    loc = {"lat": , "lng": , "height": } # location object # optional # insert your lat lng and height (optional)
    try:
        requests.post("https://api.opensensemap.org/boxes/"+senseBox_ID+"/data",
            json={
                #SDS011 P10
                pm10_ID: [data_array[0], ts, loc],
                # SDS011 P25
                pm25_ID: [data_array[1], ts, loc],                
                #BME Temp
                temperature_ID: [data_array[2], ts, loc],
                #BME Hum
                humidity_ID: [data_array[3], ts, loc],
                #BME Press
                pressure_ID: [data_array[4]/100, ts, loc], # Pressure in hPA, remove "\100" if you want the value in Pa
            },
            headers={
                "content-type": "application/json"
            },
            timeout=10 # optional 
        )            
    except:
        pass

def send_sensor_data():
    pushLuftdaten('https://api-rrd.madavi.de/data.php', 0, {
        "SDS_P1":             data_array[0],
        "SDS_P2":             data_array[1],
        "BME280_temperature": data_array[2],
        "BME280_pressure":    data_array[4],
        "BME280_humidity":    data_array[3],
    })
    pushLuftdaten('https://api.luftdaten.info/v1/push-sensor-data/', 1, {
        "P1": data_array[0],
        "P2": data_array[1],
    })
    pushLuftdaten('https://api.luftdaten.info/v1/push-sensor-data/', 11, {
        "temperature": data_array[2],
        "pressure":    data_array[4],
        "humidity":    data_array[3],
    })
    push2opensense()

def read_sensor_data():
    pm25_values = []
    pm10_values = []
    dusty.workstate = SDS011.WorkStates.Measuring
    try:
        for a in range(8):
            values = dusty.get_values()
            if values is not None:
                pm10_values.append(values[0])
                pm25_values.append(values[1])
    finally:
        dusty.workstate = SDS011.WorkStates.Sleeping

    pm25_value   = np.mean(pm25_values)
    pm10_value   = np.mean(pm10_values)
    temperature  = bme280.read_temperature()
    humidity     = bme280.read_humidity()
    pressure     = bme280.read_pressure()
    # hum2, temp2  = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 23)
    global data_array
    data_array   = [pm10_value, pm25_value, temperature, humidity, pressure, datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"), datetime.datetime.utcnow().isoformat("T")+"Z"]

def start():
    while True:
        starttime = time.time()
        read_sensor_data()
        send_sensor_data()
        time.sleep(60.0 - ((time.time() - starttime) % 60.0))

def socket_thread():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind(('localhost', 8367))
    serversocket.listen(5)
    while True:
        connection, address = serversocket.accept()
        connection.send(dumps(data_array))

sensorID  = "raspi-" + getSerial()

t1 = Thread(target = start)
t2 = Thread(target = socket_thread)

t1.start()
t2.start()
