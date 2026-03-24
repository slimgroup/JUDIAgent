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
