
import paho.mqtt.client as mqtt
import random
import time
import json

# Konfigurasi MQTT
BROKER = "localhost"
PORT = 1883
NIM = "2410010448"

TOPIC_SUHU = f"iot/{NIM}/sensor/suhu"
TOPIC_RELAY = f"iot/{NIM}/aktuator/relay"
TOPIC_PWM = f"iot/{NIM}/aktuator/pwm"

# Simulasi perangkat ESP32
relay_status = "OFF"
pwm_value = 0

# Ketika berhasil terhubung ke MQTT
def on_connect(client, userdata, flags, reason_code, properties):
    print("Terhubung ke MQTT Broker!")
    client.subscribe(TOPIC_RELAY)
    client.subscribe(TOPIC_PWM)

# Menerima perintah dari Node-RED
def on_message(client, userdata, msg):
    global relay_status, pwm_value

    message = msg.payload.decode()

    if msg.topic == TOPIC_RELAY:
        if message in ["ON", "OFF"]:
            relay_status = message
            print("Relay GPIO 26:", relay_status)

    elif msg.topic == TOPIC_PWM:
        try:
            value = int(message)

            if 0 <= value <= 255:
                pwm_value = value
                print("LED GPIO 2 PWM:", pwm_value)
            else:
                print("Nilai PWM harus 0-255")

        except ValueError:
            print("Perintah PWM tidak valid")

# Membuat client MQTT
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2,
    client_id="ESP32_Simulator"
)

client.on_connect = on_connect
client.on_message = on_message

# Menghubungkan ke broker
print("Menghubungkan ke MQTT Broker...")
client.connect(BROKER, PORT, 60)

# Menjalankan MQTT di background
client.loop_start()

try:
    while True:
        # Simulasi pembacaan suhu DHT22
        suhu = round(random.uniform(25.0, 35.0), 1)

        data = {
            "suhu": suhu
        }

        # Mengirim suhu setiap 3 detik
        client.publish(TOPIC_SUHU, json.dumps(data))

        print(f"Suhu DHT22: {suhu} °C")
        print(f"Relay: {relay_status} | PWM: {pwm_value}")
        print("-----------------------------")

        time.sleep(3)

except KeyboardInterrupt:
    print("Simulator dihentikan.")

finally:
    client.loop_stop()
    client.disconnect()
