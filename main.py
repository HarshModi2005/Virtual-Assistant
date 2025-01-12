import os
import pyttsx3
import speech_recognition as sr
import subprocess
import platform
import shutil
import re
import requests
import time
import json
from datetime import datetime
from collections import defaultdict, deque
import google.generativeai as genai
from Foundation import NSObject
from CoreLocation import CLLocationManager, CLLocation, kCLAuthorizationStatusAuthorizedAlways
import objc
from fileOperations import file_operations
from systemOperations import system_operations

# Configure the Gemini API
genai.configure(api_key)  # Replace with your actual API key
model = genai.GenerativeModel("gemini-1.5-flash")

# Contextual data
context = {
    "user": {"name": None, "preferences": {}},
    "app_usage": defaultdict(int),  # Commonly used apps
    "recent_folders": deque(maxlen=10),  # Recently accessed folders
    "recent_operations": deque(maxlen=10),  # Recent operations
    "common_demands": defaultdict(int),  # Commonly requested commands
}
def get_location():
    return 30.9685, 76.5267
def find_folder(folder_name):
    """Search for a folder on the system."""
    for root, dirs, files in os.walk("/" if platform.system() != "Windows" else "C:\\"):
        for dir in dirs:
            if folder_name.lower() in dir.lower():
                return os.path.join(root, dir)
    return None
def listen_for_wake_word(wake_word="emily"):
    """Continuously listen for the wake word."""
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    print("Listening for wake word...")

    while True:
        try:
            with mic as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source)

            # Convert speech to text
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")

            # Check if the wake word is in the command
            if wake_word in command.lower():
                print("Wake word detected!")
                # text_to_speech("I'm listening. How can I assist you?")
                main()
        except sr.UnknownValueError:
            # Ignore unrecognized speech
            pass
        except sr.RequestError as e:
            print(f"Speech recognition service error: {e}")
            break
        except KeyboardInterrupt:
            print("Exiting...")
            break
# Load and save context to avoid losing history
def load_context():
    if os.path.exists("context.json"):
        try:
            with open("context.json", "r") as file:
                loaded_context = json.load(file)
            # Convert necessary fields back to their original types
            loaded_context["app_usage"] = defaultdict(int, loaded_context.get("app_usage", {}))
            loaded_context["common_demands"] = defaultdict(int, loaded_context.get("common_demands", {}))
            loaded_context["recent_folders"] = deque(loaded_context.get("recent_folders", []), maxlen=10)
            loaded_context["recent_operations"] = deque(loaded_context.get("recent_operations", []), maxlen=10)
            return loaded_context
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error loading context: {e}")
    # Return default context if file doesn't exist or is invalid
    return {
        "user": {"name": None, "preferences": {}},
        "app_usage": defaultdict(int),
        "recent_folders": deque(maxlen=10),
        "recent_operations": deque(maxlen=10),
        "common_demands": defaultdict(int),
    }


def save_context():
    context_data = {
        "user": context["user"],
        "app_usage": dict(context["app_usage"]),
        "recent_folders": list(context["recent_folders"]),
        "recent_operations": list(context["recent_operations"]),
        "common_demands": dict(context["common_demands"]),
    }
    with open("context.json", "w") as file:
        json.dump(context_data, file, indent=4)


# Context updating functions
def update_app_usage(app_name):
    if app_name not in context["app_usage"]:
        context["app_usage"][app_name] = 0
    context["app_usage"][app_name] += 1
    save_context()


def update_recent_folders(folder_path):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    context["recent_folders"].append({"folder": folder_path, "timestamp": timestamp})
    save_context()

def update_recent_operations(operation):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    context["recent_operations"].append({"operation": operation, "timestamp": timestamp})
    save_context()

def update_common_demands(command):
    context["common_demands"][command] += 1
    save_context()

# Text-to-Speech
def text_to_speech(text):
    engine = pyttsx3.init()
    engine.setProperty('voice', 'com.apple.speech.synthesis.voice.samantha')
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate-10)
    engine.say(text)
    engine.runAndWait()

# Speech-to-Text
def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio).lower()
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            text_to_speech("Sorry, I didn't catch that. Please try again.")
        except sr.RequestError:
            text_to_speech("There seems to be an issue with the speech recognition service.")
        return None



def call_gemini_api(command):
    # Convert deques to lists for JSON serialization
    serializable_context = {
        "user": context["user"],  # User details
        "app_usage": dict(context["app_usage"]),  # Convert defaultdict to a standard dict
        "recent_folders": list(context["recent_folders"]),  # Convert deque to list
        "recent_operations": list(context["recent_operations"]),  # Convert deque to list
        "common_demands": dict(context["common_demands"]),  # Convert defaultdict to a standard dict
    }
    
    # Construct the prompt with the serialized context
    prompt = f"""
    You are an assistant integrated into a macOS virtual assistant application. 
    You maintain user context to enhance usability and personalization. 
    Current context: {json.dumps(serializable_context, indent=2)}
    Command: {command}
    """
    
    try:
        # Send the prompt to the Gemini API and get the response
        response = model.generate_content(prompt)
        return response.text.strip()  # Return the response text
    except Exception as e:
        # Handle any errors during API communication
        return f"Error while communicating with Gemini API: {str(e)}"


