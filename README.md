# SWEATER-IoT
**Smart Weather and Environmental Alarm for Temperature and Outfit Recommendations (SWEATER)**

## Project Overview
SWEATER-IoT is designed to provide smart recommendations for daily outfits based on current weather conditions and indoor temperatures. The system also functions as an alarm clock, displaying the current time, weather, and outfit suggestions, and allows users to set alarms and tasks via a Python Flask dashboard.

## System Architecture

```mermaid
flowchart TB
 subgraph Pico["Pico"]
        LEDScreen["Small LED Screen<br>Displays current time"]
        BigOLED["Big OLED<br>Displays weather, temperature,<br>and clothes to wear"]
        TmpSens1["Temperature Sensor 1<br>Captures inside temperature"]
        TmpSens2["Temperature Sensor 2<br>Captures inside temperature &amp; humidity"]
        LEDLights["9 LED Lights<br>Indicates clothes to wear / tasks<br>left for the day"]
        Algorithm1["Algorithm 1<br>Processes temperature data and<br>sends to Pi 4"]
  end
 subgraph RaspberryPi4["Raspberry Pi 4"]
        Pi4["Raspberry Pi 4"]
        Camera["Camera<br>Captures pictures of outside"]
        Storage["1 TB Storage<br>Stores camera feed and<br>temperature data"]
        Server["Server<br>Python Flask dashboard"]
        Dashboard["Dashboard<br>Sets alarm and tasks"]
        Algorithm2["Algorithm 2<br>Predicts clothes to wear and<br>sends alerts"]
  end
 subgraph Visualization["Visualization"]
        NotDecided["Visualization Tool<br>To be decided"]
  end

    TmpSens1 -- Data --> Algorithm1
    TmpSens2 -- Data --> Algorithm1
    Algorithm1 -- Sends data over WiFi --> Pi4
    Pi4 --> Camera & Storage & Server
    Camera --> Storage
    Server --> Dashboard
    Dashboard -- Sets alarm and tasks --> Algorithm2
    Algorithm2 -- Sends alerts and info --> BigOLED
    Algorithm2 -- Lights up --> LEDLights
    Algorithm2 -- Predicts clothes to wear --> BigOLED
    NotDecided --> Pi4
    style NotDecided stroke-width:4px,stroke-dasharray: 5
```

## Components

### Pico
- Display exact things here
### Raspberry Pi 4
- Display exact things here
  
### Visualization
- **Tool**: To be decided

## Installation and Setup
Some step by step process

## Usage

something here

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.


