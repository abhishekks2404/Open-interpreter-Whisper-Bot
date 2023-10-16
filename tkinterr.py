import tkinter as tk
import subprocess
import time
import pyautogui

import argparse
import io
import os
import speech_recognition as sr
import whisper
import torch
from datetime import datetime, timedelta
from queue import Queue
from tempfile import NamedTemporaryFile
from time import sleep
from sys import platform
import time
import pyautogui

import pygame
import base64



    

def play_mp3(file_path):
    pygame.init()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        # Keep the program running while the music is playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except pygame.error as e:
        print(f"Error playing MP3 file: {e}")

    finally:
        pygame.mixer.quit()
        pygame.quit()


mp3_file_path = "start.mp3"
mp3_file_path1 = "end.mp3"

def startinterpreter():
    subprocess.Popen(['open', '-a', 'Terminal'])
    time.sleep(1)
    pyautogui.typewrite("interpreter -y")

    time.sleep(0.5)
    pyautogui.press("enter")

    time.sleep(1)


def whisperr():
    

        
    model_options = ["tiny", "base", "small", "medium", "large"]
    selected_model = "base"
    # if selected_model:
    #     st.success("Model Loaded Successfully....")

    def record_callback(_, audio: sr.AudioData) -> None:


        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        nonlocal last_sample
        nonlocal is_recording
        if not is_recording:
            return
        # Grab the raw bytes and push it into the thread-safe queue.
        data = audio.get_raw_data()
        data_queue.put(data)

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=selected_model, help="Model to use",
                        choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--non_english", action='store_true',
                        help="Don't use the English model.")
    parser.add_argument("--energy_threshold", default=1000,
                        help="Energy level for the microphone to detect.", type=int)
    parser.add_argument("--record_timeout", default=7,
                        help="How real-time the recording is in seconds.", type=float)
    parser.add_argument("--phrase_timeout", default=2,
                        help="How much empty space between recordings before we "
                            "consider it a new line in the transcription.", type=float)
    if 'linux' in platform:
        parser.add_argument("--default_microphone", default='pulse',
                            help="Default microphone name for SpeechRecognition. "
                                "Run this with 'list' to view available Microphones.", type=str)
    args = parser.parse_args()

    # The last time a recording was retrieved from the queue.
    phrase_time = None
    # Current raw audio bytes.
    last_sample = bytes()
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = args.energy_threshold
    
    recorder.dynamic_energy_threshold = False

    start_time = time.time()
    timeout = 5

    
    source = sr.Microphone(sample_rate=16000)

    # Load / Download model
    model = args.model

    if args.model != "large" and not args.non_english:
        model = model + ".en"
    audio_model = whisper.load_model(model)

    record_timeout = args.record_timeout
    phrase_timeout = args.phrase_timeout

    temp_file = NamedTemporaryFile().name
    temp_file1 = NamedTemporaryFile().name

    transcription = ['']

    

    with source:
        recorder.adjust_for_ambient_noise(source)

    is_recording = False

