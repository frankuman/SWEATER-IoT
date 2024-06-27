# main.py
import time
import ntptime
from machine import Pin
from config import MQTT_BROKER, MQTT_CLIENT_ID, MQTT_TOPIC
from communication import connect_wifi, mqtt_publish, mqtt_subscribe, get_outside_temp, get_weather_data
from sensors import temp, measure_temp_humidity, flash_lights, set_lights
from display import display_message
from utils import adjusted_time, format_date, format_time, format_day_of_week
from simple import MQTTClient
# Initialize LEDs

def always_run():


    flash_lights(2)
    
 

    print("Starting . . .")
    flash_lights(2)
    connect_wifi()
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER)
    client.connect()
    mqtt_subscribe(client)
    print("Setting time")
    while True: #Sometimes OSerror on NTP time
        try:
            ntptime.settime()
            break
        except Exception as e:
            print("Trying to fetch time again...")
    print(adjusted_time())

    def main_loop():
        counter = 0
        temp_str = "Temp: --.-C"
        while True:
            
            current_time = adjusted_time()
            date_str = format_date(current_time)
            day_str = format_day_of_week(current_time)
            time_str = format_time(current_time)
            
            if counter % 30 == 0:
                tmpsensor1 = temp()
                outside_temp_str = get_outside_temp()
                outside_temp_str = f"Outside Temp: {outside_temp_str}C"
                print("Sensor 1: ", tmpsensor1)
                try:
                    temperature, humidity = measure_temp_humidity()
                    
                    print("Sensor 2: tmp ", temperature, " humidity: ", humidity)
                    set_lights((tmpsensor1 + temperature) / 2)
                    message = f"{(tmpsensor1 + temperature) / 2}"
                    temp_str = "Inside  Temp: {:.1f}C".format((tmpsensor1 + temperature) / 2)
                except Exception as error:
                    print("Sensor 2: Exception occurred", error)
                    set_lights(tmpsensor1)
                    message = f"{tmpsensor1}"
                    temp_str = "Inside  Temp: {:.1f}C".format(tmpsensor1)

                try:
                    mqtt_publish(client, MQTT_TOPIC, message)
                except Exception as error:
                    print("/--/ Could not send via MQTT")
            
            set_lights((tmpsensor1 + temperature) / 2)
            print(date_str, day_str, time_str, temp_str)
            date_str = f"{date_str}:{day_str}"
            if counter % 6 == 0 or counter % 6 == 1 or counter % 6 == 2:
                wind_speed, outside_humidity, forecast_avg_temp, chance_of_rain = get_weather_data()
                toptext = f"     w:{wind_speed} h:{outside_humidity}"
                bottomtext = f"fcast:{forecast_avg_temp} rain%:{chance_of_rain}"
                display_message(toptext, outside_temp_str, time_str, bottomtext)
            else:
                display_message(date_str, outside_temp_str, time_str, temp_str)
            
            try:
                client.check_msg()
            except Exception as error:
                print(error)
                print("/--/ Could not check the messages via MQTT")

            counter += 1
            time.sleep(1)

    time.sleep(1)
    main_loop()
always_run()