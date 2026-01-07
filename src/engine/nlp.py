import os
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

class IntentClassifier:
    def __init__(self):
        """
        Initialize the NLP engine using ONNX Runtime.
        This removes the heavy PyTorch dependency.
        """
        print("Loading ONNX Model...")
        
        # Path to cached model
        model_path = os.path.join("src", "engine", "model_cache", "onnx", "model.onnx")
        tokenizer_path = os.path.join("src", "engine", "model_cache", "tokenizer.json")
        
        # Load Tokenizer
        self.tokenizer = Tokenizer.from_file(tokenizer_path)
        self.tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", length=512)
        self.tokenizer.enable_truncation(max_length=512)
        
        # Load ONNX Session
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session = ort.InferenceSession(model_path, sess_options)
        
        # Define Intents
        self.intents = {
            "OPEN_APP": ["open google chrome", "launch notepad", "start spotify"],
            "SEARCH_FILE": ["find resume.pdf", "search for budget.xlsx"],
            "SYSTEM_CONTROL": ["mute volume", "shutdown pc", "lock screen"],
            "WEB_SEARCH": ["google pizza recipe", "search youtube for cats"]
        }
        
        # Pre-compute prototype embeddings
        self.intent_embeddings = {}
        for intent, phrases in self.intents.items():
            # Average embedding of all phrases for robust prototype
            embeddings = [self.encode(p) for p in phrases]
            self.intent_embeddings[intent] = np.mean(embeddings, axis=0)

    def encode(self, text):
        """
        Runs the ONNX model to get the sentence embedding.
        """
        encoded = self.tokenizer.encode(text)
        input_ids = np.array([encoded.ids], dtype=np.int64)
        attention_mask = np.array([encoded.attention_mask], dtype=np.int64)
        token_type_ids = np.array([encoded.type_ids], dtype=np.int64)
        
        inputs = {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'token_type_ids': token_type_ids
        }
        
        # Run inference
        outputs = self.session.run(None, inputs)
        
        # Output[0] is 'last_hidden_state' (batch, seq, hidden)
        last_hidden_state = outputs[0]
        
        # Mean Pooling
        # Exclude padding tokens from average
        mask_expanded = np.expand_dims(attention_mask, -1) # (batch, seq, 1)
        sum_embeddings = np.sum(last_hidden_state * mask_expanded, axis=1)
        sum_mask = np.clip(np.sum(mask_expanded, axis=1), a_min=1e-9, a_max=None)
        mean_pooled = sum_embeddings / sum_mask
        
        # Normalize
        norm = np.linalg.norm(mean_pooled, axis=1, keepdims=True)
        return (mean_pooled / norm).flatten()

    def predict(self, user_query):
        query_embedding = self.encode(user_query)
        
        best_intent = None
        highest_score = -1.0
        
        for intent, prototype_emb in self.intent_embeddings.items():
            # Cosine Similarity
            score = np.dot(query_embedding, prototype_emb)
            if score > highest_score:
                highest_score = score
                best_intent = intent
        
        # Smart Entity Extraction (Option B)
        entity = self.extract_entity(user_query, best_intent)
        
        return best_intent, float(highest_score), entity

    def extract_entity(self, query, intent):
        """
        Cleans the query to find the actual object/software name.
        """
        clean_q = query.lower()
        
        # 1. Remove polite prefixes/filler
        stop_phrases = [
            "can you please", "could you", "would you", "please", 
            "can you", "i want to", "hey nova", "nova"
        ]
        for phrase in stop_phrases:
            clean_q = clean_q.replace(phrase, "")
            
        # 2. Identify Action Verbs based on Intent to strip them
        action_verbs = []
        if intent == "OPEN_APP":
            action_verbs = ["open", "launch", "start", "run", "fire up"]
        elif intent == "SEARCH_FILE":
            action_verbs = ["find", "search for", "search", "lookup", "locate", "where is"]
        elif intent == "WEB_SEARCH":
            action_verbs = ["google", "search web for", "look up"]
        
        # Remove the verb (and everything before it if possible)
        for verb in action_verbs:
            if verb in clean_q:
                # specific fix: split on verb and take the right side
                parts = clean_q.split(verb, 1)
                if len(parts) > 1:
                    clean_q = parts[1] # Take what comes AFTER the verb
                break
                
        # 3. Strip articles and excessive whitespace
        clean_q = clean_q.strip()
        if clean_q.startswith("the "): clean_q = clean_q[4:]
        if clean_q.startswith("a "): clean_q = clean_q[2:]
        if clean_q.startswith("an "): clean_q = clean_q[3:]
        
        return clean_q.strip()
