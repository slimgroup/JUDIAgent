from judiagent.configuration import DomainValidation
from judiagent.nodes.validation_quality import (
    run_domain_validation,
    should_run_domain_validation,
)


def test_domain_validation_skips_non_imaging_code_in_auto_mode():
    settings = DomainValidation(mode="auto", minimum_score=0.6)
    code = """
    using JUDI
    println("hello")
    """

    assert should_run_domain_validation(code, settings) is False
    assert run_domain_validation(code, settings) is None



def test_domain_validation_reports_missing_scientific_elements():
    settings = DomainValidation(mode="strict", minimum_score=0.8)
    code = """
    using JUDI
    model = Model(n=(100,100), d=(10f0,10f0), o=(0f0,0f0), m=vel)
    src_geometry = Geometry(xsrc, ysrc, zsrc, t)
    image = rtm(model, q, d_obs)
    """

    finding = run_domain_validation(code, settings)

    assert finding is not None
    assert finding.stage == "domain_quality"
    assert finding.metadata["score"] < 0.8



def test_domain_validation_accepts_richer_imaging_workflow():
    settings = DomainValidation(mode="strict", minimum_score=0.6)
    code = """
    using JUDI, LinearAlgebra
    model = Model(n=(100,100), d=(10f0,10f0), o=(0f0,0f0), m=vel)
    src_geometry = Geometry(xsrc, ysrc, zsrc, t)
    rec_geometry = Geometry(xrec, yrec, zrec, t)
    F = judiModeling(model, src_geometry, rec_geometry)
    image = rtm(model, q, d_obs)
    residual = norm(image)
    savefig("outputs/figures/rtm.png")
    """

    assert run_domain_validation(code, settings) is None
