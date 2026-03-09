from pathlib import Path

from judiagent.tools.execution import save_julia_code, scaffold_julia_workspace


def test_scaffold_julia_workspace_uses_scripts_directory(tmp_path):
    output_path = scaffold_julia_workspace.invoke(
        {"task_name": "Forward Model", "base_directory": str(tmp_path)}
    )

    generated = Path(output_path)
    assert generated.parent == tmp_path / "scripts"
    assert generated.exists()
    assert (tmp_path / "outputs" / "figures").exists()
    assert (tmp_path / "outputs" / "data").exists()


def test_save_julia_code_creates_parent_directories(tmp_path):
    target = tmp_path / "scripts" / "nested" / "example.jl"
    result = save_julia_code.invoke(
        {"code": "using JUDI\nprintln(\"ok\")", "file_path": str(target)}
    )

    assert target.exists()
    assert "Successfully" in result
