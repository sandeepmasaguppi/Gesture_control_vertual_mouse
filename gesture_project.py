"""Download, set up, and launch the Gesture Controller project on Windows Just run the gesture_project.py file."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath


REPOSITORY = "sandeepmasaguppi/Gesture_control_vertual_mouse"
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR / "Gesture_control_vertual_mouse"
REQUIRED_FILES = (
    Path("requirements.txt"),
    Path("src") / "Gesture_Controller.py",
)


def is_project(path):
    return all((path / required_file).is_file() for required_file in REQUIRED_FILES)


def download_project():
    if PROJECT_DIR.exists():
        if is_project(PROJECT_DIR):
            return
        if any(PROJECT_DIR.iterdir()):
            raise RuntimeError(
                f"{PROJECT_DIR} exists but does not contain the expected project files. "
                "Move or rename that folder, then run this script again."
            )

    SCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    git_executable = shutil.which("git")
    if git_executable:
        with tempfile.TemporaryDirectory(dir=SCRIPT_DIR) as temporary_directory:
            clone_path = Path(temporary_directory) / "repository"
            subprocess.run(
                [
                    git_executable,
                    "clone",
                    "--depth",
                    "1",
                    f"https://github.com/{REPOSITORY}.git",
                    str(clone_path),
                ],
                check=True,
            )
            if not is_project(clone_path):
                raise RuntimeError(
                    "The GitHub repository does not contain the expected project files."
                )
            if PROJECT_DIR.exists():
                PROJECT_DIR.rmdir()
            shutil.move(str(clone_path), str(PROJECT_DIR))
        return

    api_url = f"https://api.github.com/repos/{REPOSITORY}"
    request = urllib.request.Request(
        api_url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": "gesture-project-setup"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        repository_info = json.load(response)

    branch = urllib.parse.quote(repository_info["default_branch"], safe="")
    archive_url = f"https://codeload.github.com/{REPOSITORY}/zip/refs/heads/{branch}"

    with tempfile.TemporaryDirectory(dir=PROJECT_DIR.parent) as temporary_directory:
        temporary_path = Path(temporary_directory)
        archive_path = temporary_path / "project.zip"
        request = urllib.request.Request(
            archive_url,
            headers={"User-Agent": "gesture-project-setup"},
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            archive_path.write_bytes(response.read())

        extracted_path = temporary_path / "extracted"
        extracted_path.mkdir()
        with zipfile.ZipFile(archive_path) as archive:
            for member in archive.infolist():
                member_path = PurePosixPath(member.filename)
                windows_member_path = PureWindowsPath(member.filename)
                if (
                    member_path.is_absolute()
                    or ".." in member_path.parts
                    or windows_member_path.is_absolute()
                    or windows_member_path.drive
                    or ".." in windows_member_path.parts
                ):
                    raise RuntimeError("The downloaded project archive contains an unsafe path.")
            archive.extractall(extracted_path)

        project_roots = list(extracted_path.iterdir())
        if len(project_roots) != 1 or not is_project(project_roots[0]):
            raise RuntimeError(
                "The GitHub repository does not contain the expected project files."
            )

        if PROJECT_DIR.exists():
            PROJECT_DIR.rmdir()
        shutil.move(str(project_roots[0]), str(PROJECT_DIR))


def setup_environment():
    environment_dir = PROJECT_DIR / ".venv"
    python_path = environment_dir / "Scripts" / "python.exe"

    if not python_path.is_file():
        subprocess.run(
            [sys.executable, "-m", "venv", str(environment_dir)],
            cwd=PROJECT_DIR,
            check=True,
        )

    subprocess.run(
        [str(python_path), "-m", "pip", "install", "--upgrade", "pip"],
        cwd=PROJECT_DIR,
        check=True,
    )
    subprocess.run(
        [str(python_path), "-m", "pip", "install", "-r", str(PROJECT_DIR / "requirements.txt")],
        cwd=PROJECT_DIR,
        check=True,
    )
    return python_path


def main():
    if os.name != "nt":
        raise RuntimeError("This setup script is intended to run on Windows.")

    print(f"Launcher: {Path(__file__).resolve()}")
    print(f"Preparing project in {PROJECT_DIR} ...")
    download_project()
    python_path = setup_environment()

    print("Starting gesture recognition. Close its camera window or press Enter to stop.")
    print("Project output and setup files will be under the project folder above.")
    subprocess.run(
        [str(python_path), str(PROJECT_DIR / "src" / "Gesture_Controller.py")],
        cwd=PROJECT_DIR,
        check=True,
    )


if __name__ == "__main__":
    main()