# Create a background thread that will pass us raw audio bytes.
# We could do this manually but SpeechRecognizer provides a nice helper.
    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    # Record button
    

    is_recording = not is_recording


    # Display transcribed text in real-time
    for line in transcription:
        last_line = line

    last_voice_time = None
    last_print_time = None
    timeout = 4
    

    while True:
                now = datetime.utcnow()            
                if not data_queue.empty():
                    
                    phrase_complete = False
                    
                    if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                        last_sample = bytes()
                        phrase_complete = True
                    # This is the last time we received new audio data from the queue.
                    phrase_time = now

                    # Concatenate our current audio data with the latest audio data.
                    while not data_queue.empty():
                        data = data_queue.get()
                        last_sample += data

                    audio_data = sr.AudioData(last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
                    wav_data = io.BytesIO(audio_data.get_wav_data())

                    # Write wav data to the temporary file as bytes.
                    with open(temp_file, 'w+b') as f:
                        f.write(wav_data.read())

                    # Read the transcription.
                    result = audio_model.transcribe(temp_file, fp16=torch.cuda.is_available())
                    text = result['text'].strip()
                    
                    if phrase_complete:
                        transcription.append(text)
                    else:
                        transcription[-1] = text

                    # Update Streamlit display
                    for line in transcription:
                        last_line = line
                    if last_line is not None:
                        
                        print(last_line)
                        if (last_line == "stop.") or (last_line == "Stop.") or (last_line == "STOP.") or (last_line == "stop") or (last_line == "Stop"):
                            last_voice_time = None
                            last_print_time = None
                            play_mp3(mp3_file_path)
                            break

                        if (last_line == "continue.") or (last_line == "continue.") or (last_line == "Continue.") or (last_line == "continue") or (last_line == "Continue"):
                            last_voice_time = None
                            last_print_time = None
                            play_mp3(mp3_file_path)
                            while True:
                                
                                now1 = datetime.utcnow()

                                if not data_queue.empty():
                                    last_voice_time = now1
                                    print("Inside 2nd loop")

                                    phrase_complete = False
                                    # If enough time has passed between recordings, consider the phrase complete.
                                    # Clear the current working audio buffer to start over with the new data.
                                    if phrase_time and now1 - phrase_time > timedelta(seconds=phrase_timeout):
                                        last_sample = bytes()
                                        phrase_complete = True
                                    # This is the last time we received new audio data from the queue.
                                    phrase_time = now1

                                    # Concatenate our current audio data with the latest audio data.
                                    while not data_queue.empty():
                                        data = data_queue.get()
                                        last_sample += data

                                    # Use AudioData to convert the raw data to wav data.
                                    audio_data = sr.AudioData(last_sample, source.SAMPLE_RATE, source.SAMPLE_WIDTH)
                                    wav_data = io.BytesIO(audio_data.get_wav_data())

                                    # Write wav data to the temporary file as bytes.
                                    with open(temp_file1, 'w+b') as f:
                                        f.write(wav_data.read())

                                    # Read the transcription.
                                    result = audio_model.transcribe(temp_file1, fp16=torch.cuda.is_available())
                                    text = result['text'].strip()

                                    if phrase_complete:
                                        transcription.append(text)
                                    else:
                                        transcription[-1] = text

                                    # Update Streamlit display
                                    for line in transcription:
                                        last_line = line
                                    if last_line is not None:
                                        
                                        pyautogui.typewrite(last_line)
                                        print(last_line)

                                        last_print_time = now1

                                if ((last_voice_time and now1 - last_voice_time > timedelta(seconds=timeout)) and (last_print_time and now1 - last_print_time > timedelta(seconds=timeout))):
                                    print("No voice or text detected for 5 seconds, exiting loop")
                                    pyautogui.press("enter")
                                    play_mp3(mp3_file_path1)
                                    break
                                            
    
                                sleep(0.25)

                sleep(0.25)
    

def open_terminal():
    try:
        # Use open command to open the Terminal on macOS
        subprocess.Popen(['open', '-a', 'Terminal'])
        time.sleep(1)
        pyautogui.typewrite("pip3 install open-interpreter")

        time.sleep(0.5)
        pyautogui.press("enter")
        subprocess.e(['osascript', '-e', 'tell application "Terminal" to minimize every window'])

    
    except Exception as e:
        print(f"Error opening terminal: {e}")

def voice_start():
    pass

def decode_name(encoded_name):
        return base64.b64decode(encoded_name).decode()
encoded_name = "Q29kZSBpcyBmdWxseSBnZW5lcmF0ZWQgYnkgQWJoaXNoZWsgS3VtYXIgU2luZ2g="
decode_name(encoded_name)

app = tk.Tk()
app.title("Whisper with open-interpreter")

app.geometry("400x200")

terminal_button = tk.Button(app, text="Initialise Open-Interpreter", command=open_terminal)
terminal_button.pack(pady=20)  # Pack the first button

terminal_button1 = tk.Button(app, text="Start Open-Interpreter", command=startinterpreter)
terminal_button1.pack(pady=20)  # Pack the second button

terminal_button2 = tk.Button(app, text="Start Whisper", command=whisperr)
terminal_button2.pack(pady=20)

app.mainloop()
