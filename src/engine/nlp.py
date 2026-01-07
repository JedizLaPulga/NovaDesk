import os
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
import spacy
import difflib
from src.engine.knowledge_base import INTENT_DB

class IntentClassifier:
    def __init__(self):
        """
        Initialize the NLP engine using ONNX Runtime (Intent) + spaCy (Entity).
        Backed by the detailed Knowledge Base.
        """
        print("Loading ONNX Model...")
        model_path = os.path.join("src", "engine", "model_cache", "onnx", "model.onnx")
        tokenizer_path = os.path.join("src", "engine", "model_cache", "tokenizer.json")
        
        self.tokenizer = Tokenizer.from_file(tokenizer_path)
        self.tokenizer.enable_padding(pad_id=0, pad_token="[PAD]", length=512)
        self.tokenizer.enable_truncation(max_length=512)
        
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        self.session = ort.InferenceSession(model_path, sess_options)
        
        print("Loading spaCy Model...")
        self.nlp_spacy = spacy.load("en_core_web_sm")
        
        # --- Pre-compute Knowledge Base Embeddings & Vocabulary ---
        self.intent_prototypes = [] 
        self.vocab = set()
        
        print("Indexing Knowledge Base...")
        for intent_id, data in INTENT_DB.items():
            for trigger in data["triggers"]:
                # 1. Embeddings
                emb = self.encode(trigger)
                self.intent_prototypes.append((emb, intent_id))
                
                # 2. Build Vocabulary for Spell Checker
                words = trigger.lower().split()
                self.vocab.update(words)

    def correct_query(self, query):
        """
        Domain-Specific Auto-Correct.
        Fixes 'broswer' -> 'browser', 'sappotify' -> 'spotify' (if in vocab).
        """
        words = query.lower().split()
        corrected_words = []
        
        for word in words:
            if word in self.vocab:
                corrected_words.append(word)
            else:
                # Try to find a close match in our domain vocabulary
                matches = difflib.get_close_matches(word, self.vocab, n=1, cutoff=0.8)
                if matches:
                    print(f"Auto-Correct: {word} -> {matches[0]}")
                    corrected_words.append(matches[0])
                else:
                    corrected_words.append(word)
                    
        return " ".join(corrected_words)

    def encode(self, text):
        encoded = self.tokenizer.encode(text)
        input_ids = np.array([encoded.ids], dtype=np.int64)
        attention_mask = np.array([encoded.attention_mask], dtype=np.int64)
        token_type_ids = np.array([encoded.type_ids], dtype=np.int64)
        
        inputs = {
            'input_ids': input_ids, 
            'attention_mask': attention_mask,
            'token_type_ids': token_type_ids
        }
        
        outputs = self.session.run(None, inputs)
        last_hidden_state = outputs[0]
        
        mask_expanded = np.expand_dims(attention_mask, -1)
        sum_embeddings = np.sum(last_hidden_state * mask_expanded, axis=1)
        sum_mask = np.clip(np.sum(mask_expanded, axis=1), a_min=1e-9, a_max=None)
        mean_pooled = sum_embeddings / sum_mask
        
        norm = np.linalg.norm(mean_pooled, axis=1, keepdims=True)
        return (mean_pooled / norm).flatten()

    def predict(self, user_query):
        # 0. Auto-Correct Typo
        original_query = user_query
        user_query = self.correct_query(user_query)
        if user_query != original_query:
            print(f"Corrected: '{original_query}' -> '{user_query}'")
            
        query_embedding = self.encode(user_query)
        
        best_intent = None
        highest_score = -1.0
        
        # Compare against all KB triggers
        for prototype_emb, intent_id in self.intent_prototypes:
            score = np.dot(query_embedding, prototype_emb)
            if score > highest_score:
                highest_score = score
                best_intent = intent_id
        
        # Entity Extraction (spaCy) is still valuable for Generic Intents
        # or if we need to refine a specific intent (e.g. "open music" -> entity="music")
        entity = self.extract_entity(user_query)
        
        # Fallback Entity Logic
        if not entity:
             words = user_query.split()
             entity = " ".join(words[1:]) if len(words) > 1 else ""

        return best_intent, float(highest_score), entity

    def extract_entity(self, query):
        doc = self.nlp_spacy(query)
        target_entity = ""
        
        for token in doc:
            if token.dep_ == "dobj":
                # Get subtree, remove articles
                target_entity = " ".join([t.text for t in token.subtree])
                target_entity = target_entity.replace("the ", "").replace("a ", "").replace("an ", "")
                return target_entity.strip()
        
        for token in doc:
            if token.dep_ == "pobj":
                target_entity = " ".join([t.text for t in token.subtree])
                return target_entity.strip()

        return ""
