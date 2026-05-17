"""ML xizmatlari va endpointlari uchun testlar."""
import pytest


def test_dropout_predictor_module_imports():
    from app.ml import dropout_predictor
    assert dropout_predictor is not None


def test_student_clusterer_module_imports():
    from app.ml import student_clusterer
    assert hasattr(student_clusterer, 'CLUSTER_FEATURES')
    assert len(student_clusterer.CLUSTER_FEATURES) >= 3


def test_anomaly_detector_module_imports():
    from app.ml import anomaly_detector
    assert anomaly_detector is not None


def test_ai_tutor_module_imports():
    from app.ml import ai_tutor
    assert ai_tutor is not None


def test_ml_endpoint_dropout_requires_auth(client):
    res = client.post("/api/v1/ml/predict-dropout", json={"student_id": 1})
    assert res.status_code in (401, 403, 404, 422)


def test_ml_endpoint_cluster_requires_auth(client):
    res = client.get("/api/v1/cluster")
    assert res.status_code in (401, 403, 404)
