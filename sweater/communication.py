import network
import main #circular import leggoo
from simple import MQTTClient
from config import SSID, PASSWORD, MQTT_BROKER, MQTT_CLIENT_ID, MQTT_TOPIC_SUB, MQTT_TOPIC_TIME_RESP
import time
from display import display_custom_message, display_alarm, display_prediction, display_on_oled
from sensors import flash_lights
outside_temp = 0
wind_speed = 0
humidity = 0
forecast_avg_temp = 0
chance_of_rain = 0
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    while not wlan.isconnected():
        print('Connecting to WiFi...')
        time.sleep(1)

    print('Connected to WiFi')
    print('Network configuration:', wlan.ifconfig())

def mqtt_publish(client, topic, message):
    try:
        client.publish(topic, message)
        print(f"Published message: {message} to topic: {topic}")
    except Exception as e:
        print(f"Failed to connect/publish to MQTT Broker: {e}")

def control_callback(topic, msg):
    topic_str = topic.decode()
    message = msg.decode()
    print(f"Received message on {topic_str}: {message}")

    if message == 'flash':
        flash_lights(1)
        print("Received flash command!")
    elif len(message) > 1 and message[0] == "2":
        global outside_temp
        outside_temp = message[2:]
        print(outside_temp)
    elif len(message) > 3 and message[0:2] == "at":
        alarmtime = message[3:]
        print("Displaying alarm")
        alarmtime = str(alarmtime)
        display_alarm(alarmtime)
    elif len(message) > 4 and message[0:4] == "pred":
        prediction = message[5:]
        print("Displaying prediction")
        display_prediction(prediction)
    elif len(message) > 4 and message[0:4] == "OLED":
        message = message[5:]
        print("Displaying OLED")
        display_on_oled(str(message))
    elif len(message) > 2 and message[0:2] == "wd":
        message = message[3:]
        parts = message.split('|')
        data_dict = {}
        
        for part in parts:
            key, value = part.split(':')
            data_dict[key] = value
        
        global wind_speed
        global humidity
        global forecast_avg_temp
        global chance_of_rain

        wind_speed = data_dict.get('Wind')
        humidity = data_dict.get('Humidity')
        forecast_avg_temp = data_dict.get('forecast')
        chance_of_rain = data_dict.get('rain%')
        
        print(f"Wind Speed: {wind_speed}, Humidity: {humidity}, Forecast: {forecast_avg_temp}, Rain Chance: {chance_of_rain}")
    else:
        print("Displaying on LCD:",message)
        display_custom_message(str(message))


def get_outside_temp():
    global outside_temp
    return outside_temp
def get_weather_data():
    global wind_speed
    global humidity
    global forecast_avg_temp
    global chance_of_rain
    return wind_speed, humidity, forecast_avg_temp, chance_of_rain
def mqtt_subscribe(client):
    client.set_callback(control_callback)
    client.subscribe(MQTT_TOPIC_SUB)
    client.subscribe(MQTT_TOPIC_TIME_RESP)
