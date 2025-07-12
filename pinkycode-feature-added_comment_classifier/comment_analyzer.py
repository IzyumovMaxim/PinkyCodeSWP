import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from pathlib import Path
from typing import List, Dict, Tuple, Optional

class PinkyCodeClassifier:
    def __init__(self, model_name="Maximus2005/PinkyCode"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        self.labels = {0: "meaningless", 1: "meaningful"}
    
    def predict(self, comment, code_snippet, max_length=512):
        input_text = f"{comment} {self.tokenizer.sep_token} {code_snippet}"
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            max_length=max_length,
            truncation=True,
            padding=True
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.softmax(logits, dim=-1)
            predicted_class = torch.argmax(logits, dim=-1).item()
        
        return self.labels[predicted_class]

class CodeCommentExtractor:
    def __init__(self):
        self.comment_patterns = {
            'java': {'single_line': r'//.*', 'multi_line': r'/\*.*?\*/'},
            'cpp': {'single_line': r'//.*', 'multi_line': r'/\*.*?\*/'},
            'c': {'single_line': r'//.*', 'multi_line': r'/\*.*?\*/'},
            'cs': {'single_line': r'//.*', 'multi_line': r'/\*.*?\*/'}
        }
        self.extension_mapping = {
            '.java': 'java', '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp', 
            '.c': 'c', '.cs': 'cs'
        }
    
    def extract_comments(self, file_path: str) -> List[Dict]:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return []
        
        file_ext = Path(file_path).suffix.lower()
        if file_ext not in self.extension_mapping:
            return []
        
        lang = self.extension_mapping[file_ext]
        comments = []
        
        # Single-line comments
        for match in re.finditer(self.comment_patterns[lang]['single_line'], content):
            comment = match.group().strip()
            if not self._is_trivial(comment):
                comments.append({
                    'text': re.sub(r'^//\s*', '', comment),
                    'line': content[:match.start()].count('\n') + 1
                })
        
        # Multi-line comments
        for match in re.finditer(
            self.comment_patterns[lang]['multi_line'], content, re.DOTALL
        ):
            comment = match.group()
            clean_comment = re.sub(r'/\*\*?|\*/', '', comment)
            clean_comment = re.sub(r'^\s*\*\s?', '', clean_comment, flags=re.MULTILINE).strip()
            if clean_comment and not self._is_trivial(clean_comment):
                comments.append({
                    'text': clean_comment,
                    'line': content[:match.start()].count('\n') + 1
                })
        
        return comments

    def _is_trivial(self, comment: str) -> bool:
        trivial_patterns = [
            r'^\s*$', r'^\s*-+\s*$', r'^\s*=+\s*$', r'^\s*\*+\s*$', r'^\s*#+\s*$',
            r'^\s*TODO\s*$', r'^\s*FIXME\s*$', r'^\s*XXX\s*$'
        ]
        return any(re.match(p, comment, re.IGNORECASE) for p in trivial_patterns) or len(comment.strip()) < 5

class CommentAnalyzer:
    def __init__(self):
        self.classifier = PinkyCodeClassifier()
        self.extractor = CodeCommentExtractor()
    
    def analyze_file(self, file_path: str) -> float:
        comments = self.extractor.extract_comments(file_path)
        if not comments:
            return 0.0
        
        meaningless_count = 0
        for comment in comments:
            try:
                prediction = self.classifier.predict(comment['text'], "")
                if prediction == "meaningless":
                    meaningless_count += 1
            except Exception:
                continue
        
        return (meaningless_count / len(comments)) * 100