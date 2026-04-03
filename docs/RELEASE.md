# Release Guide

This project publishes a GitHub Release automatically when you push a Git tag that matches `v*` (for example `v0.2.0`).

The workflow used is [.github/workflows/build-release.yml](.github/workflows/build-release.yml).

## What Happens On Release

When you push a tag like `v0.2.0`, GitHub Actions will:

1. Build binaries on Windows, macOS, and Linux using PyInstaller.
2. Rename the artifacts to:
	- `Apilage-Downloader-Windows.exe`
	- `Apilage-Downloader-macOS`
	- `Apilage-Downloader-Linux`
3. Create a GitHub Release named `Apilage Downloader <tag>`.
4. Attach the three binaries to that release.

## Before You Release

Run these checks locally first:

1. Make sure you are on the main branch and up to date.
2. Ensure all changes are committed.
3. Run the app once locally:

```bash
python3 main.py
```

4. Confirm release metadata is updated when needed:
	- Project version in [pyproject.toml](pyproject.toml)
	- User-facing notes in [README.md](README.md)

## Create a New Release

Use semantic versioning tags (`vMAJOR.MINOR.PATCH`), for example `v0.2.0`.

```bash
git checkout main
git pull origin main

# Create annotated tag
git tag -a v0.2.0 -m "Release v0.2.0"

# Push commit(s) and tag
git push origin main
git push origin v0.2.0
```

After the tag is pushed, monitor Actions:

1. Open repository `Actions` tab.
2. Open the `Build and Release` run for your tag.
3. Wait for both `build` and `release` jobs to pass.

## Verify The Release

After the workflow succeeds:

1. Open repository `Releases`.
2. Confirm a release exists for your tag.
3. Confirm these assets are attached:
	- `Apilage-Downloader-Windows.exe`
	- `Apilage-Downloader-macOS`
	- `Apilage-Downloader-Linux`
4. Download one asset and do a quick launch check.

## If You Need To Re-Release The Same Version

If a tag was created incorrectly, delete and recreate it.

```bash
# Delete local tag
git tag -d v0.2.0

# Delete remote tag
git push --delete origin v0.2.0

# Recreate and push
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

Note: If a GitHub Release object already exists for that tag, remove or edit it from the `Releases` page before retrying.

## Troubleshooting

If workflow does not start:

1. Confirm your tag starts with `v`.
2. Confirm the tag was pushed to `origin`.
3. Confirm workflow file exists on default branch.

If build fails:

1. Open failed job logs in Actions.
2. Check icon paths used by PyInstaller:
	- `assets/icon.ico` (Windows)
	- `assets/icon.icns` (macOS)
3. Verify entry file path `main.py` is still correct.

If release job fails to upload assets:

1. Confirm artifact names/paths were not changed in workflow.
2. Confirm expected files exist in `dist/` in each build job.

## Recommended Improvement

Current workflow installs Python `3.11`, while [pyproject.toml](pyproject.toml) states `>=3.12`.
Consider aligning these versions to avoid future compatibility surprises.
