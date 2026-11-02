"""Performance benchmark test for SC-001.

Validates that a directed graph containing 10,000 edges loads and displays in under 1.0 second.
"""

import subprocess
import sys
import time
from pathlib import Path


def test_performance_10k_edges(tmp_path: Path) -> None:
    """Generate a synthetic 10,000-edge CSV and assert CLI completes in <1.0 second."""
    csv_file = tmp_path / "perf_10k.csv"

    # Generate 10,000 unique edges across 1,000 vertices
    # u -> v where u != v
    lines = ["source,target"]
    edge_count = 0
    target_edges = 10_000

    u = 0
    while edge_count < target_edges:
        for offset in range(1, 15):
            v = (u + offset) % 1000
            lines.append(f"node_{u},node_{v}")
            edge_count += 1
            if edge_count >= target_edges:
                break
        u += 1

    csv_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    start_time = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-m", "src.cli", str(csv_file)],
        capture_output=True,
        text=True,
        check=False,
    )
    elapsed_time = time.perf_counter() - start_time

    assert proc.returncode == 0
    assert "Edges (10000):" in proc.stdout
    assert elapsed_time < 1.0, f"Loading and display took {elapsed_time:.3f}s (must be <1.0s)"
