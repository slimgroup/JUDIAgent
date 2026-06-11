"""Unit tests for the ImageGather.jl RAG corpus integration.

Cover the catalog wiring, retrieval tool surface, widened codebase grep,
chunked-output shape, and agent tool binding for the ``imagegather`` source.
"""

from __future__ import annotations

import os
import re
from dataclasses import replace
from pathlib import Path

from judiagent.rag.cache import load_chunked_documents
from judiagent.rag.catalog import RAG_CATALOG, CorpusSpec
from judiagent.settings import PROJECT_ROOT
from judiagent.tools import search_imagegather_examples
from judiagent.tools.retrieve import search_codebase

IMAGEGATHER_EXAMPLE_FILES = ("layers_cig.jl", "layers_sscig.jl", "offset_map.jl")


def _spec_with_tmp_cache(spec: CorpusSpec, tmp_path: Path, filename: str) -> CorpusSpec:
    """Return a copy of ``spec`` whose pickle cache lives under ``tmp_path``."""
    return replace(spec, cache_file=str(tmp_path / filename))


# ---------------------------------------------------------------------------
# Catalog wiring
# ---------------------------------------------------------------------------

def test_imagegather_corpora_registered_in_catalog():
    assert "imagegather" in RAG_CATALOG
    assert set(RAG_CATALOG["imagegather"].keys()) == {"docs", "examples"}


def test_imagegather_corpus_specs_are_disjoint_from_judi():
    """Cache files, persist dirs, and collection names must not collide with JUDI."""
    judi = RAG_CATALOG["judi"]
    ig = RAG_CATALOG["imagegather"]

    for kind in ("docs", "examples"):
        assert ig[kind].cache_file != judi[kind].cache_file
        assert ig[kind].collection_name != judi[kind].collection_name
        # persist_dir is a callable; sample it with an arbitrary embedding family
        assert ig[kind].persist_dir("openai") != judi[kind].persist_dir("openai")
        assert "imagegather" in ig[kind].collection_name
        assert "imagegather" in ig[kind].cache_file
        assert "imagegather" in ig[kind].persist_dir("openai")


def test_imagegather_source_dirs_exist_and_contain_expected_filetypes():
    for kind in ("docs", "examples"):
        spec = RAG_CATALOG["imagegather"][kind]
        assert os.path.isdir(spec.source_dir), f"{kind}: {spec.source_dir} missing"

        matches = [
            f
            for root, _, files in os.walk(spec.source_dir)
            for f in files
            if f.endswith(tuple("." + ext for ext in spec.filetypes))
        ]
        assert matches, f"{kind}: no files matching {spec.filetypes} under {spec.source_dir}"


def test_imagegather_filetypes_match_source_kind():
    assert RAG_CATALOG["imagegather"]["docs"].filetypes == ("md",)
    assert RAG_CATALOG["imagegather"]["examples"].filetypes == ("jl",)


# ---------------------------------------------------------------------------
# Retrieval tool surface
# ---------------------------------------------------------------------------

def test_search_imagegather_examples_is_exported():
    # Imported at the top of this module via `from judiagent.tools import ...`
    assert search_imagegather_examples is not None
    assert search_imagegather_examples.name == "search_imagegather_examples"


def test_search_imagegather_examples_description_references_package():
    description = (search_imagegather_examples.description or "").lower()
    assert "imagegather" in description


# ---------------------------------------------------------------------------
# Widened codebase grep
# ---------------------------------------------------------------------------

def test_search_codebase_finds_imagegather_only_terms():
    """A query for a term that exists only in rag/imagegather should return hits
    from that tree, proving the second search root was added."""
    result = search_codebase.invoke(
        {"query": "judiExtendedJacobian", "file_pattern": None, "use_regex": False}
    )
    assert "/rag/imagegather/" in result
    assert "No matches" not in result


