#!/usr/bin/env python3
"""
Synthetic Exchange-Rate (FX) Forecast Image Generator
----------------------------------------------------
This script creates line-chart images that resemble FX rate forecasts.  Each
image contains two time-series:
  • "actual"  – the true (simulated) exchange-rate path, generated via a
    geometric Brownian motion-style random walk.
  • "predicted" – a noisy forecast of the actual path.

The resulting PNG files can be used as CNN inputs to benchmark model
performance without revealing any proprietary data.

Usage (from project root):
    python generate_fx_images.py --num 100 --length 120 --out_dir data/fx_imgs

Parameters
----------
--num        Number of images to create (default 50)
--length     Time-series length in points (default 100)
--out_dir    Directory to write PNGs (will be created if absent)
--seed       RNG seed for reproducibility (optional)
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def generate_random_walk(n: int, start: float = 1.0, mu: float = 0.0, sigma: float = 0.01) -> np.ndarray:
    """Return a geometric Brownian-motion-style random walk of length *n*."""
    # Percentage returns
    returns = np.random.normal(mu, sigma, size=n)
    # Log-returns cumulative sum
    log_price = np.cumsum(returns)
    price = start * np.exp(log_price)
    return price


def create_fx_image(length: int, out_path: Path) -> None:
    """Generate a single FX chart image and write it to *out_path*."""
    actual = generate_random_walk(length)
    # Predicted series: actual plus Gaussian noise proportional to price level
    noise = np.random.normal(0.0, 0.005, size=length)
    predicted = actual * (1.0 + noise)

    plt.figure(figsize=(6, 4))
    x = np.arange(length)
    plt.plot(x, actual, label="Actual", linewidth=2)
    plt.plot(x, predicted, label="Predicted", linestyle="--", linewidth=1.5)
    plt.title("Synthetic FX Rate Forecast")
    plt.xlabel("Time step")
    plt.ylabel("Exchange rate")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic FX forecast images for CNN evaluation.")
    parser.add_argument("--num", type=int, default=50, help="Number of images to generate (default: 50)")
    parser.add_argument("--length", type=int, default=100, help="Length of each time series (default: 100)")
    parser.add_argument("--out_dir", type=str, default="fx_images", help="Output directory for images")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    args = parser.parse_args()

    if args.seed is not None:
        np.random.seed(args.seed)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for i in range(args.num):
        filename = out_dir / f"fx_{i:05d}.png"
        create_fx_image(args.length, filename)
        if (i + 1) % 10 == 0 or i == args.num - 1:
            print(f"[+] Generated {i + 1}/{args.num} images", end="\r", flush=True)
    print(f"\nDone. Images saved to {out_dir.resolve()}")


if __name__ == "__main__":
    main()