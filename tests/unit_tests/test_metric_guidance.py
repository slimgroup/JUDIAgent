from judiagent.nodes.validation_metrics import (
    get_task_metric_plan,
    infer_workflow_family,
    recommend_metrics,
)


def test_infer_workflow_family_for_imaging_prompt():
    assert infer_workflow_family("Write an RTM imaging example with illumination compensation") == "imaging"



def test_recommend_metrics_for_fwi_prompt():
    metrics = recommend_metrics("Run 10 iterations of FWI with gradient descent")
    names = {metric.name for metric in metrics}
    assert "objective_decrease" in names
    assert "gradient_update_norm" in names



def test_task_metric_plan_for_basic_forward_is_available():
    plan = get_task_metric_plan("basic_2d_forward")
    assert plan is not None
    assert plan.workflow == "forward_modeling"
    assert any(metric.name == "trace_energy_consistency" for metric in plan.metrics)



def test_task_id_overrides_text_in_metric_recommendation():
    metrics = recommend_metrics("Just write code", task_id="rtm_basic")
    names = {metric.name for metric in metrics}
    assert "image_residual_norm" in names
    assert "illumination_balance" in names
