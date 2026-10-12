"""Run with EXO_HOME=services/exo-runtime services/exo/.venv/bin/python this-file."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import urlopen

from exo.download.download_utils import (
    build_model_path,
    is_read_only_model_dir,
    resolve_existing_model,
)
from exo.shared.constants import EXO_DATA_HOME, EXO_MODELS_READ_ONLY_DIRS
from exo.shared.types.common import ModelId
from exo.utils.existing_model_dirs import discover_existing_model_dirs


def verify() -> None:
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        official = root / "official"
        isolated = root / "isolated"
        assert discover_existing_model_dirs(isolated, official) == ()
        (official / "models").mkdir(parents=True)
        assert discover_existing_model_dirs(isolated, official) == (
            (official / "models").resolve(),
        )
        assert discover_existing_model_dirs(official, official) == ()
    print("PASS: discovery handles absent, existing, and same-home caches")

    official_models = (Path.home() / ".exo/models").resolve()
    assert official_models in EXO_MODELS_READ_ONLY_DIRS
    assert EXO_DATA_HOME.resolve() != official_models.parent
    with urlopen("http://127.0.0.1:52416/state", timeout=10) as response:
        state = json.load(response)
    assert state["nodeBackends"], "No inference backend registered"
    completed = {}
    for downloads in state["downloads"].values():
        for download in downloads:
            if "DownloadCompleted" in download:
                entry = download["DownloadCompleted"]
                shard = next(iter(entry["shardMetadata"].values()))
                completed[shard["modelCard"]["modelId"]] = entry

    for name in (
        "mlx-community/Llama-3.2-3B-Instruct-4bit",
        "mlx-community/Qwen3-0.6B-8bit",
        "mlx-community/Qwen3.6-35B-A3B-8bit",
    ):
        model_id = ModelId(name)
        path = resolve_existing_model(model_id)
        expected = official_models / name.replace("/", "--")
        assert path == expected, (name, path)
        assert is_read_only_model_dir(path)
        assert build_model_path(model_id) == expected
        assert Path(completed[name]["modelDirectory"]) == expected
        assert not (EXO_DATA_HOME / "models" / expected.name).exists()
        print(f"PASS: resolver, loader, live scan, no duplicate: {name} -> {path}")

    assert not list((EXO_DATA_HOME / "models").rglob("*.safetensors"))
    print("PASS: isolated cache contains no duplicated safetensors weights")
    assert state["runners"], "No loaded runner"
    print("PASS: live inference runner registered")


if __name__ == "__main__":
    verify()
