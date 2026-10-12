from pathlib import Path


def discover_existing_model_dirs(
    data_home: Path, official_home: Path | None = None
) -> tuple[Path, ...]:
    """Reuse an existing official EXO model cache without granting write access."""
    official_models = (official_home or Path.home() / ".exo") / "models"
    if not official_models.is_dir():
        return ()
    if official_models.resolve() == (data_home / "models").resolve():
        return ()
    return (official_models.resolve(),)
