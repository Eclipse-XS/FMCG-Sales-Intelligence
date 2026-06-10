# DVC Google Drive remote V1

The tracked default DVC remote is `gdrive`, backed by the private Google Drive folder `gdrive://1eOCs3trjFQAAQDagx59FcgEhlEik_hQm`. DVC owns the content-addressed object layout; it must not be rearranged into human-readable folders.

Git stores code, `dvc.yaml`, `dvc.lock`, `.dvc` pointers and the non-secret remote URL. DVC stores processed datasets and canonical artifacts. MLflow stores run/registry metadata and does not replace DVC. Raw donor data, local caches, OAuth tokens, `.env`, and MLflow runtime state stay private and untracked.

Authorized workflow:

```powershell
.venv\Scripts\dvc.exe remote list
.venv\Scripts\dvc.exe pull
.venv\Scripts\dvc.exe status
.venv\Scripts\dvc.exe push
```

Google account permission and normal OAuth consent are required. Never commit a client secret, token, credential JSON, or `.dvc/config.local`; do not make the folder public. At V1.1 the configuration and ownership audit pass, but remote population is `BLOCKED_AUTH` until the owner completes consent.
