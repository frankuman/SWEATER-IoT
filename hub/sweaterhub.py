import json
import paho.mqtt.client as mqtt
from datetime import datetime, timedelta
from flask import Flask, request, render_template, jsonify, url_for
import threading
import time
import requests
import os
import glob
import base64
import cv2
from openai import OpenAI
import subprocess
import plotly.graph_objs as go
import pandas as pd
from configparser import ConfigParser

app = Flask(__name__)


config = ConfigParser()
config.read('config.ini')


MQTT_BROKER = config.get('MQTT', 'broker')
MQTT_TOPIC_PUB = config.get('MQTT', 'topic_pub')
MQTT_TOPIC_SUB = config.get('MQTT', 'topic_sub')
MQTT_TOPIC_TIME_REQ = config.get('MQTT', 'topic_time_req')
MQTT_TOPIC_TIME_RESP = config.get('MQTT', 'topic_time_resp')
temperature_data_file = config.get('Paths', 'temperature_data_file')
current_temperature_data = config.get('Paths', 'current_temperature_data')
image_directory = os.path.join(os.getcwd(), config.get('Paths', 'image_directory'))
print(image_directory)
alarm_time = None
latest_pred = "No prediction yet."
lock = threading.Lock()


WEATHER_API_URL = config.get('API', 'weather_url')
WEATHER_API_KEY = config.get('API', 'weather_key')
LOCATION = config.get('API', 'location')

openai_client = OpenAI(api_key=config.get('OpenAI', 'api_key'))



def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(MQTT_TOPIC_SUB)
    client.subscribe(MQTT_TOPIC_TIME_REQ)

def on_message(client, userdata, msg):
    if msg.topic == MQTT_TOPIC_SUB:
        temperature = float(msg.payload.decode())
        data = {
            'timestamp': datetime.now().isoformat(),
            'temperature': temperature
        }
        print(f"Received temperature: {temperature}")
        with open(current_temperature_data, 'a') as file:
            file.write(json.dumps(data) + "\n")
    elif msg.topic == MQTT_TOPIC_TIME_REQ:
        msg = "PEEP"
        client.publish(MQTT_TOPIC_TIME_RESP, msg)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

def start_mqtt():
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()

mqtt_thread = threading.Thread(target=start_mqtt)
mqtt_thread.start()

def alarm_trigger(weather_data):
    print("Alarm triggered! Performing the specific function.")
    message = "flash"
    client.publish(MQTT_TOPIC_PUB, message)
    capture_image()
    time.sleep(2)
    capture_image()
    time.sleep(2)
    capture_image()
    time.sleep(2)
    capture_image()
    time.sleep(2)
    capture_image()
    time.sleep(5)
    

    current_time = datetime.now().strftime("%H:%M:%S")
    image_data = convert_image_to_base64(os.path.join(image_directory, f"predictimage.jpg"))
    prediction = make_prediction(weather_data, image_data, current_time)
    print(f"Prediction at {current_time}: {prediction}")
    prediction = "pred:"+prediction
    print("... sending prediction ...")

    client.publish(MQTT_TOPIC_PUB, prediction)





def set_camera_to_auto():
    
    try:
        subprocess.run(["v4l2-ctl", "-d", "/dev/video0", "--set-ctrl=brightness=0"])
        subprocess.run(["v4l2-ctl", "-d", "/dev/video0", "--set-ctrl=contrast=16"])
        subprocess.run(["v4l2-ctl", "-d", "/dev/video0", "--set-ctrl=saturation=9"])
        subprocess.run(["v4l2-ctl", "-d", "/dev/video0", "--set-ctrl=hue=0"])
        subprocess.run(["v4l2-ctl", "-d", "/dev/video0", "--set-ctrl=gamma=188"])
        subprocess.run(["v4l2-ctl", "-d", "/dev/video0", "--set-ctrl=sharpness=7"])
        subprocess.run(["v4l2-ctl", "-d", "/dev/video0", "--set-ctrl=white_balance_automatic=1"])
        subprocess.run(["v4l2-ctl", "-d", "/dev/video0", "--set-ctrl=auto_exposure=2"])
    except Exception as e:
        print("Couldn't set the camera settings, probably using other camera or something")
        print(e)

