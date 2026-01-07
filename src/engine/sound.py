import winsound
import threading

class SoundEngine:
    """
    Lightweight Sound Wrapper using native Windows sounds.
    Zero external dependencies.
    """
    ENABLED = False # Default OFF
    
    @staticmethod
    def play(sound_type):
        """
        Types: 'startup', 'success', 'error', 'click'
        """
        if not SoundEngine.ENABLED:
            return

        # Run in thread to ensure it never blocks the UI
        threading.Thread(target=SoundEngine._play_worker, args=(sound_type,), daemon=True).start()

    @staticmethod
    def _play_worker(sound_type):
        try:
            if sound_type == 'startup':
                # SystemLogin is the standard 'Welcome' sound
                winsound.PlaySound("SystemLogin", winsound.SND_ALIAS)
            
            elif sound_type == 'success':
                # SystemAsterisk is a pleasant 'Ding'
                winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                
            elif sound_type == 'search':
                 # SystemExclamation is a soft 'Pop'
                winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

            elif sound_type == 'error':
                # SystemHand is the 'Critical Stop' noise
                winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
                
        except Exception:
            pass # Fail silently if sound subsystem is busy
