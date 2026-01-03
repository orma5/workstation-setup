from pathlib import Path
from utils import log, success, warn, load_folders_config, PROJECT_ROOT

def ensure_folders() -> None:
    """
    Ensure all folders from folders.yaml are created.
    This function is declarative and idempotent - it checks if each folder exists
    before attempting creation.
    """
    log("Ensuring folders are created...")

    config_path = PROJECT_ROOT / "config" / "folders.yaml"

    # Load configuration
    folders = load_folders_config(config_path)

    if not folders:
        warn("No folders specified in configuration.")
        return

    log(f"Checking {len(folders)} folders...")
    for folder_path_str in folders:
        # Expand ~ to user's home directory
        folder_path = Path(folder_path_str).expanduser()

        if folder_path.exists():
            if folder_path.is_dir():
                success(f"{folder_path} already exists.")
            else:
                warn(f"{folder_path} exists but is not a directory.")
        else:
            try:
                log(f"Creating {folder_path}...")
                folder_path.mkdir(parents=True, exist_ok=True)
                success(f"{folder_path} created.")
            except Exception as e:
                warn(f"Failed to create {folder_path}: {e}")

    success("All folders processed.")