def capture_image(test=False):
    try:
        set_camera_to_auto()

        cap = cv2.VideoCapture('/dev/video0', cv2.CAP_V4L2)  # change to '/dev/video1' if necessary

        if not cap.isOpened():
            print("Error: Could not open camera.")
            return

        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        cap.set(cv2.CAP_PROP_FPS, 5)

        time.sleep(5)

        for _ in range(10):
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                cap.release()
                return

        ret, frame = cap.read()
        if ret:
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            save_directory = image_directory
            if test==True:
                file_path = os.path.join(save_directory, f"testimage.jpg")
            else:
                file_path = os.path.join(save_directory, f"predictimage.jpg")

            if not os.path.exists(save_directory):
                os.makedirs(save_directory)

            cv2.imwrite(file_path, frame)
            print(f"Image captured and saved to {file_path}")
        else:
            print("Error: Could not read frame.")
    except Exception as e:
        print(f"Exception occurred: {e}")
    finally:
        if cap.isOpened():
            cap.release()



def store_api_temp():
    with lock:
        print("Fetching temperature data from API")
        try:
            response = requests.get(f"{WEATHER_API_URL}?key={WEATHER_API_KEY}&q={LOCATION}&days=1&aqi=yes&alerts=no")
            data = response.json()
            current_weather = data['current']
            forecast_weather = data['forecast']['forecastday'][0]['day']

            current_temp = current_weather['temp_c']
            feels_like = current_weather['feelslike_c']
            wind_speed = current_weather['wind_kph']
            humidity = current_weather['humidity']
            air_quality_index = current_weather['air_quality']['us-epa-index']

            forecast_avg_temp = forecast_weather['avgtemp_c']
            forecast_humidity = forecast_weather['avghumidity']
            chance_of_rain = forecast_weather['daily_chance_of_rain']

            print("-----------------------------------")
            print(f"Current temperature: {current_temp}°C")
            print(f"Feels like: {feels_like}°C")
            print(f"Wind: {wind_speed} kph")
            print(f"Humidity: {humidity}%")
            print(f"Air Quality Index: {air_quality_index}")
            print(f"Forecast - Avg Temperature: {forecast_avg_temp}°C")
            print(f"Forecast - Humidity: {forecast_humidity}%")
            print(f"Forecast - Chance of Rain: {chance_of_rain}%")

            weather_data = {
                'timestamp': datetime.now().isoformat(),
                'current_temp': current_temp,
                'feels_like': feels_like,
                'wind_speed': wind_speed,
                'humidity': humidity,
                'air_quality_index': air_quality_index,
                'forecast_avg_temp': forecast_avg_temp,
                'forecast_humidity': forecast_humidity,
                'chance_of_rain': chance_of_rain
            }
            with open(temperature_data_file, 'a') as file:
                file.write(json.dumps(weather_data) + "\n")

            return weather_data

        except Exception as e:
            print(f"Failed to fetch temperature data: {e}")
            return None

def send_api_temp(message):
    print("... Sending Temperature ...")
    client.publish(MQTT_TOPIC_PUB, message)

def convert_image_to_base64(image_path):
    print(f"Making prediction with image {image_path}")

    with open(image_path, 'rb') as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded_image}"



