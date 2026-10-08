#!/usr/bin/env python3
"""Install or restore Vesperwing Glass profile CSS without discovering profiles."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile


ROOT = Path(__file__).resolve().parent
DEFAULT_CSS = ROOT / "styles" / "glass.css"
DEFAULT_CONTENT_CSS = ROOT / "styles" / "content.css"
STATE_DIR_NAME = ".vesperwing-glass"
LEGACY_STATE_DIR_NAME = ".aurora-glass"
STATE_NAME = "install-state.json"
CSS_NAME = "vesperwing-glass.css"
CHROME_ENTRYPOINT = "chrome/userChrome.css"
CONTENT_ENTRYPOINT = "chrome/userContent.css"
ENTRYPOINTS = (CHROME_ENTRYPOINT, CONTENT_ENTRYPOINT)
CSS_DESTINATION = f"chrome/{CSS_NAME}"
CONTENT_CSS_NAME = "vesperwing-content.css"
CONTENT_CSS_DESTINATION = f"chrome/{CONTENT_CSS_NAME}"
LEGACY_CSS_DESTINATION = "chrome/aurora-glass.css"
LEGACY_CONTENT_CSS_DESTINATION = "chrome/aurora-content.css"
PREF_NAME = "toolkit.legacyUserProfileCustomizations.stylesheets"
PREF_MARKER = "Vesperwing Glass Thunderbird managed preference"
PREF_LINE = (
    f'user_pref("{PREF_NAME}", true); // {PREF_MARKER}\n'
)
IMPORT_TEXT = (
    "/* Managed by Vesperwing Glass Thunderbird. Original file is backed up. */\n"
    f'@import url("{CSS_NAME}");\n'
)
CONTENT_DEFAULTS_TEXT = (
    "/* Managed by Vesperwing Glass Thunderbird. Original file is backed up. */\n"
    f'@import url("{CONTENT_CSS_NAME}");\n'
)


class InstallError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_profile(profile_arg: Path) -> Path:
    try:
        profile = profile_arg.expanduser().resolve(strict=True)
    except FileNotFoundError as error:
        raise InstallError(f"profile directory does not exist: {profile_arg}") from error
    if not profile.is_dir():
        raise InstallError(f"profile path is not a directory: {profile}")
    if not (profile / "prefs.js").is_file():
        raise InstallError(
            f"{profile} does not contain prefs.js; pass the Thunderbird profile directory"
        )
    return profile


def reject_symlink(path: Path, description: str) -> None:
    if path.is_symlink():
        raise InstallError(f"refusing to use symlinked {description}: {path}")


def make_backup_dir(state_dir: Path) -> Path:
    base = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backups = state_dir / "backups"
    reject_symlink(backups, "backup directory")
    backups.mkdir(parents=True, exist_ok=True)
    candidate = backups / base
    suffix = 1
    while candidate.exists():
        candidate = backups / f"{base}-{suffix}"
        suffix += 1
    candidate.mkdir()
    return candidate


def backup_file(profile: Path, backup_dir: Path, relative: str) -> dict[str, object]:
    source = profile / relative
    reject_symlink(source, "profile file")
    if source.exists() and not source.is_file():
        raise InstallError(f"profile target is not a regular file: {source}")
    existed = source.is_file()
    record: dict[str, object] = {"existed": existed}
    if existed:
        backup_name = relative.replace("/", "__")
        backup_path = backup_dir / backup_name
        shutil.copy2(source, backup_path)
        record["backup"] = str(backup_path.relative_to(profile))
        record["sha256"] = sha256(source.read_bytes())
    return record


def atomic_write(path: Path, data: bytes, mode: int | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if mode is None:
        try:
            mode = path.stat().st_mode & 0o777
        except FileNotFoundError:
            mode = 0o644
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.vesperwing-", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
        temporary.chmod(mode)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def append_user_pref(user_js: Path) -> None:
    current = user_js.read_bytes() if user_js.exists() else b""
    if PREF_MARKER.encode("utf-8") in current:
        raise InstallError(
            "user.js already contains the Vesperwing Glass managed preference marker; "
            "restore the previous installation first"
        )
    separator = b"" if not current or current.endswith((b"\n", b"\r")) else b"\n"
    atomic_write(user_js, current + separator + PREF_LINE.encode("utf-8"))


def restore_original_file(profile: Path, state: dict[str, object], relative: str) -> None:
    files = state["files"]
    assert isinstance(files, dict)
    record = files[relative]
    assert isinstance(record, dict)
    destination = profile / relative
    reject_symlink(destination, "profile file")
    if record.get("existed"):
        backup = profile / str(record["backup"])
        if not backup.is_file():
            raise InstallError(f"backup is missing for {relative}: {backup}")
        mode = backup.stat().st_mode & 0o777
        atomic_write(destination, backup.read_bytes(), mode)
    else:
        destination.unlink(missing_ok=True)


def install(profile_arg: Path, css_arg: Path, content_css_arg: Path) -> None:
    profile = validate_profile(profile_arg)
    css_source = css_arg.expanduser().resolve()
    if not css_source.is_file():
        raise InstallError(f"glass stylesheet not found: {css_source}")
    content_css_source = content_css_arg.expanduser().resolve()
    if not content_css_source.is_file():
        raise InstallError(f"mail content stylesheet not found: {content_css_source}")

    state_dir = profile / STATE_DIR_NAME
    reject_symlink(state_dir, "install state directory")
    state_path = state_dir / STATE_NAME
    reject_symlink(state_path, "install record")
    legacy_state_path = profile / LEGACY_STATE_DIR_NAME / STATE_NAME
    reject_symlink(profile / LEGACY_STATE_DIR_NAME, "legacy install state directory")
    reject_symlink(legacy_state_path, "legacy install record")
    if legacy_state_path.is_file():
        raise InstallError(
            f"an Aurora Glass installation is present in {profile}; restore it before installing Vesperwing Glass"
        )
    if state_path.exists():
        raise InstallError(
            f"Vesperwing Glass is already installed in {profile}; restore it before reinstalling"
        )

    chrome_dir = profile / "chrome"
    reject_symlink(chrome_dir, "chrome directory")
    chrome_dir_existed = chrome_dir.exists()
    if chrome_dir.exists() and not chrome_dir.is_dir():
        raise InstallError(f"profile chrome path is not a directory: {chrome_dir}")

    state_dir.mkdir(parents=True, exist_ok=True)
    backup_dir = make_backup_dir(state_dir)
    relative_files = [*ENTRYPOINTS, CSS_DESTINATION, CONTENT_CSS_DESTINATION, "user.js"]
    files: dict[str, dict[str, object]] = {}
    for relative in relative_files:
        files[relative] = backup_file(profile, backup_dir, relative)

    state: dict[str, object] = {
        "schema_version": 1,
        "profile": str(profile),
        "installed_at_utc": datetime.now(timezone.utc).isoformat(),
        "backup_dir": str(backup_dir.relative_to(profile)),
        "chrome_dir_existed": chrome_dir_existed,
        "css_source": str(css_source),
        "content_css_source": str(content_css_source),
        "files": files,
        "generated_sha256": {},
        "user_js_marker": PREF_MARKER,
    }

    generated = {
        CHROME_ENTRYPOINT: IMPORT_TEXT.encode("utf-8") + ((profile / CHROME_ENTRYPOINT).read_bytes() if (profile / CHROME_ENTRYPOINT).exists() else b""),
        CONTENT_ENTRYPOINT: CONTENT_DEFAULTS_TEXT.encode("utf-8") + ((profile / CONTENT_ENTRYPOINT).read_bytes() if (profile / CONTENT_ENTRYPOINT).exists() else b""),
        CSS_DESTINATION: css_source.read_bytes(),
        CONTENT_CSS_DESTINATION: content_css_source.read_bytes(),
    }
    generated_hashes = {name: sha256(data) for name, data in generated.items()}
    state["generated_sha256"] = generated_hashes

    try:
        for relative, data in generated.items():
            atomic_write(profile / relative, data)
        append_user_pref(profile / "user.js")
        state_bytes = (json.dumps(state, indent=2) + "\n").encode("utf-8")
        atomic_write(state_path, state_bytes)
    except Exception:
        for relative in relative_files:
            record = files[relative]
            destination = profile / relative
            if record.get("existed"):
                backup = profile / str(record["backup"])
                if backup.exists():
                    atomic_write(destination, backup.read_bytes(), backup.stat().st_mode & 0o777)
            else:
                destination.unlink(missing_ok=True)
        if not chrome_dir_existed:
            try:
                chrome_dir.rmdir()
            except OSError:
                pass
        shutil.rmtree(backup_dir, ignore_errors=True)
        raise

    print(f"Installed Vesperwing Glass profile CSS in {profile}")
    print(f"Backup saved at {backup_dir}")
    print("Restart Thunderbird to load the chrome stylesheets.")


def remove_managed_pref(profile: Path, state: dict[str, object]) -> None:
    user_js = profile / "user.js"
    reject_symlink(user_js, "user.js")
    files = state["files"]
    assert isinstance(files, dict)
    prior_user_js = files["user.js"]
    assert isinstance(prior_user_js, dict)
    if not user_js.is_file():
        if prior_user_js.get("existed"):
            restore_original_file(profile, state, "user.js")
        return
    marker_value = state.get("user_js_marker", PREF_MARKER)
    if not isinstance(marker_value, str):
        raise InstallError("install record has an invalid managed preference marker")
    marker = marker_value.encode("utf-8")
    original_current = user_js.read_bytes()
    lines = original_current.splitlines(keepends=True)
    marker_lines = [line for line in lines if marker in line]
    if not marker_lines:
        print(
            f"Warning: managed preference line is absent from {user_js}; left it unchanged",
            file=sys.stderr,
        )
        return
    if len(marker_lines) != 1:
        raise InstallError(f"expected one managed preference line in {user_js}")
    filtered = [line for line in lines if marker not in line]
    updated = b"".join(filtered)

    if prior_user_js.get("existed"):
        backup = profile / str(prior_user_js["backup"])
        original = backup.read_bytes()
        separator = b"" if not original or original.endswith((b"\n", b"\r")) else b"\n"
        if updated == original + separator:
            shutil.copy2(backup, user_js)
            return
    if not prior_user_js.get("existed") and not updated.strip():
        user_js.unlink()
    else:
        atomic_write(user_js, updated)


def restore(profile_arg: Path, force: bool) -> None:
    profile = validate_profile(profile_arg)
    state_dir = profile / STATE_DIR_NAME
    state_path = state_dir / STATE_NAME
    legacy_state_dir = profile / LEGACY_STATE_DIR_NAME
    legacy_state_path = legacy_state_dir / STATE_NAME
    reject_symlink(state_dir, "install state directory")
    reject_symlink(state_path, "install record")
    reject_symlink(legacy_state_dir, "legacy install state directory")
    reject_symlink(legacy_state_path, "legacy install record")
    if not state_path.is_file() and legacy_state_path.is_file():
        state_dir, state_path = legacy_state_dir, legacy_state_path
    if not state_path.is_file():
        raise InstallError(f"Vesperwing Glass install record not found in {profile}")
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(state, dict):
        raise InstallError("install record is malformed")
    if state.get("schema_version") != 1 or state.get("profile") != str(profile):
        raise InstallError(f"install record does not match profile {profile}")

    generated_hashes = state.get("generated_sha256")
    files = state.get("files")
    if not isinstance(generated_hashes, dict) or not isinstance(files, dict):
        raise InstallError("install record is malformed")

    package_css = (CSS_DESTINATION, CONTENT_CSS_DESTINATION)
    if state_dir.name == LEGACY_STATE_DIR_NAME:
        package_css = (LEGACY_CSS_DESTINATION, LEGACY_CONTENT_CSS_DESTINATION)
    expected_files = {*ENTRYPOINTS, *package_css, "user.js"}
    if set(files) != expected_files or set(generated_hashes) != {
        *ENTRYPOINTS, *package_css
    }:
        raise InstallError("install record is malformed")

    # Validate every backup and target before changing any profile files. This
    # keeps a missing/corrupt backup or an unsafe symlink from causing a partial
    # restore.
    reject_symlink(profile / "chrome", "chrome directory")
    for relative in expected_files:
        record = files[relative]
        if not isinstance(record, dict) or not isinstance(record.get("existed"), bool):
            raise InstallError(f"install record is malformed for {relative}")
        destination = profile / relative
        reject_symlink(destination, "profile file")
        if destination.exists() and not destination.is_file():
            raise InstallError(f"profile target is not a regular file: {destination}")
        if record["existed"]:
            backup_rel = record.get("backup")
            if not isinstance(backup_rel, str):
                raise InstallError(f"backup path is missing for {relative}")
            backup = (profile / backup_rel).resolve()
            try:
                backup.relative_to(state_dir.resolve())
            except ValueError as error:
                raise InstallError(f"backup path escapes install state directory: {backup_rel}") from error
            if not backup.is_file():
                raise InstallError(f"backup is missing for {relative}: {backup}")
            if (profile / backup_rel).is_symlink():
                raise InstallError(f"backup is a symlink for {relative}: {backup_rel}")

    user_js = profile / "user.js"
    if user_js.is_file():
        marker_value = state.get("user_js_marker", PREF_MARKER)
        if not isinstance(marker_value, str):
            raise InstallError("install record has an invalid managed preference marker")
        marker_count = sum(
            marker_value.encode("utf-8") in line
            for line in user_js.read_bytes().splitlines()
        )
        if marker_count > 1:
            raise InstallError(f"expected one managed preference line in {user_js}")

    changed = []
    for relative, expected in generated_hashes.items():
        current = profile / relative
        if not current.is_file() or sha256(current.read_bytes()) != expected:
            changed.append(relative)
    if changed and not force:
        changed_names = ", ".join(changed)
        raise InstallError(
            f"installed files were edited after installation ({changed_names}); "
            "review them, then use --force to restore the saved originals"
        )

    for relative in (*ENTRYPOINTS, *package_css):
        restore_original_file(profile, state, relative)
    remove_managed_pref(profile, state)

    state_path.unlink()
    chrome_dir = profile / "chrome"
    if not state.get("chrome_dir_existed") and chrome_dir.is_dir():
        try:
            chrome_dir.rmdir()
        except OSError:
            pass

    backup_dir = profile / str(state["backup_dir"])
    print(f"Restored Vesperwing Glass settings in {profile}")
    print(f"Preserved backup at {backup_dir}")
    print("Restart Thunderbird to apply the restored profile files.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    install_parser = subparsers.add_parser("install", help="install the glass CSS")
    install_parser.add_argument("--profile", type=Path, required=True)
    install_parser.add_argument("--css", type=Path, default=DEFAULT_CSS)
    install_parser.add_argument("--content-css", type=Path, default=DEFAULT_CONTENT_CSS)

    restore_parser = subparsers.add_parser("restore", help="restore the saved profile files")
    restore_parser.add_argument("--profile", type=Path, required=True)
    restore_parser.add_argument(
        "--force",
        action="store_true",
        help="restore originals even if generated stylesheet files were edited",
    )

    args = parser.parse_args()
    try:
        if args.command == "install":
            install(args.profile, args.css, args.content_css)
        else:
            restore(args.profile, args.force)
    except (InstallError, OSError, json.JSONDecodeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
