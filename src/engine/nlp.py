import numpy as np
from sentence_transformers import SentenceTransformer, util

class IntentClassifier:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the NLP engine.
        Using MiniLM for fast, CPU-based embedding generation.
        """
        print("Loading AI Model... (this may take a moment first run)")
        self.model = SentenceTransformer(model_name)
        
        # Define Known Intents and their prototype phrases
        self.intents = {
            "OPEN_APP": [
                "open google chrome", "launch spotify", "start notepad", 
                "run visual studio code", "open calculator"
            ],
            "SEARCH_FILE": [
                "find resume.pdf", "search for holiday photos", 
                "where is the budget excel sheet", "locate my notes"
            ],
            "SYSTEM_CONTROL": [
                "volume up", "mute system", "lock screen", 
                "shutdown computer", "turn off pc"
            ],
            "WEB_SEARCH": [
                "google how to cook pasta", "search web for weather",
                "look up elon musk"
            ]
        }
        
        # Pre-compute embeddings for prototypes
        self.intent_embeddings = {}
        for intent, phrases in self.intents.items():
            self.intent_embeddings[intent] = self.model.encode(phrases)

    def predict(self, user_query):
        """
        Returns the (intent, confidence, entity) tuple.
        Entity extraction here is heuristic-based (simple string splitting) 
        until we add a dedicated NER model or regex.
        """
        query_embedding = self.model.encode(user_query)
        
        best_intent = None
        highest_score = -1.0
        
        # Compare query against all intent prototypes
        for intent, embeddings in self.intent_embeddings.items():
            # Calculate cosine similarity
            scores = util.cos_sim(query_embedding, embeddings)[0]
            max_score = float(np.max(scores))
            
            if max_score > highest_score:
                highest_score = max_score
                best_intent = intent
        
        # Simple Entity Extraction (Text after the first word typically)
        # This is a basic heuristic; can be improved.
        words = user_query.split()
        entity = " ".join(words[1:]) if len(words) > 1 else ""
        
        return best_intent, highest_score, entity

# Singleton instance for easy import
# nlp_engine = IntentClassifier() 
