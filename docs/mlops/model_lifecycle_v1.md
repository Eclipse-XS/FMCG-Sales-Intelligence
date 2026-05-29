# Model lifecycle V1

Data/contracts → explicit offline experiment → DVC canonical artifact → scientific review/freeze → idempotent MLflow metadata import → explicit serving version → prediction logging → delayed-label monitoring. No online training or automatic promotion/rollback exists. Immediate service metrics are request/readiness metrics; WAPE and average precision require later matured labels.

