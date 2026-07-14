# Segment assignment resolution V1.2

## Decision

The original `Segment Assignment` requirement mixed two different problems. A supervised business-segment classifier requires stable external labels and remains `DEFERRED_NOT_JUSTIFIED_V1`. The existing cluster IDs are exploratory pseudo-labels with approximately 52.5% temporal retention, not business ground truth, so no classifier was trained.

The frozen Segmentation V1 artifact does contain sufficient state for a narrower operation: a fitted `RobustScaler`, exact four-feature order, fitted KMeans model with `k=3`, centroids, canonical cluster mapping, profile labels, and artifact version. V1.2 therefore exposes `segment_cluster_membership_assignment` as `ACTIVE_EXPERIMENTAL`.

## Runtime contract

`POST /api/v1/analytics/segments/assign` accepts `store_id` plus the exact frozen features: `revenue_30d`, `average_price_30d`, `promotion_unit_share_30d`, and `revenue_volatility_30d`. It applies the persisted scaler and KMeans `.predict()` without fitting. The response includes cluster ID, profile label, geometric centroid distance, artifact fingerprint, model and contract versions, and explicit caveats.

Centroid distance is not probability, confidence, or calibration. Cluster names are descriptive labels derived from the frozen reference snapshot. Scientific status is exploratory, taxonomy stability is limited, human review is required, and labels remain `PSEUDO_LABEL_NOT_GROUND_TRUTH`.

## Safety and future requirement

Tests prohibit implicit fitting, enforce feature order, verify deterministic reference assignment, reject missing/unknown/non-finite features, confirm generic-domain behavior, and ensure no probability/confidence claim is emitted. A future supervised classifier requires externally governed business labels, materially more stores and history, stable taxonomy definitions, temporal validation, and a separate scientific review.
