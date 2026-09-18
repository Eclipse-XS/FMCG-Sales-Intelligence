# DVC remote status

The tracked default remote is `gdrive://1eOCs3trjFQAAQDagx59FcgEhlEik_hQm`. Credentials and OAuth tokens are not stored in Git. `dvc push` reached Google OAuth but was not completed because interactive account consent is a user-only security boundary. Therefore remote population and cross-machine `dvc pull` are **BLOCKED_AUTH**, not PASS.

After the owner authorizes the account, run `dvc push`, clone into an isolated directory, install from locked requirements, run `dvc pull`, and verify `dvc status`, model readiness, tests, and dashboard build. Until that succeeds, only local-cache reproducibility is proven.
