from judiagent.benchmarks import get_benchmark_task, load_benchmark_tasks
from judiagent.nodes.validation_metrics import get_task_metric_plan


def test_benchmark_catalog_loads_unique_tasks():
    tasks = load_benchmark_tasks()

    assert "basic_2d_forward" in tasks
    assert len(tasks) >= 20
    assert len(tasks) == len(set(tasks))


def test_benchmark_tasks_include_evaluation_contract():
    task = get_benchmark_task("rtm_basic")

    assert task.category == "imaging"
    assert "imaging_operator" in task.required_components
    assert "image_residual_norm" in task.metric_bundle
    assert task.acceptance_criteria


def test_runtime_metric_plans_are_backed_by_catalog_tasks():
    tasks = load_benchmark_tasks()

    for task_id in ("basic_2d_forward", "rtm_basic", "fwi_basic"):
        task = tasks[task_id]
        plan = get_task_metric_plan(task_id)

        assert plan is not None
        assert {metric.name for metric in plan.metrics}.issubset(set(task.metric_bundle))
