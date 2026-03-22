from judiagent.nodes.validation_metrics import infer_workflow_family, recommend_metrics


def test_infer_workflow_family_for_imaging_prompt():
    assert infer_workflow_family("Write an RTM imaging example with illumination compensation") == "imaging"


def test_recommend_metrics_for_fwi_prompt():
    metrics = recommend_metrics("Run 10 iterations of FWI with gradient descent")
    names = {metric.name for metric in metrics}
    assert "objective_decrease" in names
    assert "gradient_update_norm" in names
