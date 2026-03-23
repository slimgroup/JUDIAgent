#!/usr/bin/env python3
"""Sync publication-facing workflow SVGs from media/ into code_summary/figures/."""

from __future__ import annotations

from pathlib import Path
import shutil

REPO_ROOT = Path(__file__).resolve().parents[2]
MEDIA_DIR = REPO_ROOT / 'media'
OUT_DIR = REPO_ROOT / 'code_summary' / 'figures'

FIGURES = {
    'iterative_workflow.svg': 'paper_iterative_workflow.svg',
    'react_workflow.svg': 'paper_react_workflow.svg',
    'judiagent_cli.svg': 'paper_cli_view.svg',
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for source_name, output_name in FIGURES.items():
        shutil.copy2(MEDIA_DIR / source_name, OUT_DIR / output_name)
        print(f'copied {source_name} -> {output_name}')


if __name__ == '__main__':
    main()
