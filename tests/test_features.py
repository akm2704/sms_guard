"""Unit tests for task 6 feature extraction."""

from scipy.sparse import issparse

from ml.features import SmsManualFeatures, make_sms_features_pipeline
from ml.rules import detect_se_groups


def test_manual_feature_shape():
    texts = ["Hello!", "URGENT!!! Send 5000 ₸ to https://example.test"]
    X = SmsManualFeatures().transform(texts)
    assert X.shape == (2, 7)
    assert issparse(X)


def test_uppercase_and_punctuation():
    arr = SmsManualFeatures().transform(["HELLO!!!"]).toarray()[0]
    assert arr[0] == 8
    assert arr[1] == 1.0
    assert arr[2] == 3


def test_url_money_flags():
    arr = SmsManualFeatures().transform(["Pay 5000 ₸ at https://example.test"]).toarray()[0]
    assert arr[3] == 1
    assert arr[4] == 1


def test_groups_detected():
    groups = detect_se_groups("URGENT! You won a prize!")
    assert "URGENCY" in groups
    assert "PRIZE" in groups


def test_pipeline_three_branches():
    docs = ["Hello world", "Hello again", "URGENT prize free", "Free prize today"]
    pipeline = make_sms_features_pipeline()
    X = pipeline.fit_transform(docs)
    assert X.shape[0] == 4
    assert X.shape[1] > 7
    assert issparse(X)
    out = pipeline.transform(["Different new SMS"])
    assert out.shape[1] == X.shape[1]


def test_unseen_word_not_added_on_transform():
    docs = ["Hello world", "Hello again", "URGENT prize free", "Free prize today"]
    pipeline = make_sms_features_pipeline()
    pipeline.fit(docs)
    vectorizer = pipeline.named_steps["features"].named_transformers["words"].named_steps["tfidf"]
    before = len(vectorizer.vocabulary_)
    assert "unseentokenxyz" not in vectorizer.vocabulary_
    pipeline.transform(["unseentokenxyz"])
    assert len(vectorizer.vocabulary_) == before
