import importlib.util
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_module_from_path(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_example_entrypoints_import_agents():
    agent_module = _load_module_from_path(
        "example_agent",
        PROJECT_ROOT / "examples" / "agent.py",
    )
    autonomous_module = _load_module_from_path(
        "example_autonomous_agent",
        PROJECT_ROOT / "examples" / "autonomous_agent.py",
    )

    assert hasattr(agent_module, "iterative_agent")
    assert hasattr(autonomous_module, "react_agent")


def test_langgraph_target_is_importable():
    config = json.loads((PROJECT_ROOT / "langgraph.json").read_text())
    target = config["graphs"]["judiagent"]["path"]
    file_part, attr_name = target.split(":")
    module = _load_module_from_path("langgraph_target_module", PROJECT_ROOT / file_part)

    assert hasattr(module, attr_name)
