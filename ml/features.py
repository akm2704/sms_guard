"""Task 6: TF-IDF of words/characters + hand-crafted SMS features.

Pipeline accepts RAW SMS strings. Normalization lives inside the Pipeline,
so the identical function is used for training and inference.
"""

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import StandardScaler

from ml.preprocessing import normalize_sms
from ml.rules import detect_se_groups


class SmsTextNormalizer(BaseEstimator, TransformerMixin):
    """Convert a sequence of original SMS texts to normalized strings."""

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return [normalize_sms(x) for x in X]


class SmsManualFeatures(BaseEstimator, TransformerMixin):
    """Seven hand-made features derived from the original input text."""

    FEATURE_NAMES = (
        "raw_length",
        "uppercase_fraction",
        "exclamation_count",
        "has_url",
        "has_money",
        "has_phone",
        "se_group_count",
    )

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        rows = []
        for item in X:
            raw = item if isinstance(item, str) else ""
            clean = normalize_sms(raw)
            letters = [char for char in raw if char.isalpha()]
            upper_ratio = (
                sum(char.isupper() for char in letters) / len(letters)
                if letters else 0.0
            )
            rows.append([
                len(raw),
                upper_ratio,
                raw.count("!"),
                int("<url>" in clean),
                int("<money>" in clean),
                int("<phone>" in clean),
                len(detect_se_groups(raw)),
            ])
        return csr_matrix(np.asarray(rows, dtype=np.float64).reshape(-1, 7))

    def get_feature_names_out(self, input_features=None):
        return np.array(self.FEATURE_NAMES, dtype=object)


def make_sms_features_pipeline():
    """Return an UNFITTED Pipeline. Call fit only with training SMS texts."""
    word_pipeline = Pipeline([
        ("normalize", SmsTextNormalizer()),
        ("tfidf", TfidfVectorizer(
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
            sublinear_tf=True,
        )),
    ])
    char_pipeline = Pipeline([
        ("normalize", SmsTextNormalizer()),
        ("tfidf", TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=(3, 5),
            min_df=2,
            sublinear_tf=True,
        )),
    ])
    manual_pipeline = Pipeline([
        ("features", SmsManualFeatures()),
        ("scale", StandardScaler(with_mean=False)),
    ])
    return Pipeline([
        ("features", FeatureUnion([
            ("words", word_pipeline),
            ("chars", char_pipeline),
            ("manual", manual_pipeline),
        ])),
    ])
