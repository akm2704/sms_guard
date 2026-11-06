"""Lightweight predictor API checks; training is exercised by the command-line script."""
from unittest.mock import patch

import numpy as np
import pytest

from ml.baseline import predict_sms


class DummyModel:
    classes_ = np.array([0, 1])

    def predict_proba(self, x):
        assert isinstance(x, list) and len(x) == 1
        return np.array([[0.15, 0.85]])

    def predict(self, x):
        return np.array([1])


def test_predict_sms_contract():
    with patch("ml.baseline._load_model", return_value=DummyModel()):
        assert predict_sms("Test SMS") == {"label": 1, "probability": 0.85}


@pytest.mark.parametrize("value", ["", "   ", None, "x" * 1001])
def test_predict_sms_invalid_text(value):
    with pytest.raises(ValueError):
        predict_sms(value)
