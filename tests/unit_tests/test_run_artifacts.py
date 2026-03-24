from pathlib import Path

from langchain_core.messages import AIMessage, HumanMessage

from judiagent.core.run_artifacts import (
    build_task_slug,
    extract_output_paths,
    infer_primary_user_prompt,
    persist_validated_run,
)


def test_extract_output_paths_finds_figures_and_data():
    code = '''
    savefig("outputs/figures/basic_2d_forward_shot.png")
    jldsave("outputs/data/basic_2d_forward_dobs.jld2"; dobs=dobs)
    '''

    paths = extract_output_paths(code)

    assert "outputs/data/basic_2d_forward_dobs.jld2" in paths
    assert "outputs/figures/basic_2d_forward_shot.png" in paths


def test_infer_primary_user_prompt_prefers_longest_non_feedback_human_message():
    messages = [
        HumanMessage(content="basic follow-up"),
        HumanMessage(content="# Validation issues – please fix the code:\n..."),
        HumanMessage(content="Create a minimal 2D acoustic forward modeling example in JUDI.jl."),
        AIMessage(content="ok"),
    ]

    prompt = infer_primary_user_prompt(messages)

    assert prompt == "Create a minimal 2D acoustic forward modeling example in JUDI.jl."


def test_build_task_slug_prefers_output_stem():
    slug = build_task_slug(
        "Create a minimal 2D acoustic forward modeling example.",
        'savefig("outputs/figures/basic_2d_forward_shot.png")',
    )

    assert slug == "basic_2d_forward"


def test_persist_validated_run_writes_script_and_metadata(tmp_path: Path):
    messages = [HumanMessage(content="How do I create a Ricker wavelet in JUDI.jl?")]
    code = "using JUDI\nwavelet = ricker_wavelet(2000f0, 4f0, 0.015f0)"

    script_path, metadata_path = persist_validated_run(
        base_directory=tmp_path,
        messages=messages,
        code=code,
        agent_mode="iterative",
        model_name="deepseek:deepseek-chat",
    )

    assert script_path.exists()
    assert metadata_path.exists()
    assert script_path.parent == tmp_path / "scripts"
    assert metadata_path.parent == tmp_path / "outputs" / "data"
    assert "ricker_wavelet" in script_path.stem
    assert "How do I create a Ricker wavelet" in metadata_path.read_text(encoding="utf-8")



def test_build_task_slug_prefers_figure_output_over_data_output():
    code = """
using JUDI
savefig("outputs/figures/basic_2d_forward_shot.png")
@save "outputs/data/basic_2d_forward_data.jld2" dobs
"""

    assert build_task_slug("basic 2d forward", code) == "basic_2d_forward"
