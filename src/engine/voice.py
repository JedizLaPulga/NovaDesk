import speech_recognition as sr

class VoiceEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        try:
            self.microphone = sr.Microphone()
        except Exception:
            print("No microphone detected.")

    def listen_one_shot(self):
        """
        Listens until silence is detected, then returns text.
        """
        if not self.microphone:
            return None

        try:
            with self.microphone as source:
                # Short adjustment for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                # Listen (waits for voice, then waits for silence)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            try:
                # Use Google Web Speech API (high accuracy, no local model needed)
                text = self.recognizer.recognize_google(audio)
                return text
            except sr.UnknownValueError:
                return None
            except sr.RequestError:
                return None
                
        except Exception as e:
            print(f"Voice Error: {e}")
            return None
