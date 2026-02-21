from app.services.steel_model_service import SteelModelService


def test_raw_dataset_load(synthetic_steel_dataset):
    svc = SteelModelService()
    df = svc.load_raw_dataset(str(synthetic_steel_dataset))
    assert df.shape[1] == 34


def test_raw_dataset_load_tab_delimited(synthetic_steel_dataset, tmp_path):
    svc = SteelModelService()
    tab_path = tmp_path / "Faults.NNA.tsv"
    csv_text = synthetic_steel_dataset.read_text(encoding="utf-8")
    tab_path.write_text(csv_text.replace(",", "\t"), encoding="utf-8")
    df = svc.load_raw_dataset(str(tab_path))
    assert df.shape[1] == 34


def test_label_conversion(synthetic_steel_dataset):
    svc = SteelModelService()
    df = svc.load_raw_dataset(str(synthetic_steel_dataset))
    X, y = svc.convert_multiclass_labels(df)
    assert X.shape[1] == 27
    assert len(y) == len(df)


def test_training_pipeline_outputs_artifacts(synthetic_steel_dataset):
    svc = SteelModelService()
    result = svc.train(str(synthetic_steel_dataset))
    assert result["model_path"]
    assert result["metrics_path"]
    assert "macro_f1" in result["metrics"]
