"""Shared test fixtures for GestureCam tests."""

import numpy as np
import pytest


@pytest.fixture
def sample_frame():
    """Generate a blank test frame (720p BGR)."""
    return np.zeros((720, 1280, 3), dtype=np.uint8)


@pytest.fixture
def sample_face_frame(sample_frame):
    """Generate a frame with a white rectangle simulating a face."""
    frame = sample_frame.copy()
    frame[200:400, 400:700] = 255
    return frame