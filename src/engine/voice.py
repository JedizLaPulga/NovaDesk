import speech_recognition as sr
import threading

class VoiceEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        try:
            self.microphone = sr.Microphone()
        except OSError:
            print("No microphone detected.")

    def listen_one_shot(self):
        """
        Listens for a single command and returns the text.
        Blocking call (run in thread).
        """
        if not self.microphone:
            return None

        try:
            with self.microphone as source:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Listening...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
            print("Recognizing...")
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return "Error: API unavailable"
        except Exception as e:
            print(f"Voice Error: {e}")
            return None
