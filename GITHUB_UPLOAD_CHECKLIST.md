# GitHub Upload Checklist

Before uploading or updating the public repository:

- [ ] Run `python -m unittest discover -s tests -v`.
- [ ] Check that no passwords, API keys, tokens, private URLs, or `.env` files are included.
- [ ] Remove `__pycache__`, `.pyc`, temporary files, and local IDE settings.
- [ ] Confirm that generated result files are intended to be public.
- [ ] Update `README.md` if project status or run commands changed.
- [ ] Update `docs/PROJECT_STATUS.md` after a major development step.
- [ ] Use a clear Git commit message describing the change.
