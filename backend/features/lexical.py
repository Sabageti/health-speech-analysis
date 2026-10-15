import spacy

class LexicalFeatures:
    """
    Stage 2: Lexical and grammatical features based on NLP.
    e.g., Lexical Diversity (TTR), Noun/Verb Ratio, Filler Rate.
    """
    def __init__(self):
        self.nlp = None

    def _load_model(self):
        if self.nlp is None:
            print("Loading spaCy NLP model ('en_core_web_sm')...")
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("Model 'en_core_web_sm' not found. Please run: python -m spacy download en_core_web_sm")
                raise

    def extract_features(self, text: str):
        if not text or not text.strip():
            return {
                "Lexical_Diversity (TTR)": 0.0,
                "Noun_Verb_Ratio": 0.0,
                "Filler_Rate": "0.0%",
                "Filler_Count": 0,
                "Total_Nouns": 0,
                "Total_Verbs": 0
            }

        self._load_model()
        doc = self.nlp(text)

        nouns = 0
        verbs = 0
        fillers = 0
        valid_words = 0

        # Commonly used fillers/hesitations
        filler_words_lower = {"um", "uh", "ah", "er", "hmm", "mhm"}

        lemmas = []
        for token in doc:
            if not token.is_punct and not token.is_space:
                valid_words += 1

                if token.lower_ in filler_words_lower or token.pos_ == "INTJ":
                    fillers += 1

                if token.pos_ in ("NOUN", "PROPN"):
                    nouns += 1
                elif token.pos_ == "VERB":
                    verbs += 1

                lemmas.append(token.lemma_.lower())

        noun_verb_ratio = (nouns / verbs) if verbs > 0 else (nouns if nouns > 0 else 0)
        filler_rate = (fillers / valid_words) if valid_words > 0 else 0

        # TTR calculation
        ttr_score = (len(set(lemmas)) / len(lemmas)) if len(lemmas) > 0 else 0.0

        return {
            "Lexical_Diversity (TTR)": round(ttr_score, 2),
            "Noun_Verb_Ratio": round(noun_verb_ratio, 2),
            "Total_Nouns": nouns,
            "Total_Verbs": verbs,
            # "Filler_Rate": f"{round(filler_rate * 100, 2)}%",
            # "Filler_Count": fillers,

        }