def make_prediction(weather_data, image_data, timestamp):
    current_temp = weather_data['current_temp']
    feels_like = weather_data['feels_like']
    wind_speed = weather_data['wind_speed']
    humidity = weather_data['humidity']
    air_quality_index = weather_data['air_quality_index']
    forecast_avg_temp = weather_data['forecast_avg_temp']
    forecast_humidity = weather_data['forecast_humidity']
    chance_of_rain = weather_data['chance_of_rain']

    prompttext = (
        f"The current weather conditions are:\n"
        f"Temperature: {current_temp}°C\n"
        f"Feels like: {feels_like}°C\n"
        f"Wind: {wind_speed} kph\n"
        f"Humidity: {humidity}%\n"
        f"Air Quality Index: {air_quality_index}\n"
        f"Forecast - Avg Temperature: {forecast_avg_temp}°C\n"
        f"Forecast - Humidity: {forecast_humidity}%\n"
        f"Forecast - Chance of Rain: {chance_of_rain}%\n"
        f"Time - Time is: {timestamp}%\n"

        f"Based on this and the image, predict the most appropriate clothing from 1 to 9 where:\n"
        "1 - Tshirt and shorts\n"
        "2 - Tshirt and pants\n"
        "3 - Longshirt and pants\n"
        "4 - Hoodie and pants\n"
        "5 - Light jacket and pants\n"
        "6 - Light jacket and hoodie and pants OR raining clothes\n"
        "7 - Heavy jacket and pants\n"
        "8 - Heavy jacket and hoodie and pants\n"
        "9 - Snowstorm, don't go outside\n"
        "Provide ONLY the prediction as a number from 1 to 9."
    )

    prompt = {
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": image_data}},
            {"type": "text", "text": prompttext}
        ]
    }

    print(prompttext)
    print("\n---------------------------------------------------------------------------")

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[prompt],
        temperature=0.5,
        max_tokens=36,
        top_p=1,
        frequency_penalty=1,
        presence_penalty=0
    )

    print(response.choices[0].message.content)

    prediction = response.choices[0].message.content

    prediction_list = [
        "1 - Tshirt and shorts",
        "2 - Tshirt and pants",
        "3 - Longshirt and pants",
        "4 - Hoodie and pants",
        "5 - Light jacket and pants",
        "6 - Light jacket and hoodie and pants OR raining clothes",
        "7 - Heavy jacket and pants",
        "8 - Heavy jacket and hoodie and pants",
        "9 - Snowstorm, don't go outside"
    ]
    
    try:
        prediction_index = int(prediction) - 1
        if 0 <= prediction_index < len(prediction_list):
            prediction_text = prediction_list[prediction_index]
        else:
            prediction_text = "Invalid prediction"
    except ValueError:
        prediction_text = "Invalid prediction"
    global latest_pred
    latest_pred = prediction_text
    return prediction

def check_alarm_time():
    global alarm_time
    global last_prediction_time
    counter = 0
    print("Starting check_alarm_time thread")
    while True:
        current_time = datetime.now()

        if alarm_time:
            if current_time.strftime("%H:%M") == alarm_time:
                weather_data = store_api_temp()
                try:
                    alarm_trigger(weather_data)
                except Exception as e: #use latest data if api call didnt work
                    with open(temperature_data_file, 'r') as file:
                        lines = file.readlines()
                    if lines:
                        weather_data = json.loads(lines[-1])
                    alarm_trigger(weather_data)
                alarm_time = None

        if counter % 300 == 0:  # every 5 minutes right now, can be updates
            weather_data = store_api_temp()
            if weather_data:
                current_temp = weather_data['current_temp']
                send_api_temp(f"2:{current_temp}")
                if alarm_time == None:
                    wind_speed = weather_data['wind_speed']
                    humidity = weather_data['humidity']
                    forecast_avg_temp = weather_data['forecast_avg_temp']
                    chance_of_rain = weather_data['chance_of_rain']
                    LCD_TEXT = f"wd:Wind:{wind_speed}|Humidity:{humidity}|forecast:{forecast_avg_temp}|rain%:{chance_of_rain}"
                    client.publish(MQTT_TOPIC_PUB, LCD_TEXT)

            else: #if api call failed send latest temp with X indicating error
                with open(temperature_data_file, 'r') as file:
                    lines = file.readlines()
                if lines:
                    weather_data = json.loads(lines[-1])
                    current_temp = weather_data['current_temp']
                    send_api_temp(f"2:{current_temp}X")

        counter += 1
        time.sleep(1)

alarm_thread = threading.Thread(target=check_alarm_time)
alarm_thread.start()
app.alarm_thread_started = True

@app.route('/')
def index():
    capture_image(test=True)
    return render_template('index.html')

@app.route('/set_time', methods=['POST'])
def set_alarm():
    global alarm_time
    alarm_time = request.form['alarm_time']
    alarm_message = "at:"+alarm_time
    print("... sending alarm time ...")
    client.publish(MQTT_TOPIC_PUB, alarm_message)
    return jsonify({'status': 'success', 'alarm_time': alarm_time})

@app.route('/get_temperature_data', methods=['GET'])
def get_temperature_data():
    with open(current_temperature_data, 'r') as file:
        lines = file.readlines()
    if lines:
        latest_data = json.loads(lines[-1])
        return jsonify(latest_data)
    else:
        return jsonify({"error": "No temperature data available"}), 404

@app.route('/get_outside_temperature_data', methods=['GET'])
def get_outside_temperature_data():
    with open(temperature_data_file, 'r') as file:
        lines = file.readlines()
    if lines:
        latest_data = json.loads(lines[-1])
        return jsonify(latest_data)
    else:
        return jsonify({"error": "No temperature data available"}), 404