# Find file/folder path case-insensitively
def find_path_insensitive(path):
    if os.path.exists(path):
        return path

    if os.path.isabs(path):
        directory, target = os.path.split(path)
        if os.path.exists(directory):
            for entry in os.listdir(directory):
                if entry.lower() == target.lower():
                    return os.path.join(directory, entry)
        return None

    common_locations = [
        os.getcwd(),
        os.path.expanduser("~"),
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Downloads"),
        "/Applications",
        "/Users"
    ]
    
    search_path = path.strip("/")
    
    for location in common_locations:
        try:
            for root, dirs, files in os.walk(location):
                current_depth = root[len(location):].count(os.sep)
                if current_depth > 5:
                    continue
                
                for dir_name in dirs:
                    if dir_name.lower() == search_path.lower():
                        return os.path.join(root, dir_name)
                    search_words = search_path.lower().split()
                    dir_words = dir_name.lower().split()
                    if all(word in ' '.join(dir_words) for word in search_words):
                        return os.path.join(root, dir_name)
        except (PermissionError, OSError):
            continue
            
    return None

# Process Gemini API response for speech
def process_for_speech(llm_response):
    prompt = f"""
    Please convert the following response into a concise and conversational format suitable for a voice assistant:
    {llm_response}
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error while processing for speech: {str(e)}")
        return "I'm sorry, I couldn't process the response. Please try again."


def set_volume_mac(volume_level):
    """
    Set the system volume on macOS.
    :param volume_level: Volume level (0 to 100).
    """
    if 0 <= volume_level <= 100:
        try:
            # Use the exact volume percentage directly (no macOS-specific scaling is required here).
            subprocess.run(
                ["osascript", "-e", f"set volume output volume {volume_level}"],
                check=True
            )
            print(f"Volume successfully set to {volume_level}%.")
        except subprocess.CalledProcessError as e:
            print(f"Error setting volume. Error message: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
    else:
        print("Volume level must be between 0 and 100.")
def functionality_control(command):
    """
    Perform various functionality controls including weather information.
    Currently supports:
    - Weather information (temperature, rain chance, air quality)
    """
    if "weather" in command.lower():
        try:
            # Replace with your WeatherAPI.com key (free tier)
            API_KEY = ""
            
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
# Handle user commands
def handle_command(command):
    if command is None:
        return
    if any(op in command for op in ["time"]):
                current_time = time.strftime("%I:%M %p")
                text_to_speech(f"The current time is {current_time}.")
    elif any(op in command for op in ["volume"]):
        match = re.search(r"set volume to (\d+)", command)
        if match:
            volume_level = int(match.group(1))
            print(f"Setting volume to {volume_level}...")
            if platform.system() == "Darwin":  # macOS
                set_volume_mac(volume_level)
            else:
                text_to_speech("Unsupported operating system.")
        else:
            text_to_speech("Invalid command format. Use 'set volume to <level>'.")
    elif any(op in command for op in ['weather']):
        functionality_control(command)
    elif any(op in command for op in ["find", "search"]):
        text_to_speech("Please provide the folder name you want to search for.")
        folder_name = speech_to_text()
        folder_path = find_folder(folder_name)
        if folder_path:
            text_to_speech(f"Folder '{folder_name}' found at: {folder_path}")
        else:
            text_to_speech(f"Folder '{folder_name}' not found.")
    else:
        update_common_demands(command)
        llm_response = call_gemini_api(command)
        print(f"AI Understanding: {llm_response}")

        speech_response = process_for_speech(llm_response)
        text_to_speech(speech_response)

        if "create folder" in command or "delete folder" in command or "list files" in command:
            folder_name = command.split("folder")[-1].strip()
            update_recent_folders(folder_name)
            file_operations(command)
        elif "create file" in command or "delete file" in command:
            update_recent_operations(command)
            file_operations(command)
        elif "move file" in command or "rename file" in command:
            update_recent_operations(command)
            file_operations(command)
        elif "open" in command or "close" in command or "bluetooth" in command:
            app_name = command.split("open")[-1].strip()
            update_app_usage(app_name)
            system_operations(command)
        else:
            text_to_speech("I'm not sure how to help with that. Could you please rephrase your request?")

# Main function
def main():
    global context
    context = load_context()

    if context["user"]["name"]:
        text_to_speech(f"Hello, {context['user']['name']}! How can I assist you today?")
    else:
        text_to_speech("Hello! What's your name?")
        user_name = speech_to_text()
        if user_name:
            context["user"]["name"] = user_name.capitalize()
            save_context()
            text_to_speech(f"Nice to meet you, {context['user']['name']}! How can I help you today?")

    while True:
        command = speech_to_text()
        if command:
            if "exit" in command or "quit" in command or "chup" in command:
                text_to_speech("Goodbye! and have a great day.")
                break
            handle_command(command)

if __name__ == "__main__":
    listen_for_wake_word() 
