import os
from functools import lru_cache

import numpy as np
from fastembed import TextEmbedding
from tokenizers import Tokenizer

from .settings import DATA, MODEL

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")


@lru_cache(maxsize=1)
def model():
    return TextEmbedding(MODEL, cache_dir=str(DATA / "models"), threads=4)


def tokenizer():
    # Clone: chunk counting must not truncate; inference tokenizer stays unchanged.
    tok = Tokenizer.from_str(model().model.tokenizer.to_str())
    tok.no_truncation()
    tok.no_padding()
    return tok


def embed(texts):
    vectors = np.asarray(list(model().embed(texts, batch_size=32)), dtype="float32")
    vectors /= np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-12)
    return np.ascontiguousarray(vectors)
