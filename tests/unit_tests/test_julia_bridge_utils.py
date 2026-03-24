from judiagent.julia.bridge_types import JuliaExecutionResult
from judiagent.julia.error_formatting import (
    format_runtime_error,
    parse_error_and_trace,
    sanitize_stacktrace,
    strip_condapkg_noise,
)


def test_parse_error_and_trace_splits_stacktrace_block():
    message, trace = parse_error_and_trace(
        "MethodError: foo()\nStacktrace:\n [1] top-level scope"
    )

    assert message == "MethodError: foo()"
    assert trace == "[1] top-level scope"


def test_sanitize_stacktrace_removes_internal_frames():
    trace = "\n".join(
        [
            "[1] my_user_code() at user.jl:10",
            "[2] PythonCall.jl frame",
            "[3] pyjlmodule_seval frame",
        ]
    )

    cleaned = sanitize_stacktrace(trace)

    assert cleaned == "[1] my_user_code() at user.jl:10"


def test_strip_condapkg_noise_keeps_meaningful_lines():
    text = "\n".join(
        [
            "CondaPkg Initialising pixi.toml",
            "",
            "ERROR: MethodError: no method matching foo()",
        ]
    )

    assert strip_condapkg_noise(text) == "ERROR: MethodError: no method matching foo()"


def test_format_runtime_error_combines_message_and_trace():
    result = JuliaExecutionResult(
        has_error=True,
        error_summary="ERROR: failure",
        error_trace="[1] top-level scope",
    )

    formatted = format_runtime_error(result)

    assert "ERROR: failure" in formatted
    assert "Stacktrace:" in formatted
    assert "[1] top-level scope" in formatted


def test_format_runtime_error_includes_return_code_and_command():
    result = JuliaExecutionResult(
        has_error=True,
        error_summary="Error running Julia: [Errno 2] No such file or directory: 'julia'",
        return_code=127,
        command="/usr/bin/julia",
    )

    formatted = format_runtime_error(result)

    assert "Return code: 127" in formatted
    assert "Julia executable: /usr/bin/julia" in formatted


def test_execute_and_capture_treats_zero_exit_with_non_error_stderr_as_success(monkeypatch):
    from judiagent.julia import execution_bridge

    def fake_execute_julia_inline(*, code: str):
        return ("ok\n", "Warning: using fallback cache\n", 0, "/usr/bin/julia")

    monkeypatch.setattr(execution_bridge, "execute_julia_inline", fake_execute_julia_inline)

    result = execution_bridge.execute_and_capture("println(1)")

    assert result.has_error is False
    assert result.stdout == "ok\n"
    assert result.return_code == 0
    assert result.command == "/usr/bin/julia"


def test_determine_code_timeout_secs_uses_longer_budget_for_heavy_rtm(monkeypatch):
    from judiagent.julia import subprocess_runner

    monkeypatch.delenv("JUDIAgent_JULIA_CODE_TIMEOUT_SECS", raising=False)
    monkeypatch.delenv("JUDIAgent_JULIA_HEAVY_CODE_TIMEOUT_SECS", raising=False)

    timeout = subprocess_runner.determine_code_timeout_secs(
        "using JUDI\nJ = judiJacobian(F, q)\nrtm = adjoint(J) * d_obs\n"
    )

    assert timeout == 600


def test_determine_code_timeout_secs_keeps_shorter_budget_for_small_tasks(monkeypatch):
    from judiagent.julia import subprocess_runner

    monkeypatch.delenv("JUDIAgent_JULIA_CODE_TIMEOUT_SECS", raising=False)
    monkeypatch.delenv("JUDIAgent_JULIA_HEAVY_CODE_TIMEOUT_SECS", raising=False)

    timeout = subprocess_runner.determine_code_timeout_secs(
        "using JUDI\nwavelet = ricker_wavelet(2000f0, 4f0, 0.015f0)\n"
    )

    assert timeout == 180
