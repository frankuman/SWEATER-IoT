import ubinascii
import machine

SSID = 'ssid'             #change this
PASSWORD = 'password'  #change this

MQTT_BROKER = '192.168.0.101'
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_TOPIC = 'home/temperature'
MQTT_TOPIC_SUB = 'home/control'
MQTT_TOPIC_TIME_REQ = 'home/time/request'
MQTT_TOPIC_TIME_RESP = 'home/time/response'
