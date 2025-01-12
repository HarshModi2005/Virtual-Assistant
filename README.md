# README: Virtual Assistant

## Overview

The **Python Automation Toolkit** is a collection of Python scripts designed to simplify and automate various tasks. It integrates system controls, file management, application handling, and real-time weather reporting. With support for speech input and output, the toolkit provides a hands-free and intuitive user experience.

---

This is the result of a group collaboration between the contributors namely, Myself, Vedant Singh Bedi and Harsh Modi 

## Features

### 1. **Weather Information**
- Provides current temperature, rain chance, and air quality index (AQI).
- Utilizes `WeatherAPI` for accurate weather data.
- Auto-detects location to deliver precise information.

### 2. **System Operations**
- Open, close, and manage applications on macOS.
- Toggle Bluetooth on/off and check its status via AppleScript.
  
### 3. **File and Folder Management**
- Create, delete, rename, move, and list files and folders.
- Supports speech-guided interaction for file operations.
- Handles case-insensitive file and folder lookups for convenience.

---

## Dependencies

The toolkit uses several Python libraries and tools:

- `requests`: For API calls (e.g., weather data).
- `pyttsx3`: For text-to-speech functionality.
- `speech_recognition`: To capture and process voice input.
- `subprocess`: For system-level operations.
- `platform`, `os`, `shutil`: For file system and OS-specific tasks.
- `re`, `time`, `json`: For general-purpose operations.
- `datetime`, `collections`: For data management.
- `google.generativeai`: For additional generative AI features.
- macOS-specific:
  - `Foundation`, `CoreLocation`, `objc`: For location services.
  - AppleScript integration (`osascript`) for Bluetooth and app controls.

---

## Setup Instructions

1. **Install Python Dependencies**
   ```bash
   pip install requests pyttsx3 SpeechRecognition
   ```

2. **Set Up WeatherAPI**
   - Register at [WeatherAPI](https://www.weatherapi.com) and get a free API key.
   - Replace the placeholder `API_KEY` in the weather function with your key.

3. **macOS Configuration**
   - Ensure location services are enabled.
   - Allow access to the `System Preferences` and `Control Center` for AppleScript operations.

---

## Usage

### Running the Program
Execute the main script:
```bash
python main.py
```

### Example Commands
- **Weather Reporting**: "Tell me the weather."
- **Bluetooth Control**:
  - "Turn Bluetooth on."
  - "Check Bluetooth status."
- **File Management**:
  - "Create a folder named 'Projects'."
  - "Delete the file 'example.txt'."
- **Application Control**:
  - "Open Safari."
  - "Close Calendar."

### Interaction
The toolkit uses speech recognition for commands and responds via text-to-speech.

---

## Code Structure

- **`functionality_control`**: Handles weather and other utility commands.
- **`system_operations`**: Manages system-level tasks like app control and Bluetooth.
- **`file_operations`**: Handles file and folder creation, deletion, and listing.
- **Utility Functions**:
  - `text_to_speech`: Converts text into spoken words.
  - `speech_to_text`: Captures and processes spoken commands.
  - `find_path_insensitive`: Performs case-insensitive file and folder lookups.

---

## Future Enhancements

- **Cross-Platform Support**:
  - Extend functionality for Windows and Linux.
- **Enhanced Speech Recognition**:
  - Improve accuracy and support for multiple languages.
- **Dynamic API Integration**:
  - Expand beyond weather data to include other useful APIs.
- **Error Handling**:
  - Add more robust exception handling for edge cases.

---

## License

This project is open-source and available under the [MIT License](https://opensource.org/licenses/MIT).

---
