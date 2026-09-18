# Store Segmentation Modeling V1

Store Segmentation V1 is exploratory unsupervised clustering of physical stores. It does not use or produce ground-truth labels and it does not train Segment Assignment.

The source artifact contains 60 rows: 20 stores observed at three month-end snapshots. The primary clustering cohort uses the latest eligible snapshot per store, 2024-03-30, and therefore has 20 independent units. The 40 earlier rows are retained only for temporal stability diagnostics.

## Feature contract

The frozen clustering features are `revenue_30d`, `average_price_30d`, `promotion_unit_share_30d`, and `revenue_volatility_30d`. IDs and region/store/channel context do not enter Euclidean distance. Units and profit are removed as redundant with revenue, floor area is static capacity context and highly correlated with volume, and active SKU count is constant in the reference cohort.

RobustScaler is fitted on the 20-store reference cohort. No outlier store is removed and no log transform is applied.

## Candidates and selection

KMeans and Ward agglomerative clustering are evaluated at k=2..5 using silhouette, Davies–Bouldin, Calinski–Harabasz, cluster sizes, historical assignment retention, and interpretation. There is no supervised train/test split. The frozen V1 choice is KMeans with k=3. Raw IDs are canonicalized by ascending centroid projection on the first principal component.

## Pseudo-labels and limitations

Latest-snapshot assignments are versioned pseudo-labels carrying `PSEUDO_LABEL_NOT_GROUND_TRUTH`. Historical assignments use the same scaler and frozen centroids. Distance to centroid is not a probability.

The data are synthetic, span about 90 days, and contain only 20 independent stores and three snapshots per store. Internal metrics measure geometry under this representation, not natural or statistically proven store types. Future Segment Assignment readiness depends on measured stability.

## Reproduction

```powershell
.venv\Scripts\python.exe -m src.modeling.cli run --task segmentation --output artifacts/canonical/segmentation_v1 --experiment-id segmentation_v1_canonical --overwrite
```
