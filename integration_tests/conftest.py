import pytest
import nltk

@pytest.fixture(scope="session", autouse=True)
def ensure_nltk_data():
    nltk.download("punkt", quiet=True)
    nltk.download("averaged_perceptron_tagger", quiet=True)

from metrics import get_density, get_comments, get_readability
@pytest.fixture(scope="module")
def metrics_funcs():
    return {
        "density": get_density,
        "comments": get_comments,
        "readability": get_readability,
    }