def test_search_codebase_still_finds_judi_only_terms():
    """Regression guard: widening the grep must not break JUDI-side hits."""
    result = search_codebase.invoke(
        {"query": "judiModeling", "file_pattern": None, "use_regex": False}
    )
    assert "/rag/judi/" in result
    assert "No matches" not in result


# ---------------------------------------------------------------------------
# Chunking with JUDI-style headings
# ---------------------------------------------------------------------------

def test_imagegather_example_files_carry_judi_style_headings():
    """Every example file must contain at least one ``# # Heading`` marker so the
    Julia example chunker can split it into named sections."""
    examples_dir = Path(RAG_CATALOG["imagegather"]["examples"].source_dir)
    heading_re = re.compile(r"^#\s+#\s+\S", re.MULTILINE)

    for name in IMAGEGATHER_EXAMPLE_FILES:
        path = examples_dir / name
        assert path.exists(), f"{path} missing"
        headings = heading_re.findall(path.read_text())
        assert len(headings) >= 3, f"{name}: only {len(headings)} headings (want >= 3)"


def test_imagegather_examples_chunk_into_named_sections(tmp_path):
    spec = _spec_with_tmp_cache(
        RAG_CATALOG["imagegather"]["examples"],
        tmp_path,
        "loaded_imagegather_examples.pkl",
    )
    chunks = load_chunked_documents(spec)

    # 3 example files, each annotated with multiple `# #` sections.
    assert len(chunks) >= len(IMAGEGATHER_EXAMPLE_FILES) * 3

    # Every chunk has a non-empty heading and a source path under rag/imagegather/.
    for chunk in chunks:
        assert chunk.metadata.get("heading"), "chunk has no heading"
        assert "rag/imagegather/" in chunk.metadata.get("source", "")

    # Each example file contributed at least one chunk.
    chunked_sources = {Path(c.metadata["source"]).name for c in chunks}
    for name in IMAGEGATHER_EXAMPLE_FILES:
        assert name in chunked_sources, f"{name} contributed no chunks"


def test_imagegather_docs_chunk_non_empty(tmp_path):
    spec = _spec_with_tmp_cache(
        RAG_CATALOG["imagegather"]["docs"],
        tmp_path,
        "loaded_imagegather_docs.pkl",
    )
    chunks = load_chunked_documents(spec)

    assert chunks, "imagegather docs produced zero chunks"
    for chunk in chunks:
        assert "rag/imagegather/docs/" in chunk.metadata.get("source", "")


# ---------------------------------------------------------------------------
# Agent tool binding
# ---------------------------------------------------------------------------

def test_iterative_agent_binds_imagegather_tool():
    from judiagent.agents.agent import iterative_agent

    tool_names = {t.name for t in iterative_agent.registered_tools}
    assert "search_imagegather_examples" in tool_names
    assert "search_judi_examples" in tool_names  # regression guard


def test_react_agent_binds_imagegather_tool():
    from judiagent.agents.autonomous_agent import react_agent

    tool_names = {t.name for t in react_agent.registered_tools}
    assert "search_imagegather_examples" in tool_names
    assert "search_judi_examples" in tool_names


def test_gather_intelligence_prompt_mentions_imagegather_tool():
    from judiagent.prompting.shared import GATHER_INTELLIGENCE

    assert "search_imagegather_examples" in GATHER_INTELLIGENCE
    assert "search_judi_examples" in GATHER_INTELLIGENCE


# ---------------------------------------------------------------------------
# Provenance and licensing
# ---------------------------------------------------------------------------

def test_imagegather_license_file_present():
    license_path = PROJECT_ROOT / "rag" / "imagegather" / "LICENSE"
    assert license_path.is_file(), "imagegather LICENSE missing"
    assert "MIT" in license_path.read_text()


def test_third_party_doc_lists_imagegather():
    doc = (PROJECT_ROOT / "rag" / "THIRD_PARTY.md").read_text()
    assert "ImageGather.jl" in doc
    assert "ext_PhyParams" in doc
