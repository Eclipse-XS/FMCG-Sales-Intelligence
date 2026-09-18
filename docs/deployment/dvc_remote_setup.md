# Future DVC remote setup

No DVC remote is configured. Git contains source, contracts, pointers and pipeline metadata; a fresh machine cannot retrieve cached datasets/models. An S3-compatible remote is recommended for durable automation and GitHub compatibility. Google Drive is simpler for a single-user demonstration but weaker for unattended CI. Configure credentials outside Git, push DVC objects, then prove reproduction in a clean clone before claiming cross-machine reproducibility.

