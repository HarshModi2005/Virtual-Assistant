import os
import subprocess
import time




def system_operations(command):
    """
    Perform operations like opening or closing an application.
    app_name: Name of the application
    command: 'open' or 'close'
    """
    if "bluetooth" in command.lower():
        try:
            if "on" in command.lower():
                # AppleScript to turn Bluetooth on
                script = """
                tell application "System Preferences"
                    activate
                    set current pane to pane "com.apple.preferences.Bluetooth"
                end tell
                tell application "System Events"
                    tell process "System Preferences"
                        delay 1
                        if exists (button "Turn Bluetooth On" of window 1) then
                            click button "Turn Bluetooth On" of window 1
                        end if
                    end tell
                end tell
                tell application "System Preferences" to quit
                """
                subprocess.run(['osascript', '-e', script], check=True)
                text_to_speech("Turning Bluetooth on")
                
            elif "off" in command.lower():
                text_to_speech("Are you sure you want to turn off Bluetooth?")
                confirm = speech_to_text().strip().lower()
                
                if "yes" in confirm:
                    # AppleScript to turn Bluetooth off
                    script = """
                    tell application "System Preferences"
                        activate
                        set current pane to pane "com.apple.preferences.Bluetooth"
                    end tell
                    tell application "System Events"
                        tell process "System Preferences"
                            delay 1
                            if exists (button "Turn Bluetooth Off" of window 1) then
                                click button "Turn Bluetooth Off" of window 1
                            end if
                        end tell
                    end tell
                    tell application "System Preferences" to quit
                    """
                    subprocess.run(['osascript', '-e', script], check=True)
                    text_to_speech("Turning Bluetooth off")
                else:
                    text_to_speech("Operation cancelled")
                    
            elif "status" in command.lower():
                # AppleScript to check Bluetooth status
                script = """
                tell application "System Events"
                    tell process "ControlCenter"
                        set btStatus to value of switch "Bluetooth" of group 1 of group 1 of group 2
                        return btStatus
                    end tell
                end tell
                """
                try:
                    result = subprocess.run(['osascript', '-e', script], 
                                         capture_output=True, 
                                         text=True, 
                                         check=True)
                    status = result.stdout.strip()
                    if status == "1":
                        text_to_speech("Bluetooth is currently on")
                    else:
                        text_to_speech("Bluetooth is currently off")
                except:
                    text_to_speech("Unable to determine Bluetooth status")
                    
        except subprocess.CalledProcessError as e:
            text_to_speech(f"Error controlling Bluetooth: {str(e)}")
            
    # Existing application control code
    else:
        app_name = command.replace("open", "").replace("close", "").strip()
        app_name = app_name.capitalize()    
    if "open" in command:
        try:
            # Check in both /Applications and /System/Applications
            app_path = f"/Applications/{app_name}.app" if not app_name.lower().endswith(".app") else f"/Applications/{app_name}"
            system_app_path = f"/System/Applications/{app_name}.app" if not app_name.lower().endswith(".app") else f"/System/Applications/{app_name}"

            if os.path.exists(app_path):
                subprocess.run(["open", app_path], check=True)
            elif os.path.exists(system_app_path):
                subprocess.run(["open", system_app_path], check=True)
            else:
                raise FileNotFoundError(f"The application {app_name} could not be found.")
            
            text_to_speech(f"Opening {app_name}...")
        except Exception as e:
            print(f"Error opening {app_name}: {e}")
    
    elif "close" in command:
        text_to_speech(f"Are you sure you want to close {app_name}?")
        time.sleep(3)
        confirm = speech_to_text().strip().lower()
        if confirm == "yes":
            try:
                subprocess.run(["pkill", "-f", app_name], check=True)
                print(f"Closed {app_name}")
            except Exception as e:
                print(f"Error closing {app_name}: {e}")
        else:
            print(f"Operation to close {app_name} cancelled.")

