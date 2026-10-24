# GitHub publication checklist

- [ ] Check institution/supervisor rules before publishing research material.
- [ ] Check Solomon input-data redistribution terms; if necessary remove `data/solomon/*.txt` and document download instructions.
- [ ] Review report and manifests for personal information and sensitive data.
- [ ] Run `python -m unittest discover -s tests` locally with OR-Tools installed.
- [ ] Verify both route folders using the commands in README.
- [ ] Review `git status` before committing; ensure `.idea`, `__pycache__`, `.env` are excluded.
- [ ] Upload extracted project **contents**, not the ZIP as a single repository file.
- [ ] Keep old exploratory results backed up locally; do not overwrite published data.
