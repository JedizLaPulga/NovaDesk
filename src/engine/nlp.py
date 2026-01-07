import os
import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer
import spacy

class IntentClassifier:
    def __init__(self):
        """
        Initialize the NLP engine using ONNX Runtime (Intent) + spaCy (Entity).
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
            embeddings = [self.encode(p) for p in phrases]
            self.intent_embeddings[intent] = np.mean(embeddings, axis=0)

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
        query_embedding = self.encode(user_query)
        
        best_intent = None
        highest_score = -1.0
        
        for intent, prototype_emb in self.intent_embeddings.items():
            score = np.dot(query_embedding, prototype_emb)
            if score > highest_score:
                highest_score = score
                best_intent = intent
        
        # Smart Entity Extraction using spaCy
        entity = self.extract_entity(user_query)
        
        # Fallback: If spaCy fails to find a distinct object, usage brute force
        if not entity:
             words = user_query.split()
             entity = " ".join(words[1:]) if len(words) > 1 else ""

        return best_intent, float(highest_score), entity

    def extract_entity(self, query):
        """
        Uses spaCy dependency parsing to find the Direct Object (dobj) of the command.
        """
        doc = self.nlp_spacy(query)
        target_entity = ""
        
        # 1. Look for the main verb (ROOT)
        # typical structure: "Open (ROOT) the browser (dobj)"
        for token in doc:
            if token.dep_ == "dobj":
                # We found the object! Get its subtree (e.g. "the nice browser")
                target_entity = " ".join([t.text for t in token.subtree])
                # Remove articles from the result
                target_entity = target_entity.replace("the ", "").replace("a ", "").replace("an ", "")
                return target_entity.strip()
        
        # 2. If no dobj, look for pobj (object of preposition)
        # e.g. "Search for (prep) cats (pobj)"
        for token in doc:
            if token.dep_ == "pobj":
                # Ensure it's related to the root verb
                target_entity = " ".join([t.text for t in token.subtree])
                return target_entity.strip()

        return ""
