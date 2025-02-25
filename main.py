import network
import time
import json
import urequests  # Import untuk HTTP request
from machine import Pin, time_pulse_us
import dht  # Tambahkan library DHT

# Konfigurasi WiFi
WIFI_SSID = "ath"
WIFI_PASSWORD = "abcdabcd"

# Konfigurasi Flask Server
FLASK_SERVER_URL = "http://localhost:5000/sensor1/data"

# Pin Sensor
TRIGGER_PIN = 5  
ECHO_PIN = 4     
DHT_PIN = 14  

# Inisialisasi perangkat
trigger = Pin(TRIGGER_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)
dht11 = dht.DHT11(Pin(DHT_PIN))

def connect_wifi():
    station = network.WLAN(network.STA_IF)
    station.active(True)
    if not station.isconnected():
        print("Menghubungkan ke WiFi...", WIFI_SSID)
        station.connect(WIFI_SSID, WIFI_PASSWORD)
        while not station.isconnected():
            pass
    print("WiFi Connected:", station.ifconfig())

def measure_distance():
    trigger.value(0)
    time.sleep_us(2)
    
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)

    durasi = time_pulse_us(echo, 1, 30000)  
    
    if durasi < 0:
        print("Sensor tidak mendapatkan jarak")
        return None
    
    jarak_cm = (durasi / 2) / 29.1
    return jarak_cm

def read_temperature():
    try:
        dht11.measure()
        suhu = dht11.temperature()
        return suhu
    except Exception as e:
        print("Gagal membaca suhu:", e)
        return None

def send_to_flask_api(distance, temperature):
    payload = {}
    
    if distance is not None:
        payload["distance"] = distance
    if temperature is not None:
        payload["temperature"] = temperature

    if payload:
        try:
            response = urequests.post(FLASK_SERVER_URL, json=payload)
            if response.status_code == 201:
                print("Data berhasil dikirim ke server Flask.")
            else:
                print(f"Error mengirim data ke Flask: {response.status_code}")
        except Exception as e:
            print("Error data ke server Flask:", e)

def main():
    connect_wifi()
    
    while True:
        distance = measure_distance()
        temperature = read_temperature()

        if distance is not None:
            print("Jarak: {:.2f} cm".format(distance))
        else:
            print("Jarak: None (tidak terdeteksi)")

        if temperature is not None:
            print("Suhu: {:.2f} °C".format(temperature))
        else:
            print("Suhu: None (tidak terdeteksi)")

        # Kirim data ke server Flask
        send_to_flask_api(distance, temperature)

        time.sleep(1)

main()
