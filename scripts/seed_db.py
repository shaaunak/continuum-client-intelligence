#!/usr/bin/env python3
"""Seed CONTINUUM PostgreSQL database with deterministic synthetic data."""

import argparse
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(ROOT_DIR))

from app.services.seed_service import seed_database


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed CONTINUUM synthetic dataset.")
    parser.add_argument("--seed", type=int, default=20270101, help="Random seed")
    parser.add_argument(
        "--scale",
        choices=["full", "compact"],
        default="full",
        help="Dataset scale: full (~12,000 clients) or compact (~2,400 clients)",
    )
    args = parser.parse_args()

    t0 = time.perf_counter()
    print(f"Generating & seeding CONTINUUM dataset (seed={args.seed}, scale={args.scale})...")
    counts = seed_database(seed=args.seed, scale=args.scale)
    elapsed = time.perf_counter() - t0
    print(f"Completed in {elapsed:.2f}s:")
    for k, v in counts.items():
        print(f"  {k}: {v:,}")


if __name__ == "__main__":
    main()
