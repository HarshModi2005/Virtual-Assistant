import requests
import pyttsx3
import speech_recognition as sr
import subprocess
import platform
import shutil
import re
import time
import json
from datetime import datetime
from collections import defaultdict, deque
import google.generativeai as genai
from Foundation import NSObject
from CoreLocation import CLLocationManager, CLLocation, kCLAuthorizationStatusAuthorizedAlways
import objc



def functionality_control(command):
    """
    Perform various functionality controls including weather information.
    Currently supports:
    - Weather information (temperature, rain chance, air quality)
    """
    if "weather" in command.lower():
        try:
            # Replace with your WeatherAPI.com key (free tier)
            API_KEY = "11d3f1abb125430c9ce195032251101"
            
            # Get current location
            text_to_speech("Getting your current location...")
            latitude, longitude = get_location()
            
            if not latitude or not longitude:
                text_to_speech("Unable to get your location. Please check your location services settings.")
                return
            
            # Get weather data from WeatherAPI.com
            url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={latitude},{longitude}&aqi=yes"
            
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                # Extract location
                location = data['location']['name']
                region = data['location']['region']
                
                # Current weather data
                current = data['current']
                temperature = round(current['temp_c'])
                feels_like = round(current['feelslike_c'])
                condition = current['condition']['text']
                
                # Air quality
                air_quality = current['air_quality']
                us_epa_index = air_quality.get('us-epa-index', 0)
                aqi_descriptions = {
                    1: "Good",
                    2: "Moderate",
                    3: "Unhealthy for sensitive groups",
                    4: "Unhealthy",
                    5: "Very Unhealthy",
                    6: "Hazardous"
                }
                
                # Get chance of rain from forecast
                forecast = data['forecast']['forecastday'][0]['day']
                chance_of_rain = forecast['daily_chance_of_rain']
                
                # Build and speak the weather report
                report = f"Current weather in {location}, {region}: "
                report += f"Temperature is {temperature}°C, feels like {feels_like}°C. "
                report += f"Conditions are {condition}. "
                report += f"Chance of rain today is {chance_of_rain}%. "
                
                if us_epa_index in aqi_descriptions:
                    report += f"Air quality is {aqi_descriptions[us_epa_index]}. "
                
                # Additional details
                humidity = current['humidity']
                wind_kph = current['wind_kph']
                report += f"Humidity is {humidity}%, "
                report += f"and wind speed is {round(wind_kph)} kilometers per hour."
                
                text_to_speech(report)
                
            else:
                text_to_speech("Sorry, I couldn't retrieve the weather information. Please check your API key and internet connection.")
                
        except requests.RequestException as e:
            text_to_speech("Sorry, there was an error connecting to the weather service. Please check your internet connection.")
            print(f"Error: {str(e)}")
            
        except Exception as e:
            text_to_speech("Sorry, there was an unexpected error getting the weather information.")
            print(f"Error: {str(e)}")
            
    else:
        text_to_speech("Sorry, I don't recognize that command.")
