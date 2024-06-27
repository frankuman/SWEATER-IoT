import dht
from machine import Pin, ADC
import time

tempSensor = dht.DHT11(Pin(26))
adc = ADC(27)
sf = 4095 / 65535  # Scale factor
volt_per_adc = 3.3 / 4095

def temp():
    mv = adc.read_u16()
    adc_12b = mv * sf
    volt = adc_12b * volt_per_adc

    dx = abs(50 - 0)
    dy = abs(0 - 0.5)
    shift = volt - 0.5
    temp = shift / (dy / dx)
    
    return temp

def measure_temp_humidity():
    tempSensor.measure()
    temperature = tempSensor.temperature()
    humidity = tempSensor.humidity()
    return temperature, humidity

led = Pin("LED", Pin.OUT)
ledG1 = Pin(0, Pin.OUT)
ledG2 = Pin(1, Pin.OUT)
ledG3 = Pin(2, Pin.OUT)
ledY1 = Pin(3, Pin.OUT)
ledY2 = Pin(4, Pin.OUT)
ledY3 = Pin(5, Pin.OUT)
ledR1 = Pin(6, Pin.OUT)
ledR2 = Pin(7, Pin.OUT)
ledR3 = Pin(8, Pin.OUT)
def flash_lights(times):
    for i in range(times):
        print(f"{i} Testing lights . . .")
        ledG1.high()
        time.sleep(0.1)
        ledG2.high()
        ledG1.low()
        time.sleep(0.1)
        ledG3.high()
        ledG2.low()
        time.sleep(0.1)
        ledY1.high()
        ledG3.low()
        time.sleep(0.1)
        ledY2.high()
        ledY1.low()
        time.sleep(0.1)
        ledY3.high()
        ledY2.low()
        time.sleep(0.1)
        ledR1.high()
        ledY3.low()
        time.sleep(0.1)
        ledR2.high()
        ledR1.low()
        time.sleep(0.1)
        ledR3.high()
        ledR2.low()
        time.sleep(0.1)
        ledR2.high()
        ledR3.low()
        time.sleep(0.1)
        ledR1.high()
        ledR2.low()
        time.sleep(0.1)
        ledY3.high()
        ledR1.low()
        time.sleep(0.1)
        ledY2.high()
        ledY3.low()
        time.sleep(0.1)
        ledY1.high()
        ledY2.low()
        time.sleep(0.1)
        ledG3.high()
        ledY1.low()
        time.sleep(0.1)
        ledG2.high()
        ledG3.low()
        time.sleep(0.1)
        ledG1.high()
        ledG2.low()
def set_lights(curr_temp):
    ledG1.low()
    ledG2.low()
    ledG3.low()
    ledY1.low()
    ledY2.low()
    ledY3.low()
    ledR1.low()
    ledR2.low()
    ledR3.low()
    
    if 15 <= curr_temp < 17:
        ledG1.high()
    elif 17 <= curr_temp < 19:
        ledG2.high()
    elif 19 <= curr_temp < 21:
        ledG3.high()
    elif 21 <= curr_temp < 23:
        ledY1.high()
    elif 23 <= curr_temp < 25:
        ledY2.high()
    elif 25 <= curr_temp < 27:
        ledY3.high()
    elif 27 <= curr_temp < 29:
        ledR1.high()
    elif 29 <= curr_temp < 31:
        ledR2.high()
    elif curr_temp >= 31:
        ledR3.high()