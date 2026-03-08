"""
File for defining the specifics related to the different retrievers. Gives flexibility to vary the splitting functions etc.
"""

from dataclasses import dataclass
from functools import partial
from typing import Callable, Union

from judiagent.configuration import PROJECT_ROOT
from judiagent.rag import split_docs, split_examples


@dataclass
class RetrieverSpec:
    dir_path: str
    persist_path: Callable  # Callable as we want to change where we store when we modify the embedding model in the configuration.
    cache_path: str
    collection_name: str
    filetype: Union[str, list[str]]  # Can be a single filetype or a list of filetypes.
    split_func: Callable


RETRIEVER_SPECS = {
    "judi": {
        "docs": RetrieverSpec(
            dir_path=str(PROJECT_ROOT / "rag" / "judi" / "docs" / "src"),
            persist_path=lambda retriever_dir_name: str(
                PROJECT_ROOT
                / "rag"
                / "retriever_store"
                / f"retriever_judi_docs_{retriever_dir_name}"
            ),
            cache_path=str(
                PROJECT_ROOT / "rag" / "loaded_store" / "loaded_judi_docs.pkl"
            ),
            collection_name="judi_docs",
            filetype="md",
            split_func=split_docs.split_docs,
        ),
        "examples": RetrieverSpec(
            dir_path=str(PROJECT_ROOT / "rag" / "judi" / "examples"),
            persist_path=lambda retriever_dir_name: str(
                PROJECT_ROOT
                / "rag"
                / "retriever_store"
                / f"retriever_judi_examples_{retriever_dir_name}"
            ),
            cache_path=str(
                PROJECT_ROOT / "rag" / "loaded_store" / "loaded_judi_examples.pkl"
            ),
            collection_name="judi_examples",
            filetype="jl",
            split_func=partial(
                split_examples.split_examples,
                header_to_split_on=1,  # Split on `# #`
            ),
        ),
    },
}
