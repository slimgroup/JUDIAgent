from judiagent.core.julia_code import extract_fenced_julia, parse_julia_code_block


def test_extract_fenced_julia_prefers_last_non_empty_block():
    response = """
Before the final answer:
```julia
using JUDI
println("debug")
```

Final answer:
```julia
using JUDI
wavelet = ricker_wavelet(2000f0, 4f0, 0.015f0)
```
"""

    extracted = extract_fenced_julia(response)

    assert 'println("debug")' not in extracted
    assert extracted.strip().endswith('wavelet = ricker_wavelet(2000f0, 4f0, 0.015f0)')


def test_parse_julia_code_block_uses_last_fenced_solution():
    response = """
Option A:
```julia
using JUDI
println("debug")
```

Option B:
```julia
using JUDI
recording_time = 2000f0
dt = 4f0
f0 = 0.015f0
wavelet = ricker_wavelet(recording_time, dt, f0)
```
"""

    code_block = parse_julia_code_block(response)

    assert code_block.imports == 'using JUDI'
    assert 'println("debug")' not in code_block.body
    assert 'wavelet = ricker_wavelet(recording_time, dt, f0)' in code_block.body
