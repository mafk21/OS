# Release process

JARVIS releases begin as drafts and must be reviewed by a maintainer before publication.

## Prerequisites

- All required checks on `main` are green.
- Dependency, secret, CodeQL, and privacy scans are clear or reviewed.
- Installation is manually tested on clean Windows, macOS, and Linux systems.
- Release notes disclose known limitations and breaking changes.

## Create a beta release

```bash
git checkout main
git pull --ff-only
git tag -s v1.0.0-beta.1 -m "JARVIS v1.0.0-beta.1"
git push origin v1.0.0-beta.1
```

A `v*` tag triggers `.github/workflows/release.yml`. It reruns the cross-platform matrix, creates clean source packages and SHA-256 checksums, and opens a **draft** GitHub release. Review every artifact and note before publishing it.

## Signing status

The automated archives are checksum-protected source packages, not code-signed native installers. Do not describe them as signed. Native Windows signing and macOS signing/notarization require private certificates held outside GitHub and must be added only through protected repository/environment secrets. Never commit signing keys.

## Rollback

If an unpublished draft is wrong, delete the draft and tag, fix `main` through a pull request, and create a new tag. If a published release has a security defect, publish a fixed release and advisory; do not silently replace artifacts under an existing version.
