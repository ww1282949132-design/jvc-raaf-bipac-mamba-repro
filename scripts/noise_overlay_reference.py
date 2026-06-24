#!/usr/bin/env python3
"""Reference formula for SNR-based equipment-noise overlays.

The full raw equipment-noise recordings are restricted and are not included in
this public package. This script documents the scaling rule used to construct
SNR-controlled overlays.
"""

from __future__ import annotations

import math
from typing import Iterable


def demean(values: Iterable[float]) -> list[float]:
    values = list(values)
    if not values:
        return []
    mean = sum(values) / len(values)
    return [value - mean for value in values]


def rms(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return math.sqrt(sum(value * value for value in values) / len(values))


def scale_noise_to_snr(clean: Iterable[float], noise: Iterable[float], snr_db: float) -> list[float]:
    """Scale noise so that RMS(clean) / RMS(noise_scaled) matches snr_db."""

    clean_centered = demean(clean)
    noise_centered = demean(noise)
    clean_rms = rms(clean_centered)
    noise_rms = rms(noise_centered)
    if noise_rms == 0:
        raise ValueError("Noise RMS is zero; cannot scale noise.")
    target_noise_rms = clean_rms / (10 ** (snr_db / 20.0))
    scale = target_noise_rms / noise_rms
    return [value * scale for value in noise_centered]


def overlay(clean: Iterable[float], noise: Iterable[float], snr_db: float) -> list[float]:
    clean_values = list(clean)
    scaled_noise = scale_noise_to_snr(clean_values, noise, snr_db)
    if len(clean_values) != len(scaled_noise):
        raise ValueError("Clean and noise sequences must have the same length.")
    return [signal + noise_value for signal, noise_value in zip(clean_values, scaled_noise)]


if __name__ == "__main__":
    clean_demo = [0.2, 0.4, -0.1, -0.3]
    noise_demo = [0.1, -0.2, 0.3, -0.1]
    print(overlay(clean_demo, noise_demo, snr_db=-3))

