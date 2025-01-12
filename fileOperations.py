import os
import pyttsx3
import speech_recognition as sr
import subprocess
import platform
import re
import google.generativeai as genai
import shutil
import glob
import time
import requests
import json
from datetime import datetime
import pvporcupine
import pyaudio
import struct
from collections import defaultdict, deque
def text_to_speech(text):
    """Convert text to speech."""
    engine = pyttsx3.init()
    engine.setProperty('voice', 'com.apple.voice.compact.en-US.Samantha')
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate-10 ) 
    engine.say(text)
    engine.runAndWait()


def speech_to_text():
    """Convert speech to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            text_to_speech("Sorry, I didn't catch that. Please try again.")
            return None
        except sr.RequestError:
            text_to_speech("There seems to be an issue with the speech recognition service.")
            return None

def find_path_insensitive(path):
    """
    Find a file/directory path in a case-insensitive way for macOS.
    Returns the correct-cased path if found, None otherwise.
    """
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
def file_operations(command):
    """Perform file and folder operations."""
    
    # Creating a folder
    if "create folder" in command:
        if "in" in command:
            directory = command.split("in", 1)[1].strip()  # Get everything after "in"
        else:
            directory = command.replace("list files", "").strip()
        if not directory:
            text_to_speech("I could not get the directory name. I will make the folder in the current directory for now")
            directory = os.getcwd()
        if directory.startswith("~"):
            directory = os.path.expanduser(directory)
        actual_path = find_path_insensitive(directory)
        text_to_speech("Please provide the folder name .")
        folder_name = speech_to_text()
        if not folder_name:
            text_to_speech("Please specify the folder name like 'create folder in Folder1'.")
        else:
            folder_path = os.path.join(actual_path, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            text_to_speech(f"Folder '{folder_name}' created successfully. Let me know if there's anything else.")
        # text_to_speech("Do you want to create the folder in Documents? Please say yes or no.")
        # response = speech_to_text().lower()
        
        # if "yes" in response:
        #     parent_directory = os.path.expanduser("~/Documents")
        # else:
        #     text_to_speech("Please provide the full path where you want to create the folder.")
        #     parent_directory = speech_to_text()
        #     parent_directory = os.path.expanduser(parent_directory)
        
        # text_to_speech("Please provide the folder name.")
        # folder_name = speech_to_text()
        # folder_path = os.path.join(parent_directory, folder_name)
        
        # if os.path.exists(folder_path):
        #     text_to_speech(f"Folder '{folder_name}' already exists in the specified location.")
        # else:
        #     os.makedirs(folder_path, exist_ok=True)
        #     text_to_speech(f"Folder '{folder_name}' created successfully.")
    
    # Deleting a folder
    elif "delete folder" in command:
        text_to_speech("Please provide the folder name to delete.")
        folder_name = speech_to_text()
        folder_path = find_path_insensitive(folder_name)
        
        if folder_path and os.path.isdir(folder_path):
            try:
                os.rmdir(folder_path)
                text_to_speech(f"Folder '{folder_name}' deleted successfully.")
            except OSError:
                text_to_speech("The folder is not empty or cannot be deleted.")
        else:
            text_to_speech("Folder not found.")
    
    # Creating a file
    elif "create file" in command:
        text_to_speech("Please provide the folder name where you want to create the file.")
        folder_name = speech_to_text()
        folder_path = find_path_insensitive(folder_name)
        
        if not folder_path:
            text_to_speech("Folder not found. Do you want to create the folder? Please say yes or no.")
            response = speech_to_text().lower()
            if "yes" in response:
                folder_path = os.path.expanduser(f"~/Documents/{folder_name}")
                os.makedirs(folder_path, exist_ok=True)
                text_to_speech(f"Folder '{folder_name}' created in Documents.")
            else:
                text_to_speech("Operation cancelled.")
                return
        
        text_to_speech("Please provide the file name.")
        file_name = speech_to_text()
        text_to_speech("Please provide the file extension (e.g., txt, pdf, py).")
        file_extension = speech_to_text()
        file_extension = f".{file_extension.lstrip('.')}"
        file_path = os.path.join(folder_path, file_name + file_extension)
        
        try:
            with open(file_path, 'w') as file:
                file.write("")
            text_to_speech(f"File '{file_name}{file_extension}' created successfully in folder '{folder_name}'.")
        except Exception as e:
            text_to_speech(f"An error occurred: {str(e)}.")
    
    # Deleting a file
    elif "delete file" in command:
        text_to_speech("Please provide the folder name from where you want to delete the file.")
        folder_name = speech_to_text()
        folder_path = find_path_insensitive(folder_name)
        text_to_speech("Please provide the file name.")
        file_name = speech_to_text()
        text_to_speech("Please provide the file extension (e.g., txt, pdf, py).")
        file_extension = speech_to_text()
        file_extension = f".{file_extension.lstrip('.')}"
        file_path = os.path.join(folder_path, file_name + file_extension)
        file_path = find_path_insensitive(file_path)
        if file_path and os.path.isfile(file_path):
            try:
                os.remove(file_path)
                text_to_speech(f"File '{file_name}' deleted successfully.")
            except Exception as e:
                text_to_speech(f"Error deleting the file: {str(e)}.")
        else:
            text_to_speech("File not found.")

    elif "list files" in command:
        # Extract the directory path from the command
        if "in" in command:
            directory = command.split("in", 1)[1].strip()  # Get everything after "in"
        else:
            directory = command.replace("list files", "").strip()

        # Default to current directory if no specific directory is provided
        if not directory:
            directory = os.getcwd()

        # Expand '~' to the user's home directory
        if directory.startswith("~"):
            directory = os.path.expanduser(directory)

        # Use case-insensitive search for the directory
        actual_path = find_path_insensitive(directory)

        if not actual_path:  # If not found, search the entire system
            text_to_speech(f"Searching for the folder '{directory}' anywhere in the system. Please wait...")
            # Search for the directory across the system
            for root, dirs, _ in os.walk("/"):  # Start searching from root
                if any(dir_name.lower() == directory.lower() for dir_name in dirs):
                    actual_path = os.path.join(root, directory)
                    break

        # Check if the directory exists and list files
        if actual_path and os.path.isdir(actual_path):
            try:
                files = os.listdir(actual_path)
                if files:
                    files_list = [file.replace('.', ' dot ') for file in files if not file.startswith('.')]  # Skip hidden files
                    directory_name = os.path.basename(actual_path)
                
                    text_to_speech(f"Directory: {directory_name}.")
                    for file in files_list:
                        text_to_speech(f"{file}.")
                        time.sleep(0.5)  # Pause between file names
                    text_to_speech("Let me know if you need more help.")
                else:
                    text_to_speech(f"Directory '{os.path.basename(actual_path)}' is empty.")
            except Exception as e:
                text_to_speech(f"Error accessing the directory: {str(e)}")
        else:
            text_to_speech(f"Folder '{directory}' not found anywhere in the system. Please check the folder name and try again.")

    
    
    # Moving files
    elif "move file" in command:
        text_to_speech("Please provide the folder name from where you want to move the file.")
        folder_name = speech_to_text()
        source_folder = find_path_insensitive(folder_name)
        text_to_speech("Please provide the destination folder name.")
        folder_name = speech_to_text()
        target_folder = find_path_insensitive(folder_name)
        if not source_folder or not target_folder:
            text_to_speech("Source or destination folder not found. Please check the folder names and try again.")
            return
        text_to_speech("Please provide the file name.")
        file_name = speech_to_text()
        text_to_speech("Please provide the file extension (e.g., txt, pdf, py).")
        file_extension = speech_to_text()
        file_extension = f".{file_extension.lstrip('.')}"
        file_path = os.path.join(source_folder, file_name + file_extension)
        source_file = find_path_insensitive(file_path)
        if source_file and os.path.isfile(source_file):
            target_file = os.path.join(target_folder, os.path.basename(file_name))
            try:
                os.rename(source_file, target_file)
                text_to_speech(f"File '{file_name}' moved to folder '{os.path.basename(target_folder)}'.")
            except Exception as e:
                text_to_speech(f"Error moving the file: {str(e)}.")
        else:
            text_to_speech("File not found in the source folder.")

    elif "rename file" in command:
        text_to_speech("Please provide the folder name where the file is located.")
        folder_name = speech_to_text()
        if not folder_name:
            text_to_speech("I didn't catch the folder name. Please try again.")
            return
        folder_path = find_path_insensitive(folder_name)
        if not folder_path:
            text_to_speech(f"Could not find the folder {folder_name}. Please check the folder name.")
            return
        text_to_speech("Please provide the current file name without extension.")
        old_file_name = speech_to_text()
        if not old_file_name:
            text_to_speech("I didn't catch the file name. Please try again.")
            return
        text_to_speech("Please provide the file extension without dot (e.g., txt, pdf, py).")
        file_extension = speech_to_text()
        if not file_extension:
            text_to_speech("I didn't catch the file extension. Please try again.")
            return
        file_extension = f".{file_extension.strip().lstrip('.')}"
        old_file_found = False
        old_file_path = None
        try:
            for entry in os.listdir(folder_path):
                if entry.lower() == f"{old_file_name}{file_extension}".lower():
                    old_file_path = os.path.join(folder_path, entry)
                    old_file_found = True
                    break
        except Exception as e:
            text_to_speech(f"Error accessing the folder: {str(e)}")
            return
        if not old_file_found:
            text_to_speech(f"Could not find the file {old_file_name}{file_extension} in folder {folder_name}.")
            return  
        text_to_speech("Please provide the new file name without extension.")
        new_file_name = speech_to_text()
        if not new_file_name:
            text_to_speech("I didn't catch the new file name. Please try again.")
            return
        try:
            # Create new path preserving the directory and extension
            new_file_with_ext = f"{new_file_name}{file_extension}"
            new_file_path = os.path.join(folder_path, new_file_with_ext)
            # Check if new filename already exists
            if os.path.exists(new_file_path):
                text_to_speech(f"A file named {new_file_with_ext} already exists in this location.")
                return
            # Perform the rename operation
            os.rename(old_file_path, new_file_path)
            text_to_speech(f"File renamed from {os.path.basename(old_file_path)} to {new_file_with_ext} successfully.")
        except PermissionError:
            text_to_speech("Permission denied. Unable to rename the file.")
        except Exception as e:
            text_to_speech(f"There was an error renaming the file: {str(e)}")
            return
    else:
        text_to_speech("I can't perform that operation yet. Let me know how else I can help.")

def find_folder(folder_name):
    """Attempt to find the folder by searching in the current working directory and subdirectories."""
    for root, dirs, files in os.walk(os.getcwd()):
        if folder_name in dirs:
            return os.path.join(root, folder_name)
    return None
