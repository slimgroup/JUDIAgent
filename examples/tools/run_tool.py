"""
Example: invoke a tool directly for testing.

Available tools:
  execute_shell_command, execute_julia_snippet, lint_julia_code,
  fetch_working_directory, list_files_in_directory, read_from_file,
  write_to_file, search_codebase, lookup_function_docs,
  search_judi_examples

We use search_codebase as a demo here.
"""

from judiagent.tools import search_codebase

if __name__ == "__main__":
    out = search_codebase.invoke({"query": "MPI"})
