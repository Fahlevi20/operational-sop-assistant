from sop_assistant.download import download_model


def test_download_uses_local_target_without_exposing_token(tmp_path):
    calls = []

    def snapshot(**kwargs):
        calls.append(kwargs)
        return str(tmp_path / "model")

    result = download_model(tmp_path / "model", downloader=snapshot)
    assert result == str(tmp_path / "model")
    assert calls[0]["repo_id"] == "google/embeddinggemma-300m"
    assert calls[0]["local_dir"] == str(tmp_path / "model")
    assert "*.safetensors" in calls[0]["allow_patterns"]
    assert "*.gguf" not in calls[0]["allow_patterns"]
