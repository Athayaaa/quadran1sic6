import network
import time
import json
from machine import Pin, time_pulse_us
from umqtt.simple import MQTTClient
import dht

# Konfigurasi WiFi
WIFI_SSID = "ath"
WIFI_PASSWORD = "abcdabcd"

# Konfigurasi Ubidots
UBIDOTS_TOKEN = "BBUS-yBUiFHIde8IM2WN63jlRn6vzFlXgbj"
DEVICE_LABEL = "njajal"
VARIABLE_DISTANCE = "distance"
VARIABLE_TEMPERATURE = "temperature"

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

def mqtt_connect():
    broker = "things.ubidots.com"
    port = 1883
    username = UBIDOTS_TOKEN
    password = ""

    client_id = b"esp32_mqtt_" + bytes(str(time.ticks_ms()), 'utf-8')
    topic = b"/v1.6/devices/" + DEVICE_LABEL.encode('utf-8')

    client = MQTTClient(client_id, broker, port, username, password)
    client.connect()
    print("MQTT Connected to", broker)
    return client, topic

def measure_distance():
    trigger.value(0)
    time.sleep_us(2)
    
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)

    durasi = time_pulse_us(echo, 1, 30000)  # Timeout 30ms (~5 meter max)
    
    if durasi < 0:
        print("Sensor tidak mendapatkan pantulan")
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

def send_to_ubidots_mqtt(client, topic, distance, temperature):
    payload = {}
    
    if distance is not None:
        payload[VARIABLE_DISTANCE] = distance
    if temperature is not None:
        payload[VARIABLE_TEMPERATURE] = temperature

    if payload:
        json_payload = json.dumps(payload)
        try:
            client.publish(topic, json_payload)
            print("Published:", json_payload)
        except Exception as e:
            print("Error saat mengirim data via MQTT:", e)

def main():
    connect_wifi()
    client, topic = mqtt_connect()
    
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

        send_to_ubidots_mqtt(client, topic, distance, temperature)
        time.sleep(1)

main()