@app.route('/send_control', methods=['POST'])
def send_control():
    message = request.form['message']
    if message == "alarm":
        weather_data = store_api_temp()
        if weather_data:
            current_temp = weather_data['current_temp']
            send_api_temp(f"2:{current_temp}")
        alarm_trigger(weather_data)
        return jsonify({'status': 'success', 'message': message})      
    client.publish(MQTT_TOPIC_PUB, message)
    return jsonify({'status': 'success', 'message': message})
@app.route('/history')
def history():
    return render_template('history.html')
@app.route('/get_latest_pred')
def get_pred():
    global latest_pred
    return jsonify(latest_pred)
@app.route('/get_historical_data', methods=['GET'])
def get_historical_data():
    current_time = datetime.utcnow()
    cutoff_time = current_time - timedelta(hours=23, minutes=59)
    
    with open(temperature_data_file, 'r') as file:
        lines = file.readlines()
    outside_data = [json.loads(line) for line in lines if datetime.fromisoformat(json.loads(line)['timestamp']) > cutoff_time]

    outside_timestamps = [datetime.fromisoformat(entry['timestamp']).strftime('%H:%M:%S') for entry in outside_data]
    current_temps = [entry['current_temp'] for entry in outside_data]
    feels_like = [entry['feels_like'] for entry in outside_data]
    wind_speeds = [entry['wind_speed'] for entry in outside_data]
    humidities = [entry['humidity'] for entry in outside_data]

    with open(current_temperature_data, 'r') as file:
        lines = file.readlines()
    inside_data = [json.loads(line) for line in lines if datetime.fromisoformat(json.loads(line)['timestamp']) > cutoff_time]

    inside_timestamps = [datetime.fromisoformat(entry['timestamp']).strftime('%H:%M:%S') for entry in inside_data]
    inside_temps = [entry['temperature'] for entry in inside_data]

    inside_trace = go.Scatter(x=inside_timestamps, y=inside_temps, mode='lines', name='Inside Temp')
    outside_trace = go.Scatter(x=outside_timestamps, y=current_temps, mode='lines', name='Outside Temp')
    feels_like_trace = go.Scatter(x=outside_timestamps, y=feels_like, mode='lines', name='Feels Like Temp')
    wind_speed_trace = go.Scatter(x=outside_timestamps, y=wind_speeds, mode='lines', name='Wind Speed')
    humidity_trace = go.Scatter(x=outside_timestamps, y=humidities, mode='lines', name='Humidity')

    inside_layout = go.Layout(title='Inside Temperature', xaxis=dict(title='Time'), yaxis=dict(title='Temperature (°C)'))
    outside_layout = go.Layout(title='Outside Temperature', xaxis=dict(title='Time'), yaxis=dict(title='Temperature (°C)'))
    feels_like_layout = go.Layout(title='Feels Like Temperature', xaxis=dict(title='Time'), yaxis=dict(title='Feels Like Temp (°C)'))
    wind_speed_layout = go.Layout(title='Wind Speed', xaxis=dict(title='Time'), yaxis=dict(title='Wind Speed (kph)'))
    humidity_layout = go.Layout(title='Humidity', xaxis=dict(title='Time'), yaxis=dict(title='Humidity (%)'))

    inside_graph = {'data': [inside_trace], 'layout': inside_layout}
    outside_graph = {'data': [outside_trace], 'layout': outside_layout}
    feels_like_graph = {'data': [feels_like_trace], 'layout': feels_like_layout}
    wind_speed_graph = {'data': [wind_speed_trace], 'layout': wind_speed_layout}
    humidity_graph = {'data': [humidity_trace], 'layout': humidity_layout}

    inside_graph_dict = go.Figure(inside_graph).to_dict()
    outside_graph_dict = go.Figure(outside_graph).to_dict()
    feels_like_graph_dict = go.Figure(feels_like_graph).to_dict()
    wind_speed_graph_dict = go.Figure(wind_speed_graph).to_dict()
    humidity_graph_dict = go.Figure(humidity_graph).to_dict()

    return jsonify({
        'inside': inside_graph_dict,
        'outside': outside_graph_dict,
        'feels_like': feels_like_graph_dict,
        'wind_speed': wind_speed_graph_dict,
        'humidity': humidity_graph_dict
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
