# Data source inventory

Generated from immutable local artifacts. Profiles are bounded to 250,000 rows per tabular file; hashes cover full files.

## coca_cola_reference

- Status: `profiled`
- URL: https://github.com/Chad-Lines/Data-Projects/tree/main/Coca-Cola%20Sales%20Data%20Visualiation
- Provenance: educational/unknown upstream
- License: not identified
- Redistribution: verify repository/upstream rights
- Intended use: reporting reference only
- Grain: must be confirmed per file from columns and source documentation
- Limitations: Profiles are bounded samples; semantic keys require source-specific review.
- Files: 5

### `data\raw\coca_cola_reference\1.png`

Size: 57420 bytes. Profiled rows: n/a. Duplicates in profile: n/a.

### `data\raw\coca_cola_reference\2.png`

Size: 341573 bytes. Profiled rows: n/a. Duplicates in profile: n/a.

### `data\raw\coca_cola_reference\3.png`

Size: 108168 bytes. Profiled rows: n/a. Duplicates in profile: n/a.

### `data\raw\coca_cola_reference\4.png`

Size: 162270 bytes. Profiled rows: n/a. Duplicates in profile: n/a.

### `data\raw\coca_cola_reference\Project Explanation.md`

Size: 4095 bytes. Profiled rows: n/a. Duplicates in profile: n/a.

## dunnhumby

- Status: `profiled`
- URL: https://github.com/bltap-plmarket/dunnhumby-complete-journey
- Provenance: real retail donor via third-party representation
- License: not identified
- Redistribution: verify upstream license
- Intended use: basket and promotion distributions
- Grain: must be confirmed per file from columns and source documentation
- Limitations: Profiles are bounded samples; semantic keys require source-specific review.
- Files: 27

### `data\raw\dunnhumby\_columns.parquet`

Size: 4834 bytes. Profiled rows: 91. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| table_name | str | 0.0 | 11 |
| column_name | str | 0.0 | 75 |
| data_type | str | 0.0 | 5 |
| description | str | 0.0 | 30 |

### `data\raw\dunnhumby\_hierarchies.parquet`

Size: 3116 bytes. Profiled rows: 8. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| table_name | str | 0.0 | 2 |
| hierarchy_name | str | 0.0 | 2 |
| level_order | int64 | 0.0 | 5 |
| level_column | str | 0.0 | 8 |

### `data\raw\dunnhumby\_measures.parquet`

Size: 5459 bytes. Profiled rows: 23. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| measure_name | str | 0.0 | 23 |
| host_table | str | 0.0 | 4 |
| expression | str | 0.0 | 23 |
| format_string | str | 0.0 | 4 |
| description | str | 0.0 | 4 |
| category | str | 0.0 | 6 |

### `data\raw\dunnhumby\_model.json`

Size: 17538 bytes. Profiled rows: n/a. Duplicates in profile: n/a.

### `data\raw\dunnhumby\_relationships.parquet`

Size: 5295 bytes. Profiled rows: 14. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| from_table | str | 0.0 | 5 |
| from_column | str | 0.0 | 7 |
| to_table | str | 0.0 | 6 |
| to_column | str | 0.0 | 7 |
| cardinality | str | 0.0 | 1 |
| cross_filter | str | 0.0 | 1 |
| comment | str | 0.0 | 2 |

### `data\raw\dunnhumby\_tables.parquet`

Size: 5956 bytes. Profiled rows: 11. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| table_name | str | 0.0 | 11 |
| source_file | str | 0.0 | 11 |
| kind | str | 0.0 | 4 |
| grain | str | 63.636 | 4 |
| primary_key | str | 45.455 | 6 |
| row_count | float64 | 63.636 | 4 |
| is_storytelling_table | bool | 0.0 | 2 |
| comment | str | 0.0 | 3 |

### `data\raw\dunnhumby\agg_commodity_cohort_yoy.parquet`

Size: 51784 bytes. Profiled rows: 1326. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| COMMODITY_DESC | string | 0.0 | 307 |
| DEPARTMENT | string | 0.0 | 43 |
| HH_Trend | string | 0.0 | 5 |
| Households_Y1 | float64 | 0.0 | 443 |
| Households_Y2 | float64 | 0.0 | 435 |
| Sales_Y1 | float64 | 0.0 | 1106 |
| Sales_Y2 | float64 | 0.0 | 1070 |
| Units_Y1 | float64 | 0.0 | 654 |
| Units_Y2 | float64 | 0.0 | 665 |
| Sales_Delta | float64 | 0.0 | 1266 |
| Sales_Delta_Pct | float64 | 13.499 | 933 |

### `data\raw\dunnhumby\agg_dept_yoy_by_cohort.parquet`

Size: 7920 bytes. Profiled rows: 146. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| DEPARTMENT | string | 0.0 | 44 |
| HH_Trend | string | 0.0 | 5 |
| Sales_Y1 | float64 | 0.0 | 109 |
| Sales_Y2 | float64 | 0.0 | 109 |
| Sales_Delta | float64 | 0.0 | 140 |
| Sales_Delta_Pct | float64 | 24.658 | 79 |

### `data\raw\dunnhumby\agg_household_campaign_lift.parquet`

Size: 1045627 bytes. Profiled rows: 75000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| household_key | int64 | 0.0 | 2500 |
| CAMPAIGN | int64 | 0.0 | 30 |
| CAMPAIGN_TYPE | str | 0.0 | 3 |
| Exposed | bool | 0.0 | 2 |
| Pre_Spend | float64 | 0.0 | 40065 |
| Post_Spend | float64 | 0.0 | 40146 |
| Spend_Delta | float64 | 0.0 | 48464 |
| Has_Complete_Post_Window | bool | 0.0 | 1 |
| Extends_Past_Observation | bool | 0.0 | 2 |

### `data\raw\dunnhumby\agg_promo_sales_weekly.parquet`

Size: 5721203 bytes. Profiled rows: 250000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| PRODUCT_ID | int32 | 0.0 | 17243 |
| WEEK_NO | int8 | 0.0 | 102 |
| Sales | float64 | 0.0 | 8257 |
| Units | int64 | 0.0 | 331 |
| Baskets | int64 | 0.0 | 130 |
| OnDisplay_AnyStore | bool | 0.0 | 2 |
| InMailer_AnyStore | bool | 0.0 | 2 |
| Stores_OnDisplay | int32 | 0.0 | 106 |
| Stores_InMailer | int32 | 0.0 | 123 |
| Total_Stores | int32 | 0.0 | 111 |
| DisplayShare | float64 | 0.0 | 1519 |
| MailerShare | float64 | 0.0 | 208 |

### `data\raw\dunnhumby\bridge_coupon_product.parquet`

Size: 441867 bytes. Profiled rows: 119384. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| COUPON_UPC | int64 | 0.0 | 1135 |
| PRODUCT_ID | int64 | 0.0 | 44133 |
| CAMPAIGN | int64 | 0.0 | 30 |

### `data\raw\dunnhumby\dim_campaign.parquet`

Size: 5833 bytes. Profiled rows: 30. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| CAMPAIGN_TYPE | str | 0.0 | 3 |
| CAMPAIGN | int64 | 0.0 | 30 |
| START_DAY | int64 | 0.0 | 27 |
| END_DAY | int64 | 0.0 | 28 |
| Duration_Days | int64 | 0.0 | 17 |
| Start_Week | int64 | 0.0 | 24 |
| End_Week | int64 | 0.0 | 26 |
| Extends_Past_Observation | bool | 0.0 | 2 |

### `data\raw\dunnhumby\dim_coupon.parquet`

Size: 12136 bytes. Profiled rows: 1135. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| COUPON_UPC | int64 | 0.0 | 1135 |
| CAMPAIGN | int64 | 0.0 | 30 |
| Eligible_Product_Count | int64 | 0.0 | 140 |
| Redemption_Count | int64 | 0.0 | 33 |
| Was_Redeemed | bool | 0.0 | 2 |

### `data\raw\dunnhumby\dim_date.parquet`

Size: 14144 bytes. Profiled rows: 711. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| Day_Idx | int64 | 0.0 | 711 |
| Week_No | int64 | 0.0 | 102 |
| Year_Idx | int64 | 0.0 | 2 |
| Half_Idx | int64 | 0.0 | 4 |
| Quarter_Idx | int64 | 0.0 | 8 |
| Month_Idx | int64 | 0.0 | 24 |
| DayOfWeek | int64 | 0.0 | 7 |
| AnchorDate | datetime64[us] | 0.0 | 711 |
| YearMonth | str | 0.0 | 24 |
| YearLabel | str | 0.0 | 2 |
| WeekLabel | str | 0.0 | 102 |

### `data\raw\dunnhumby\dim_household.parquet`

Size: 145234 bytes. Profiled rows: 2500. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| household_key | int32 | 0.0 | 2500 |
| AGE_DESC | string | 0.0 | 7 |
| MARITAL_STATUS_CODE | string | 0.0 | 4 |
| INCOME_DESC | string | 0.0 | 13 |
| HOMEOWNER_DESC | string | 0.0 | 6 |
| HH_COMP_DESC | string | 0.0 | 7 |
| HOUSEHOLD_SIZE_DESC | string | 0.0 | 6 |
| KID_CATEGORY_DESC | string | 0.0 | 5 |
| HasDemographics | bool | 0.0 | 2 |
| ReceivedAnyCampaign | bool | 0.0 | 2 |
| Campaign_Count | int16 | 0.0 | 18 |
| RedeemedAnyCoupon | bool | 0.0 | 2 |
| Redemption_Count | int16 | 0.0 | 30 |
| Spend_Y1 | float64 | 0.0 | 2486 |
| Spend_Y2 | float64 | 0.0 | 2470 |
| Spend_Total | float64 | 0.0 | 2497 |
| Spend_Delta | float64 | 0.0 | 2496 |
| Spend_Delta_Pct | float64 | 0.12 | 2477 |
| HH_Trend | string | 0.0 | 5 |
| Basket_Count | int32 | 0.0 | 395 |
| Avg_Basket_Value | float64 | 0.0 | 2500 |
| First_Day | int16 | 0.0 | 128 |
| Last_Day | int16 | 0.0 | 200 |
| Active_Days | int16 | 0.0 | 284 |

### `data\raw\dunnhumby\dim_product.parquet`

Size: 880861 bytes. Profiled rows: 92353. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| PRODUCT_ID | int64 | 0.0 | 92353 |
| MANUFACTURER | int64 | 0.0 | 6476 |
| DEPARTMENT | string | 0.0 | 44 |
| BRAND | string | 0.0 | 2 |
| COMMODITY_DESC | string | 0.0 | 308 |
| SUB_COMMODITY_DESC | string | 0.0 | 2383 |
| CURR_SIZE_OF_PRODUCT | string | 0.0 | 4345 |
| Has_Real_Category | boolean | 0.0 | 2 |
| Is_Private_Brand | bool[pyarrow] | 0.0 | 2 |

### `data\raw\dunnhumby\dim_store.parquet`

Size: 3207 bytes. Profiled rows: 582. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| STORE_ID | int32 | 0.0 | 582 |

### `data\raw\dunnhumby\fact_campaign_received.parquet`

Size: 13843 bytes. Profiled rows: 7208. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| household_key | int64 | 0.0 | 1584 |
| CAMPAIGN | int64 | 0.0 | 30 |

### `data\raw\dunnhumby\fact_causal_weekly.parquet`

Size: 5708673 bytes. Profiled rows: 250000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| PRODUCT_ID | int32 | 0.0 | 5921 |
| WEEK_NO | int8 | 0.0 | 93 |
| OnDisplay_AnyStore | bool | 0.0 | 2 |
| InMailer_AnyStore | bool | 0.0 | 2 |
| Stores_OnDisplay | int32 | 0.0 | 108 |
| Stores_InMailer | int32 | 0.0 | 131 |
| Total_Stores | int32 | 0.0 | 110 |
| DisplayShare | float64 | 0.0 | 1730 |
| MailerShare | float64 | 0.0 | 300 |

### `data\raw\dunnhumby\fact_coupon_redemption.parquet`

Size: 14798 bytes. Profiled rows: 2318. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| household_key | int64 | 0.0 | 434 |
| DAY | int64 | 0.0 | 328 |
| COUPON_UPC | int64 | 0.0 | 556 |
| CAMPAIGN | int64 | 0.0 | 30 |

### `data\raw\dunnhumby\fact_transactions.parquet`

Size: 22927021 bytes. Profiled rows: 250000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| household_key | int32 | 0.0 | 2491 |
| BASKET_ID | int64 | 0.0 | 27796 |
| DAY | int16 | 0.0 | 125 |
| PRODUCT_ID | int32 | 0.0 | 34192 |
| QUANTITY | int64 | 0.0 | 1510 |
| SALES_VALUE | float64 | 0.0 | 2579 |
| STORE_ID | int32 | 0.0 | 278 |
| RETAIL_DISC | float64 | 0.0 | 1150 |
| TRANS_TIME | int16 | 0.0 | 1341 |
| WEEK_NO | int8 | 0.0 | 19 |
| COUPON_DISC | float64 | 0.0 | 111 |
| COUPON_MATCH_DISC | float64 | 0.0 | 27 |
| GROSS_SALES | float64 | 0.0 | 3940 |
| TOTAL_DISC | float64 | 0.0 | 1239 |
| TRANS_HOUR | int8 | 0.0 | 24 |

### `data\raw\dunnhumby\investigation_findings.json`

Size: 13861 bytes. Profiled rows: n/a. Duplicates in profile: n/a.

### `data\raw\dunnhumby\investigation_findings.md`

Size: 11742 bytes. Profiled rows: n/a. Duplicates in profile: n/a.

### `data\raw\dunnhumby\measures.dax`

Size: 4094 bytes. Profiled rows: n/a. Duplicates in profile: n/a.

### `data\raw\dunnhumby\README.md`

Size: 12314 bytes. Profiled rows: n/a. Duplicates in profile: n/a.

### `data\raw\dunnhumby\storyboard.json`

Size: 8484 bytes. Profiled rows: n/a. Duplicates in profile: n/a.

### `data\raw\dunnhumby\theme.json`

Size: 1339 bytes. Profiled rows: n/a. Duplicates in profile: n/a.

## favorita

- Status: `profiled`
- URL: https://www.kaggle.com/datasets/evgeniypolin/favorita-grocery-sales-forecasting
- Provenance: public Kaggle mirror; upstream is Corporacion Favorita competition data
- License: mirror license unspecified
- Redistribution: do not redistribute raw; upstream competition terms and mirror rights unresolved
- Intended use: primary sales backbone
- Grain: must be confirmed per file from columns and source documentation
- Limitations: Profiles are bounded samples; semantic keys require source-specific review.
- Files: 8

### `holidays_events.csv/holidays_events.csv`

Size: 890850000 bytes. Profiled rows: 350. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| date | str | 0.0 | 312 |
| type | str | 0.0 | 6 |
| locale | str | 0.0 | 3 |
| locale_name | str | 0.0 | 24 |
| description | str | 0.0 | 103 |
| transferred | bool | 0.0 | 2 |

### `items.csv/items.csv`

Size: 890850000 bytes. Profiled rows: 4100. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| item_nbr | int64 | 0.0 | 4100 |
| family | str | 0.0 | 33 |
| class | int64 | 0.0 | 337 |
| perishable | int64 | 0.0 | 2 |

### `oil.csv/oil.csv`

Size: 890850000 bytes. Profiled rows: 1218. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| date | str | 0.0 | 1218 |
| dcoilwtico | float64 | 3.53 | 998 |

### `sample_submission.csv/sample_submission.csv`

Size: 890850000 bytes. Profiled rows: 250000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| id | int64 | 0.0 | 250000 |
| unit_sales | int64 | 0.0 | 1 |

### `stores.csv/stores.csv`

Size: 890850000 bytes. Profiled rows: 54. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| store_nbr | int64 | 0.0 | 54 |
| city | str | 0.0 | 22 |
| state | str | 0.0 | 16 |
| type | str | 0.0 | 5 |
| cluster | int64 | 0.0 | 17 |

### `test.csv/test.csv`

Size: 890850000 bytes. Profiled rows: 250000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| id | int64 | 0.0 | 250000 |
| date | str | 0.0 | 2 |
| store_nbr | int64 | 0.0 | 54 |
| item_nbr | int64 | 0.0 | 3901 |
| onpromotion | bool | 0.0 | 2 |

### `train.csv/train.csv`

Size: 890850000 bytes. Profiled rows: 250000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| id | int64 | 0.0 | 250000 |
| date | str | 0.0 | 8 |
| store_nbr | int64 | 0.0 | 46 |
| item_nbr | int64 | 0.0 | 1602 |
| unit_sales | float64 | 0.0 | 9615 |
| onpromotion | float64 | 100.0 | 0 |

### `transactions.csv/transactions.csv`

Size: 890850000 bytes. Profiled rows: 83488. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| date | str | 0.0 | 1682 |
| store_nbr | int64 | 0.0 | 54 |
| transactions | int64 | 0.0 | 4993 |

## fmcg_daily

- Status: `profiled`
- URL: https://www.kaggle.com/datasets/beatafaron/fmcg-daily-sales-data-to-2022-2024
- Provenance: synthetic
- License: not identified
- Redistribution: verify Kaggle dataset license
- Intended use: FMCG semantic/statistical donor
- Grain: must be confirmed per file from columns and source documentation
- Limitations: Profiles are bounded samples; semantic keys require source-specific review.
- Files: 7

### `data\raw\fmcg_daily\batch_MI-006_2025-01-06.parquet`

Size: 11332 bytes. Profiled rows: 135. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| date | datetime64[us] | 0.0 | 5 |
| sku | str | 0.0 | 1 |
| brand | str | 0.0 | 1 |
| segment | str | 0.0 | 1 |
| category | str | 0.0 | 1 |
| channel | str | 0.0 | 3 |
| region | str | 0.0 | 3 |
| pack_type | str | 0.0 | 3 |
| price_unit | float64 | 0.0 | 92 |
| promotion_flag | int64 | 0.0 | 2 |
| delivery_days | int64 | 0.0 | 4 |
| stock_available | int64 | 0.0 | 93 |
| delivered_qty | int64 | 0.0 | 53 |
| units_sold | int64 | 0.0 | 20 |

### `data\raw\fmcg_daily\batch_MI-006_2025-01-13.parquet`

Size: 11764 bytes. Profiled rows: 189. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| date | datetime64[us] | 0.0 | 7 |
| sku | str | 0.0 | 1 |
| brand | str | 0.0 | 1 |
| segment | str | 0.0 | 1 |
| category | str | 0.0 | 1 |
| channel | str | 0.0 | 3 |
| region | str | 0.0 | 3 |
| pack_type | str | 0.0 | 3 |
| price_unit | float64 | 0.0 | 122 |
| promotion_flag | int64 | 0.0 | 2 |
| delivery_days | int64 | 0.0 | 4 |
| stock_available | int64 | 0.0 | 108 |
| delivered_qty | int64 | 0.0 | 57 |
| units_sold | int64 | 0.0 | 20 |

### `data\raw\fmcg_daily\batch_MI-006_2025-01-20.parquet`

Size: 11723 bytes. Profiled rows: 189. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| date | datetime64[us] | 0.0 | 7 |
| sku | str | 0.0 | 1 |
| brand | str | 0.0 | 1 |
| segment | str | 0.0 | 1 |
| category | str | 0.0 | 1 |
| channel | str | 0.0 | 3 |
| region | str | 0.0 | 3 |
| pack_type | str | 0.0 | 3 |
| price_unit | float64 | 0.0 | 114 |
| promotion_flag | int64 | 0.0 | 2 |
| delivery_days | int64 | 0.0 | 4 |
| stock_available | int64 | 0.0 | 104 |
| delivered_qty | int64 | 0.0 | 56 |
| units_sold | int64 | 0.0 | 20 |

### `data\raw\fmcg_daily\batch_MI-006_2025-01-27.parquet`

Size: 11766 bytes. Profiled rows: 189. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| date | datetime64[us] | 0.0 | 7 |
| sku | str | 0.0 | 1 |
| brand | str | 0.0 | 1 |
| segment | str | 0.0 | 1 |
| category | str | 0.0 | 1 |
| channel | str | 0.0 | 3 |
| region | str | 0.0 | 3 |
| pack_type | str | 0.0 | 3 |
| price_unit | float64 | 0.0 | 116 |
| promotion_flag | int64 | 0.0 | 2 |
| delivery_days | int64 | 0.0 | 4 |
| stock_available | int64 | 0.0 | 114 |
| delivered_qty | int64 | 0.0 | 57 |
| units_sold | int64 | 0.0 | 20 |

### `data\raw\fmcg_daily\df_weekly_MI-006_enriched.csv`

Size: 354378 bytes. Profiled rows: 1349. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| sku | str | 0.0 | 1 |
| week | str | 0.0 | 150 |
| channel | str | 0.0 | 3 |
| region | str | 0.0 | 3 |
| units_sold | int64 | 0.0 | 171 |
| stock_available | float64 | 0.0 | 812 |
| promotion_flag | int64 | 0.0 | 2 |
| price_unit | float64 | 0.0 | 1194 |
| delivery_days | float64 | 0.0 | 62 |
| is_holiday_peak | bool | 0.0 | 2 |
| week_number | int64 | 0.0 | 52 |
| month | int64 | 0.0 | 12 |
| year | int64 | 0.0 | 3 |
| is_holiday_week | int64 | 0.0 | 2 |
| is_summer | int64 | 0.0 | 2 |
| is_winter | int64 | 0.0 | 2 |
| sku_age | int64 | 0.0 | 150 |
| lifecycle_stage | str | 0.0 | 3 |
| lag_1 | float64 | 0.0 | 171 |
| lag_2 | float64 | 0.0 | 171 |
| rolling_mean_4 | float64 | 0.0 | 376 |
| rolling_std_4 | float64 | 0.0 | 1312 |
| momentum | float64 | 0.0 | 194 |
| target_next_week | float64 | 0.0 | 178 |
| price_avg | float64 | 0.0 | 1194 |
| promo_rate | float64 | 0.0 | 14 |
| stock_avg | float64 | 0.0 | 812 |
| deliveries | int64 | 0.0 | 6 |
| avg_temp | float64 | 0.0 | 1349 |
| inflation_index | float64 | 0.0 | 1349 |
| school_in_session | int64 | 0.0 | 2 |
| category_trend | float64 | 0.0 | 1349 |
| event_score | float64 | 0.0 | 162 |

### `data\raw\fmcg_daily\FMCG_2022_2024.csv`

Size: 17747435 bytes. Profiled rows: 190757. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| date | str | 0.0 | 1076 |
| sku | str | 0.0 | 30 |
| brand | str | 0.0 | 14 |
| segment | str | 0.0 | 13 |
| category | str | 0.0 | 5 |
| channel | str | 0.0 | 3 |
| region | str | 0.0 | 3 |
| pack_type | str | 0.0 | 3 |
| price_unit | float64 | 0.0 | 751 |
| promotion_flag | int64 | 0.0 | 2 |
| delivery_days | int64 | 0.0 | 5 |
| stock_available | int64 | 0.0 | 355 |
| delivered_qty | int64 | 0.0 | 321 |
| units_sold | int64 | 0.0 | 135 |

### `data\raw\fmcg_daily\weekly_df_final_for_modeling.csv`

Size: 5005351 bytes. Profiled rows: 31027. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| sku | str | 0.0 | 30 |
| week | str | 0.0 | 150 |
| channel | str | 0.0 | 3 |
| region | str | 0.0 | 3 |
| units_sold | int64 | 0.0 | 310 |
| stock_available | float64 | 0.0 | 2223 |
| promotion_flag | int64 | 0.0 | 2 |
| price_unit | float64 | 0.0 | 8470 |
| delivery_days | float64 | 0.0 | 71 |
| is_holiday_peak | bool | 0.0 | 2 |
| week_number | int64 | 0.0 | 52 |
| month | int64 | 0.0 | 12 |
| year | int64 | 0.0 | 3 |
| is_holiday_week | int64 | 0.0 | 2 |
| is_summer | int64 | 0.0 | 2 |
| is_winter | int64 | 0.0 | 2 |
| sku_age | int64 | 0.0 | 150 |
| lifecycle_stage | str | 0.0 | 3 |
| lag_1 | float64 | 0.0 | 310 |
| lag_2 | float64 | 0.0 | 310 |
| rolling_mean_4 | float64 | 0.0 | 775 |
| rolling_std_4 | float64 | 0.0 | 24883 |
| momentum | float64 | 0.0 | 388 |
| target_next_week | float64 | 0.0 | 324 |

## grocery_inventory

- Status: `profiled`
- URL: https://www.kaggle.com/datasets/salahuddinahmedshuvo/grocery-inventory-and-sales-dataset
- Provenance: synthetic/unknown; verify dataset card
- License: not identified
- Redistribution: verify Kaggle dataset license
- Intended use: inventory parameter donor
- Grain: must be confirmed per file from columns and source documentation
- Limitations: Profiles are bounded samples; semantic keys require source-specific review.
- Files: 1

### `data\raw\grocery_inventory\Grocery_Inventory_and_Sales_Dataset.csv`

Size: 137097 bytes. Profiled rows: 990. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| Product_ID | str | 0.0 | 990 |
| Product_Name | str | 0.0 | 121 |
| Catagory | str | 0.101 | 7 |
| Supplier_ID | str | 0.0 | 990 |
| Supplier_Name | str | 0.0 | 350 |
| Stock_Quantity | int64 | 0.0 | 91 |
| Reorder_Level | int64 | 0.0 | 100 |
| Reorder_Quantity | int64 | 0.0 | 100 |
| Unit_Price | str | 0.0 | 112 |
| Date_Received | str | 0.0 | 351 |
| Last_Order_Date | str | 0.0 | 332 |
| Expiration_Date | str | 0.0 | 341 |
| Warehouse_Location | str | 0.0 | 990 |
| Sales_Volume | int64 | 0.0 | 81 |
| Inventory_Turnover_Rate | int64 | 0.0 | 100 |
| Status | str | 0.0 | 3 |

## instacart

- Status: `profiled`
- URL: https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis
- Provenance: public mirror of the Instacart competition files
- License: CC0-1.0 on mirror dataset card
- Redistribution: mirror declares CC0; upstream provenance remains documented
- Intended use: basket distributions
- Grain: must be confirmed per file from columns and source documentation
- Limitations: Profiles are bounded samples; semantic keys require source-specific review.
- Files: 6

### `aisles.csv`

Size: 207073669 bytes. Profiled rows: 134. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| aisle_id | int64 | 0.0 | 134 |
| aisle | str | 0.0 | 134 |

### `departments.csv`

Size: 207073669 bytes. Profiled rows: 21. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| department_id | int64 | 0.0 | 21 |
| department | str | 0.0 | 21 |

### `order_products__prior.csv`

Size: 207073669 bytes. Profiled rows: 250000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| order_id | int64 | 0.0 | 24758 |
| product_id | int64 | 0.0 | 23386 |
| add_to_cart_order | int64 | 0.0 | 68 |
| reordered | int64 | 0.0 | 2 |

### `order_products__train.csv`

Size: 207073669 bytes. Profiled rows: 250000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| order_id | int64 | 0.0 | 23648 |
| product_id | int64 | 0.0 | 24256 |
| add_to_cart_order | int64 | 0.0 | 76 |
| reordered | int64 | 0.0 | 2 |

### `orders.csv`

Size: 207073669 bytes. Profiled rows: 250000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| order_id | int64 | 0.0 | 250000 |
| user_id | int64 | 0.0 | 15117 |
| eval_set | str | 0.0 | 3 |
| order_number | int64 | 0.0 | 100 |
| order_dow | int64 | 0.0 | 7 |
| order_hour_of_day | int64 | 0.0 | 24 |
| days_since_prior_order | float64 | 6.047 | 31 |

### `products.csv`

Size: 207073669 bytes. Profiled rows: 49688. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| product_id | int64 | 0.0 | 49688 |
| product_name | str | 0.0 | 49688 |
| aisle_id | int64 | 0.0 | 134 |
| department_id | int64 | 0.0 | 21 |

## m5

- Status: `profiled`
- URL: https://doi.org/10.5281/zenodo.10203108
- Provenance: University of Nicosia Zenodo distribution; upstream is M5 Forecasting Accuracy
- License: record marked open; upstream competition provenance retained
- Redistribution: do not redistribute raw without confirming upstream terms
- Intended use: price/calendar/demand donor
- Grain: must be confirmed per file from columns and source documentation
- Limitations: Profiles are bounded samples; semantic keys require source-specific review.
- Files: 5

### `data\raw\m5\calendar.csv`

Size: 103469 bytes. Profiled rows: 1969. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| date | str | 0.0 | 1969 |
| wm_yr_wk | int64 | 0.0 | 282 |
| weekday | str | 0.0 | 7 |
| wday | int64 | 0.0 | 7 |
| month | int64 | 0.0 | 12 |
| year | int64 | 0.0 | 6 |
| d | str | 0.0 | 1969 |
| event_name_1 | str | 91.772 | 30 |
| event_type_1 | str | 91.772 | 4 |
| event_name_2 | str | 99.746 | 4 |
| event_type_2 | str | 99.746 | 2 |
| snap_CA | int64 | 0.0 | 2 |
| snap_TX | int64 | 0.0 | 2 |
| snap_WI | int64 | 0.0 | 2 |

### `data\raw\m5\sales_train_evaluation.csv`

Size: 121736518 bytes. Profiled rows: 30490. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| id | str | 0.0 | 30490 |
| item_id | str | 0.0 | 3049 |
| dept_id | str | 0.0 | 7 |
| cat_id | str | 0.0 | 3 |
| store_id | str | 0.0 | 10 |
| state_id | str | 0.0 | 3 |
| d_1 | int64 | 0.0 | 84 |
| d_2 | int64 | 0.0 | 82 |
| d_3 | int64 | 0.0 | 72 |
| d_4 | int64 | 0.0 | 79 |
| d_5 | int64 | 0.0 | 63 |
| d_6 | int64 | 0.0 | 84 |
| d_7 | int64 | 0.0 | 85 |
| d_8 | int64 | 0.0 | 100 |
| d_9 | int64 | 0.0 | 91 |
| d_10 | int64 | 0.0 | 73 |
| d_11 | int64 | 0.0 | 68 |
| d_12 | int64 | 0.0 | 69 |
| d_13 | int64 | 0.0 | 65 |
| d_14 | int64 | 0.0 | 68 |
| d_15 | int64 | 0.0 | 81 |
| d_16 | int64 | 0.0 | 82 |
| d_17 | int64 | 0.0 | 61 |
| d_18 | int64 | 0.0 | 67 |
| d_19 | int64 | 0.0 | 60 |
| d_20 | int64 | 0.0 | 52 |
| d_21 | int64 | 0.0 | 62 |
| d_22 | int64 | 0.0 | 75 |
| d_23 | int64 | 0.0 | 64 |
| d_24 | int64 | 0.0 | 60 |
| d_25 | int64 | 0.0 | 58 |
| d_26 | int64 | 0.0 | 54 |
| d_27 | int64 | 0.0 | 53 |
| d_28 | int64 | 0.0 | 56 |
| d_29 | int64 | 0.0 | 65 |
| d_30 | int64 | 0.0 | 71 |
| d_31 | int64 | 0.0 | 54 |
| d_32 | int64 | 0.0 | 60 |
| d_33 | int64 | 0.0 | 55 |
| d_34 | int64 | 0.0 | 61 |
| d_35 | int64 | 0.0 | 62 |
| d_36 | int64 | 0.0 | 73 |
| d_37 | int64 | 0.0 | 80 |
| d_38 | int64 | 0.0 | 60 |
| d_39 | int64 | 0.0 | 58 |
| d_40 | int64 | 0.0 | 58 |
| d_41 | int64 | 0.0 | 59 |
| d_42 | int64 | 0.0 | 63 |
| d_43 | int64 | 0.0 | 74 |
| d_44 | int64 | 0.0 | 71 |
| d_45 | int64 | 0.0 | 62 |
| d_46 | int64 | 0.0 | 65 |
| d_47 | int64 | 0.0 | 56 |
| d_48 | int64 | 0.0 | 61 |
| d_49 | int64 | 0.0 | 58 |
| d_50 | int64 | 0.0 | 71 |
| d_51 | int64 | 0.0 | 70 |
| d_52 | int64 | 0.0 | 59 |
| d_53 | int64 | 0.0 | 56 |
| d_54 | int64 | 0.0 | 55 |
| d_55 | int64 | 0.0 | 54 |
| d_56 | int64 | 0.0 | 60 |
| d_57 | int64 | 0.0 | 70 |
| d_58 | int64 | 0.0 | 64 |
| d_59 | int64 | 0.0 | 56 |
| d_60 | int64 | 0.0 | 49 |
| d_61 | int64 | 0.0 | 51 |
| d_62 | int64 | 0.0 | 60 |
| d_63 | int64 | 0.0 | 69 |
| d_64 | int64 | 0.0 | 72 |
| d_65 | int64 | 0.0 | 75 |
| d_66 | int64 | 0.0 | 66 |
| d_67 | int64 | 0.0 | 65 |
| d_68 | int64 | 0.0 | 62 |
| d_69 | int64 | 0.0 | 57 |
| d_70 | int64 | 0.0 | 58 |
| d_71 | int64 | 0.0 | 71 |
| d_72 | int64 | 0.0 | 74 |
| d_73 | int64 | 0.0 | 64 |
| d_74 | int64 | 0.0 | 61 |
| d_75 | int64 | 0.0 | 59 |
| d_76 | int64 | 0.0 | 58 |
| d_77 | int64 | 0.0 | 65 |
| d_78 | int64 | 0.0 | 69 |
| d_79 | int64 | 0.0 | 75 |
| d_80 | int64 | 0.0 | 62 |
| d_81 | int64 | 0.0 | 58 |
| d_82 | int64 | 0.0 | 56 |
| d_83 | int64 | 0.0 | 57 |
| d_84 | int64 | 0.0 | 68 |
| d_85 | int64 | 0.0 | 73 |
| d_86 | int64 | 0.0 | 69 |
| d_87 | int64 | 0.0 | 51 |
| d_88 | int64 | 0.0 | 52 |
| d_89 | int64 | 0.0 | 52 |
| d_90 | int64 | 0.0 | 48 |
| d_91 | int64 | 0.0 | 59 |
| d_92 | int64 | 0.0 | 70 |
| d_93 | int64 | 0.0 | 77 |
| d_94 | int64 | 0.0 | 60 |
| d_95 | int64 | 0.0 | 61 |
| d_96 | int64 | 0.0 | 53 |
| d_97 | int64 | 0.0 | 57 |
| d_98 | int64 | 0.0 | 64 |
| d_99 | int64 | 0.0 | 73 |
| d_100 | int64 | 0.0 | 67 |
| d_101 | int64 | 0.0 | 67 |
| d_102 | int64 | 0.0 | 63 |
| d_103 | int64 | 0.0 | 62 |
| d_104 | int64 | 0.0 | 63 |
| d_105 | int64 | 0.0 | 64 |
| d_106 | int64 | 0.0 | 67 |
| d_107 | int64 | 0.0 | 75 |
| d_108 | int64 | 0.0 | 59 |
| d_109 | int64 | 0.0 | 50 |
| d_110 | int64 | 0.0 | 47 |
| d_111 | int64 | 0.0 | 51 |
| d_112 | int64 | 0.0 | 60 |
| d_113 | int64 | 0.0 | 66 |
| d_114 | int64 | 0.0 | 65 |
| d_115 | int64 | 0.0 | 58 |
| d_116 | int64 | 0.0 | 55 |
| d_117 | int64 | 0.0 | 54 |
| d_118 | int64 | 0.0 | 57 |
| d_119 | int64 | 0.0 | 60 |
| d_120 | int64 | 0.0 | 63 |
| d_121 | int64 | 0.0 | 64 |
| d_122 | int64 | 0.0 | 62 |
| d_123 | int64 | 0.0 | 56 |
| d_124 | int64 | 0.0 | 64 |
| d_125 | int64 | 0.0 | 57 |
| d_126 | int64 | 0.0 | 66 |
| d_127 | int64 | 0.0 | 76 |
| d_128 | int64 | 0.0 | 79 |
| d_129 | int64 | 0.0 | 69 |
| d_130 | int64 | 0.0 | 66 |
| d_131 | int64 | 0.0 | 64 |
| d_132 | int64 | 0.0 | 65 |
| d_133 | int64 | 0.0 | 67 |
| d_134 | int64 | 0.0 | 73 |
| d_135 | int64 | 0.0 | 80 |
| d_136 | int64 | 0.0 | 67 |
| d_137 | int64 | 0.0 | 67 |
| d_138 | int64 | 0.0 | 65 |
| d_139 | int64 | 0.0 | 58 |
| d_140 | int64 | 0.0 | 65 |
| d_141 | int64 | 0.0 | 77 |
| d_142 | int64 | 0.0 | 69 |
| d_143 | int64 | 0.0 | 66 |
| d_144 | int64 | 0.0 | 68 |
| d_145 | int64 | 0.0 | 55 |
| d_146 | int64 | 0.0 | 61 |
| d_147 | int64 | 0.0 | 66 |
| d_148 | int64 | 0.0 | 65 |
| d_149 | int64 | 0.0 | 68 |
| d_150 | int64 | 0.0 | 61 |
| d_151 | int64 | 0.0 | 57 |
| d_152 | int64 | 0.0 | 58 |
| d_153 | int64 | 0.0 | 59 |
| d_154 | int64 | 0.0 | 78 |
| d_155 | int64 | 0.0 | 85 |
| d_156 | int64 | 0.0 | 80 |
| d_157 | int64 | 0.0 | 69 |
| d_158 | int64 | 0.0 | 69 |
| d_159 | int64 | 0.0 | 65 |
| d_160 | int64 | 0.0 | 65 |
| d_161 | int64 | 0.0 | 67 |
| d_162 | int64 | 0.0 | 76 |
| d_163 | int64 | 0.0 | 74 |
| d_164 | int64 | 0.0 | 68 |
| d_165 | int64 | 0.0 | 63 |
| d_166 | int64 | 0.0 | 57 |
| d_167 | int64 | 0.0 | 63 |
| d_168 | int64 | 0.0 | 66 |
| d_169 | int64 | 0.0 | 73 |
| d_170 | int64 | 0.0 | 74 |
| d_171 | int64 | 0.0 | 66 |
| d_172 | int64 | 0.0 | 57 |
| d_173 | int64 | 0.0 | 60 |
| d_174 | int64 | 0.0 | 61 |
| d_175 | int64 | 0.0 | 67 |
| d_176 | int64 | 0.0 | 75 |
| d_177 | int64 | 0.0 | 72 |
| d_178 | int64 | 0.0 | 58 |
| d_179 | int64 | 0.0 | 54 |
| d_180 | int64 | 0.0 | 55 |
| d_181 | int64 | 0.0 | 52 |
| d_182 | int64 | 0.0 | 61 |
| d_183 | int64 | 0.0 | 66 |
| d_184 | int64 | 0.0 | 69 |
| d_185 | int64 | 0.0 | 65 |
| d_186 | int64 | 0.0 | 67 |
| d_187 | int64 | 0.0 | 74 |
| d_188 | int64 | 0.0 | 63 |
| d_189 | int64 | 0.0 | 73 |
| d_190 | int64 | 0.0 | 78 |
| d_191 | int64 | 0.0 | 78 |
| d_192 | int64 | 0.0 | 72 |
| d_193 | int64 | 0.0 | 67 |
| d_194 | int64 | 0.0 | 69 |
| d_195 | int64 | 0.0 | 63 |
| d_196 | int64 | 0.0 | 72 |
| d_197 | int64 | 0.0 | 77 |
| d_198 | int64 | 0.0 | 85 |
| d_199 | int64 | 0.0 | 78 |
| d_200 | int64 | 0.0 | 69 |
| d_201 | int64 | 0.0 | 59 |
| d_202 | int64 | 0.0 | 58 |
| d_203 | int64 | 0.0 | 71 |
| d_204 | int64 | 0.0 | 80 |
| d_205 | int64 | 0.0 | 78 |
| d_206 | int64 | 0.0 | 63 |
| d_207 | int64 | 0.0 | 58 |
| d_208 | int64 | 0.0 | 59 |
| d_209 | int64 | 0.0 | 51 |
| d_210 | int64 | 0.0 | 61 |
| d_211 | int64 | 0.0 | 69 |
| d_212 | int64 | 0.0 | 73 |
| d_213 | int64 | 0.0 | 54 |
| d_214 | int64 | 0.0 | 56 |
| d_215 | int64 | 0.0 | 60 |
| d_216 | int64 | 0.0 | 66 |
| d_217 | int64 | 0.0 | 73 |
| d_218 | int64 | 0.0 | 80 |
| d_219 | int64 | 0.0 | 64 |
| d_220 | int64 | 0.0 | 71 |
| d_221 | int64 | 0.0 | 66 |
| d_222 | int64 | 0.0 | 59 |
| d_223 | int64 | 0.0 | 59 |
| d_224 | int64 | 0.0 | 69 |
| d_225 | int64 | 0.0 | 75 |
| d_226 | int64 | 0.0 | 77 |
| d_227 | int64 | 0.0 | 65 |
| d_228 | int64 | 0.0 | 62 |
| d_229 | int64 | 0.0 | 60 |
| d_230 | int64 | 0.0 | 63 |
| d_231 | int64 | 0.0 | 61 |
| d_232 | int64 | 0.0 | 68 |
| d_233 | int64 | 0.0 | 66 |
| d_234 | int64 | 0.0 | 59 |
| d_235 | int64 | 0.0 | 56 |
| d_236 | int64 | 0.0 | 61 |
| d_237 | int64 | 0.0 | 53 |
| d_238 | int64 | 0.0 | 64 |
| d_239 | int64 | 0.0 | 75 |
| d_240 | int64 | 0.0 | 81 |
| d_241 | int64 | 0.0 | 63 |
| d_242 | int64 | 0.0 | 62 |
| d_243 | int64 | 0.0 | 59 |
| d_244 | int64 | 0.0 | 61 |
| d_245 | int64 | 0.0 | 73 |
| d_246 | int64 | 0.0 | 85 |
| d_247 | int64 | 0.0 | 81 |
| d_248 | int64 | 0.0 | 76 |
| d_249 | int64 | 0.0 | 71 |
| d_250 | int64 | 0.0 | 71 |
| d_251 | int64 | 0.0 | 68 |
| d_252 | int64 | 0.0 | 74 |
| d_253 | int64 | 0.0 | 84 |
| d_254 | int64 | 0.0 | 82 |
| d_255 | int64 | 0.0 | 69 |
| d_256 | int64 | 0.0 | 70 |
| d_257 | int64 | 0.0 | 68 |
| d_258 | int64 | 0.0 | 67 |
| d_259 | int64 | 0.0 | 72 |
| d_260 | int64 | 0.0 | 82 |
| d_261 | int64 | 0.0 | 79 |
| d_262 | int64 | 0.0 | 64 |
| d_263 | int64 | 0.0 | 62 |
| d_264 | int64 | 0.0 | 58 |
| d_265 | int64 | 0.0 | 62 |
| d_266 | int64 | 0.0 | 71 |
| d_267 | int64 | 0.0 | 74 |
| d_268 | int64 | 0.0 | 72 |
| d_269 | int64 | 0.0 | 60 |
| d_270 | int64 | 0.0 | 60 |
| d_271 | int64 | 0.0 | 59 |
| d_272 | int64 | 0.0 | 62 |
| d_273 | int64 | 0.0 | 72 |
| d_274 | int64 | 0.0 | 76 |
| d_275 | int64 | 0.0 | 75 |
| d_276 | int64 | 0.0 | 59 |
| d_277 | int64 | 0.0 | 67 |
| d_278 | int64 | 0.0 | 64 |
| d_279 | int64 | 0.0 | 69 |
| d_280 | int64 | 0.0 | 70 |
| d_281 | int64 | 0.0 | 86 |
| d_282 | int64 | 0.0 | 86 |
| d_283 | int64 | 0.0 | 68 |
| d_284 | int64 | 0.0 | 69 |
| d_285 | int64 | 0.0 | 68 |
| d_286 | int64 | 0.0 | 68 |
| d_287 | int64 | 0.0 | 72 |
| d_288 | int64 | 0.0 | 83 |
| d_289 | int64 | 0.0 | 77 |
| d_290 | int64 | 0.0 | 66 |
| d_291 | int64 | 0.0 | 64 |
| d_292 | int64 | 0.0 | 59 |
| d_293 | int64 | 0.0 | 59 |
| d_294 | int64 | 0.0 | 69 |
| d_295 | int64 | 0.0 | 82 |
| d_296 | int64 | 0.0 | 76 |
| d_297 | int64 | 0.0 | 67 |
| d_298 | int64 | 0.0 | 73 |
| d_299 | int64 | 0.0 | 88 |
| d_300 | int64 | 0.0 | 78 |
| d_301 | int64 | 0.0 | 81 |
| d_302 | int64 | 0.0 | 66 |
| d_303 | int64 | 0.0 | 65 |
| d_304 | int64 | 0.0 | 57 |
| d_305 | int64 | 0.0 | 56 |
| d_306 | int64 | 0.0 | 53 |
| d_307 | int64 | 0.0 | 64 |
| d_308 | int64 | 0.0 | 76 |
| d_309 | int64 | 0.0 | 85 |
| d_310 | int64 | 0.0 | 80 |
| d_311 | int64 | 0.0 | 68 |
| d_312 | int64 | 0.0 | 68 |
| d_313 | int64 | 0.0 | 64 |
| d_314 | int64 | 0.0 | 67 |
| d_315 | int64 | 0.0 | 70 |
| d_316 | int64 | 0.0 | 75 |
| d_317 | int64 | 0.0 | 81 |
| d_318 | int64 | 0.0 | 70 |
| d_319 | int64 | 0.0 | 63 |
| d_320 | int64 | 0.0 | 71 |
| d_321 | int64 | 0.0 | 72 |
| d_322 | int64 | 0.0 | 73 |
| d_323 | int64 | 0.0 | 83 |
| d_324 | int64 | 0.0 | 74 |
| d_325 | int64 | 0.0 | 68 |
| d_326 | int64 | 0.0 | 65 |
| d_327 | int64 | 0.0 | 68 |
| d_328 | int64 | 0.0 | 70 |
| d_329 | int64 | 0.0 | 86 |
| d_330 | int64 | 0.0 | 84 |
| d_331 | int64 | 0.0 | 3 |
| d_332 | int64 | 0.0 | 66 |
| d_333 | int64 | 0.0 | 60 |
| d_334 | int64 | 0.0 | 59 |
| d_335 | int64 | 0.0 | 59 |
| d_336 | int64 | 0.0 | 77 |
| d_337 | int64 | 0.0 | 84 |
| d_338 | int64 | 0.0 | 58 |
| d_339 | int64 | 0.0 | 72 |
| d_340 | int64 | 0.0 | 68 |
| d_341 | int64 | 0.0 | 65 |
| d_342 | int64 | 0.0 | 70 |
| d_343 | int64 | 0.0 | 70 |
| d_344 | int64 | 0.0 | 81 |
| d_345 | int64 | 0.0 | 77 |
| d_346 | int64 | 0.0 | 68 |
| d_347 | int64 | 0.0 | 67 |
| d_348 | int64 | 0.0 | 68 |
| d_349 | int64 | 0.0 | 57 |
| d_350 | int64 | 0.0 | 69 |
| d_351 | int64 | 0.0 | 83 |
| d_352 | int64 | 0.0 | 80 |
| d_353 | int64 | 0.0 | 65 |
| d_354 | int64 | 0.0 | 56 |
| d_355 | int64 | 0.0 | 59 |
| d_356 | int64 | 0.0 | 56 |
| d_357 | int64 | 0.0 | 66 |
| d_358 | int64 | 0.0 | 78 |
| d_359 | int64 | 0.0 | 71 |
| d_360 | int64 | 0.0 | 57 |
| d_361 | int64 | 0.0 | 52 |
| d_362 | int64 | 0.0 | 55 |
| d_363 | int64 | 0.0 | 54 |
| d_364 | int64 | 0.0 | 67 |
| d_365 | int64 | 0.0 | 73 |
| d_366 | int64 | 0.0 | 73 |
| d_367 | int64 | 0.0 | 54 |
| d_368 | int64 | 0.0 | 59 |
| d_369 | int64 | 0.0 | 68 |
| d_370 | int64 | 0.0 | 68 |
| d_371 | int64 | 0.0 | 79 |
| d_372 | int64 | 0.0 | 85 |
| d_373 | int64 | 0.0 | 83 |
| d_374 | int64 | 0.0 | 70 |
| d_375 | int64 | 0.0 | 65 |
| d_376 | int64 | 0.0 | 67 |
| d_377 | int64 | 0.0 | 75 |
| d_378 | int64 | 0.0 | 70 |
| d_379 | int64 | 0.0 | 88 |
| d_380 | int64 | 0.0 | 90 |
| d_381 | int64 | 0.0 | 71 |
| d_382 | int64 | 0.0 | 63 |
| d_383 | int64 | 0.0 | 64 |
| d_384 | int64 | 0.0 | 54 |
| d_385 | int64 | 0.0 | 61 |
| d_386 | int64 | 0.0 | 78 |
| d_387 | int64 | 0.0 | 81 |
| d_388 | int64 | 0.0 | 66 |
| d_389 | int64 | 0.0 | 64 |
| d_390 | int64 | 0.0 | 56 |
| d_391 | int64 | 0.0 | 61 |
| d_392 | int64 | 0.0 | 72 |
| d_393 | int64 | 0.0 | 80 |
| d_394 | int64 | 0.0 | 83 |
| d_395 | int64 | 0.0 | 70 |
| d_396 | int64 | 0.0 | 59 |
| d_397 | int64 | 0.0 | 60 |
| d_398 | int64 | 0.0 | 69 |
| d_399 | int64 | 0.0 | 73 |
| d_400 | int64 | 0.0 | 88 |
| d_401 | int64 | 0.0 | 86 |
| d_402 | int64 | 0.0 | 76 |
| d_403 | int64 | 0.0 | 77 |
| d_404 | int64 | 0.0 | 69 |
| d_405 | int64 | 0.0 | 69 |
| d_406 | int64 | 0.0 | 73 |
| d_407 | int64 | 0.0 | 78 |
| d_408 | int64 | 0.0 | 90 |
| d_409 | int64 | 0.0 | 71 |
| d_410 | int64 | 0.0 | 69 |
| d_411 | int64 | 0.0 | 68 |
| d_412 | int64 | 0.0 | 72 |
| d_413 | int64 | 0.0 | 72 |
| d_414 | int64 | 0.0 | 81 |
| d_415 | int64 | 0.0 | 80 |
| d_416 | int64 | 0.0 | 65 |
| d_417 | int64 | 0.0 | 64 |
| d_418 | int64 | 0.0 | 61 |
| d_419 | int64 | 0.0 | 62 |
| d_420 | int64 | 0.0 | 68 |
| d_421 | int64 | 0.0 | 80 |
| d_422 | int64 | 0.0 | 85 |
| d_423 | int64 | 0.0 | 64 |
| d_424 | int64 | 0.0 | 59 |
| d_425 | int64 | 0.0 | 56 |
| d_426 | int64 | 0.0 | 48 |
| d_427 | int64 | 0.0 | 71 |
| d_428 | int64 | 0.0 | 77 |
| d_429 | int64 | 0.0 | 82 |
| d_430 | int64 | 0.0 | 74 |
| d_431 | int64 | 0.0 | 75 |
| d_432 | int64 | 0.0 | 68 |
| d_433 | int64 | 0.0 | 74 |
| d_434 | int64 | 0.0 | 84 |
| d_435 | int64 | 0.0 | 100 |
| d_436 | int64 | 0.0 | 91 |
| d_437 | int64 | 0.0 | 73 |
| d_438 | int64 | 0.0 | 66 |
| d_439 | int64 | 0.0 | 68 |
| d_440 | int64 | 0.0 | 65 |
| d_441 | int64 | 0.0 | 72 |
| d_442 | int64 | 0.0 | 84 |
| d_443 | int64 | 0.0 | 85 |
| d_444 | int64 | 0.0 | 62 |
| d_445 | int64 | 0.0 | 62 |
| d_446 | int64 | 0.0 | 60 |
| d_447 | int64 | 0.0 | 61 |
| d_448 | int64 | 0.0 | 66 |
| d_449 | int64 | 0.0 | 85 |
| d_450 | int64 | 0.0 | 83 |
| d_451 | int64 | 0.0 | 65 |
| d_452 | int64 | 0.0 | 61 |
| d_453 | int64 | 0.0 | 58 |
| d_454 | int64 | 0.0 | 62 |
| d_455 | int64 | 0.0 | 64 |
| d_456 | int64 | 0.0 | 76 |
| d_457 | int64 | 0.0 | 77 |
| d_458 | int64 | 0.0 | 64 |
| d_459 | int64 | 0.0 | 66 |
| d_460 | int64 | 0.0 | 69 |
| d_461 | int64 | 0.0 | 76 |
| d_462 | int64 | 0.0 | 74 |
| d_463 | int64 | 0.0 | 87 |
| d_464 | int64 | 0.0 | 87 |
| d_465 | int64 | 0.0 | 78 |
| d_466 | int64 | 0.0 | 71 |
| d_467 | int64 | 0.0 | 68 |
| d_468 | int64 | 0.0 | 73 |
| d_469 | int64 | 0.0 | 79 |
| d_470 | int64 | 0.0 | 93 |
| d_471 | int64 | 0.0 | 83 |
| d_472 | int64 | 0.0 | 76 |
| d_473 | int64 | 0.0 | 76 |
| d_474 | int64 | 0.0 | 71 |
| d_475 | int64 | 0.0 | 64 |
| d_476 | int64 | 0.0 | 81 |
| d_477 | int64 | 0.0 | 86 |
| d_478 | int64 | 0.0 | 86 |
| d_479 | int64 | 0.0 | 62 |
| d_480 | int64 | 0.0 | 68 |
| d_481 | int64 | 0.0 | 62 |
| d_482 | int64 | 0.0 | 66 |
| d_483 | int64 | 0.0 | 80 |
| d_484 | int64 | 0.0 | 83 |
| d_485 | int64 | 0.0 | 82 |
| d_486 | int64 | 0.0 | 80 |
| d_487 | int64 | 0.0 | 69 |
| d_488 | int64 | 0.0 | 63 |
| d_489 | int64 | 0.0 | 66 |
| d_490 | int64 | 0.0 | 80 |
| d_491 | int64 | 0.0 | 92 |
| d_492 | int64 | 0.0 | 90 |
| d_493 | int64 | 0.0 | 75 |
| d_494 | int64 | 0.0 | 72 |
| d_495 | int64 | 0.0 | 79 |
| d_496 | int64 | 0.0 | 71 |
| d_497 | int64 | 0.0 | 79 |
| d_498 | int64 | 0.0 | 91 |
| d_499 | int64 | 0.0 | 98 |
| d_500 | int64 | 0.0 | 85 |
| d_501 | int64 | 0.0 | 77 |
| d_502 | int64 | 0.0 | 67 |
| d_503 | int64 | 0.0 | 75 |
| d_504 | int64 | 0.0 | 93 |
| d_505 | int64 | 0.0 | 94 |
| d_506 | int64 | 0.0 | 94 |
| d_507 | int64 | 0.0 | 73 |
| d_508 | int64 | 0.0 | 71 |
| d_509 | int64 | 0.0 | 68 |
| d_510 | int64 | 0.0 | 69 |
| d_511 | int64 | 0.0 | 85 |
| d_512 | int64 | 0.0 | 86 |
| d_513 | int64 | 0.0 | 90 |
| d_514 | int64 | 0.0 | 73 |
| d_515 | int64 | 0.0 | 70 |
| d_516 | int64 | 0.0 | 67 |
| d_517 | int64 | 0.0 | 70 |
| d_518 | int64 | 0.0 | 83 |
| d_519 | int64 | 0.0 | 88 |
| d_520 | int64 | 0.0 | 81 |
| d_521 | int64 | 0.0 | 80 |
| d_522 | int64 | 0.0 | 91 |
| d_523 | int64 | 0.0 | 77 |
| d_524 | int64 | 0.0 | 78 |
| d_525 | int64 | 0.0 | 91 |
| d_526 | int64 | 0.0 | 91 |
| d_527 | int64 | 0.0 | 87 |
| d_528 | int64 | 0.0 | 75 |
| d_529 | int64 | 0.0 | 68 |
| d_530 | int64 | 0.0 | 77 |
| d_531 | int64 | 0.0 | 73 |
| d_532 | int64 | 0.0 | 76 |
| d_533 | int64 | 0.0 | 88 |
| d_534 | int64 | 0.0 | 92 |
| d_535 | int64 | 0.0 | 76 |
| d_536 | int64 | 0.0 | 74 |
| d_537 | int64 | 0.0 | 67 |
| d_538 | int64 | 0.0 | 66 |
| d_539 | int64 | 0.0 | 73 |
| d_540 | int64 | 0.0 | 86 |
| d_541 | int64 | 0.0 | 85 |
| d_542 | int64 | 0.0 | 70 |
| d_543 | int64 | 0.0 | 66 |
| d_544 | int64 | 0.0 | 67 |
| d_545 | int64 | 0.0 | 66 |
| d_546 | int64 | 0.0 | 72 |
| d_547 | int64 | 0.0 | 77 |
| d_548 | int64 | 0.0 | 76 |
| d_549 | int64 | 0.0 | 65 |
| d_550 | int64 | 0.0 | 68 |
| d_551 | int64 | 0.0 | 75 |
| d_552 | int64 | 0.0 | 81 |
| d_553 | int64 | 0.0 | 87 |
| d_554 | int64 | 0.0 | 84 |
| d_555 | int64 | 0.0 | 90 |
| d_556 | int64 | 0.0 | 83 |
| d_557 | int64 | 0.0 | 74 |
| d_558 | int64 | 0.0 | 78 |
| d_559 | int64 | 0.0 | 80 |
| d_560 | int64 | 0.0 | 84 |
| d_561 | int64 | 0.0 | 95 |
| d_562 | int64 | 0.0 | 94 |
| d_563 | int64 | 0.0 | 80 |
| d_564 | int64 | 0.0 | 76 |
| d_565 | int64 | 0.0 | 76 |
| d_566 | int64 | 0.0 | 75 |
| d_567 | int64 | 0.0 | 77 |
| d_568 | int64 | 0.0 | 81 |
| d_569 | int64 | 0.0 | 86 |
| d_570 | int64 | 0.0 | 69 |
| d_571 | int64 | 0.0 | 67 |
| d_572 | int64 | 0.0 | 59 |
| d_573 | int64 | 0.0 | 59 |
| d_574 | int64 | 0.0 | 72 |
| d_575 | int64 | 0.0 | 82 |
| d_576 | int64 | 0.0 | 82 |
| d_577 | int64 | 0.0 | 69 |
| d_578 | int64 | 0.0 | 69 |
| d_579 | int64 | 0.0 | 63 |
| d_580 | int64 | 0.0 | 68 |
| d_581 | int64 | 0.0 | 78 |
| d_582 | int64 | 0.0 | 84 |
| d_583 | int64 | 0.0 | 93 |
| d_584 | int64 | 0.0 | 93 |
| d_585 | int64 | 0.0 | 75 |
| d_586 | int64 | 0.0 | 70 |
| d_587 | int64 | 0.0 | 73 |
| d_588 | int64 | 0.0 | 73 |
| d_589 | int64 | 0.0 | 83 |
| d_590 | int64 | 0.0 | 88 |
| d_591 | int64 | 0.0 | 72 |
| d_592 | int64 | 0.0 | 69 |
| d_593 | int64 | 0.0 | 72 |
| d_594 | int64 | 0.0 | 67 |
| d_595 | int64 | 0.0 | 80 |
| d_596 | int64 | 0.0 | 91 |
| d_597 | int64 | 0.0 | 81 |
| d_598 | int64 | 0.0 | 61 |
| d_599 | int64 | 0.0 | 59 |
| d_600 | int64 | 0.0 | 56 |
| d_601 | int64 | 0.0 | 62 |
| d_602 | int64 | 0.0 | 67 |
| d_603 | int64 | 0.0 | 83 |
| d_604 | int64 | 0.0 | 80 |
| d_605 | int64 | 0.0 | 63 |
| d_606 | int64 | 0.0 | 62 |
| d_607 | int64 | 0.0 | 60 |
| d_608 | int64 | 0.0 | 55 |
| d_609 | int64 | 0.0 | 68 |
| d_610 | int64 | 0.0 | 83 |
| d_611 | int64 | 0.0 | 84 |
| d_612 | int64 | 0.0 | 73 |
| d_613 | int64 | 0.0 | 79 |
| d_614 | int64 | 0.0 | 70 |
| d_615 | int64 | 0.0 | 66 |
| d_616 | int64 | 0.0 | 70 |
| d_617 | int64 | 0.0 | 84 |
| d_618 | int64 | 0.0 | 76 |
| d_619 | int64 | 0.0 | 75 |
| d_620 | int64 | 0.0 | 70 |
| d_621 | int64 | 0.0 | 67 |
| d_622 | int64 | 0.0 | 67 |
| d_623 | int64 | 0.0 | 73 |
| d_624 | int64 | 0.0 | 79 |
| d_625 | int64 | 0.0 | 86 |
| d_626 | int64 | 0.0 | 72 |
| d_627 | int64 | 0.0 | 60 |
| d_628 | int64 | 0.0 | 59 |
| d_629 | int64 | 0.0 | 61 |
| d_630 | int64 | 0.0 | 62 |
| d_631 | int64 | 0.0 | 69 |
| d_632 | int64 | 0.0 | 73 |
| d_633 | int64 | 0.0 | 58 |
| d_634 | int64 | 0.0 | 58 |
| d_635 | int64 | 0.0 | 61 |
| d_636 | int64 | 0.0 | 53 |
| d_637 | int64 | 0.0 | 63 |
| d_638 | int64 | 0.0 | 75 |
| d_639 | int64 | 0.0 | 73 |
| d_640 | int64 | 0.0 | 58 |
| d_641 | int64 | 0.0 | 59 |
| d_642 | int64 | 0.0 | 61 |
| d_643 | int64 | 0.0 | 68 |
| d_644 | int64 | 0.0 | 69 |
| d_645 | int64 | 0.0 | 86 |
| d_646 | int64 | 0.0 | 83 |
| d_647 | int64 | 0.0 | 67 |
| d_648 | int64 | 0.0 | 66 |
| d_649 | int64 | 0.0 | 61 |
| d_650 | int64 | 0.0 | 62 |
| d_651 | int64 | 0.0 | 68 |
| d_652 | int64 | 0.0 | 80 |
| d_653 | int64 | 0.0 | 80 |
| d_654 | int64 | 0.0 | 64 |
| d_655 | int64 | 0.0 | 59 |
| d_656 | int64 | 0.0 | 64 |
| d_657 | int64 | 0.0 | 63 |
| d_658 | int64 | 0.0 | 65 |
| d_659 | int64 | 0.0 | 78 |
| d_660 | int64 | 0.0 | 76 |
| d_661 | int64 | 0.0 | 60 |
| d_662 | int64 | 0.0 | 70 |
| d_663 | int64 | 0.0 | 84 |
| d_664 | int64 | 0.0 | 81 |
| d_665 | int64 | 0.0 | 71 |
| d_666 | int64 | 0.0 | 66 |
| d_667 | int64 | 0.0 | 62 |
| d_668 | int64 | 0.0 | 52 |
| d_669 | int64 | 0.0 | 50 |
| d_670 | int64 | 0.0 | 53 |
| d_671 | int64 | 0.0 | 53 |
| d_672 | int64 | 0.0 | 65 |
| d_673 | int64 | 0.0 | 77 |
| d_674 | int64 | 0.0 | 78 |
| d_675 | int64 | 0.0 | 72 |
| d_676 | int64 | 0.0 | 59 |
| d_677 | int64 | 0.0 | 68 |
| d_678 | int64 | 0.0 | 65 |
| d_679 | int64 | 0.0 | 65 |
| d_680 | int64 | 0.0 | 79 |
| d_681 | int64 | 0.0 | 77 |
| d_682 | int64 | 0.0 | 65 |
| d_683 | int64 | 0.0 | 64 |
| d_684 | int64 | 0.0 | 66 |
| d_685 | int64 | 0.0 | 63 |
| d_686 | int64 | 0.0 | 71 |
| d_687 | int64 | 0.0 | 83 |
| d_688 | int64 | 0.0 | 82 |
| d_689 | int64 | 0.0 | 63 |
| d_690 | int64 | 0.0 | 61 |
| d_691 | int64 | 0.0 | 70 |
| d_692 | int64 | 0.0 | 68 |
| d_693 | int64 | 0.0 | 75 |
| d_694 | int64 | 0.0 | 85 |
| d_695 | int64 | 0.0 | 87 |
| d_696 | int64 | 0.0 | 88 |
| d_697 | int64 | 0.0 | 2 |
| d_698 | int64 | 0.0 | 67 |
| d_699 | int64 | 0.0 | 62 |
| d_700 | int64 | 0.0 | 65 |
| d_701 | int64 | 0.0 | 72 |
| d_702 | int64 | 0.0 | 74 |
| d_703 | int64 | 0.0 | 82 |
| d_704 | int64 | 0.0 | 58 |
| d_705 | int64 | 0.0 | 68 |
| d_706 | int64 | 0.0 | 75 |
| d_707 | int64 | 0.0 | 66 |
| d_708 | int64 | 0.0 | 85 |
| d_709 | int64 | 0.0 | 82 |
| d_710 | int64 | 0.0 | 68 |
| d_711 | int64 | 0.0 | 69 |
| d_712 | int64 | 0.0 | 63 |
| d_713 | int64 | 0.0 | 64 |
| d_714 | int64 | 0.0 | 65 |
| d_715 | int64 | 0.0 | 91 |
| d_716 | int64 | 0.0 | 78 |
| d_717 | int64 | 0.0 | 66 |
| d_718 | int64 | 0.0 | 67 |
| d_719 | int64 | 0.0 | 57 |
| d_720 | int64 | 0.0 | 56 |
| d_721 | int64 | 0.0 | 63 |
| d_722 | int64 | 0.0 | 76 |
| d_723 | int64 | 0.0 | 71 |
| d_724 | int64 | 0.0 | 59 |
| d_725 | int64 | 0.0 | 56 |
| d_726 | int64 | 0.0 | 51 |
| d_727 | int64 | 0.0 | 52 |
| d_728 | int64 | 0.0 | 56 |
| d_729 | int64 | 0.0 | 72 |
| d_730 | int64 | 0.0 | 70 |
| d_731 | int64 | 0.0 | 54 |
| d_732 | int64 | 0.0 | 58 |
| d_733 | int64 | 0.0 | 49 |
| d_734 | int64 | 0.0 | 54 |
| d_735 | int64 | 0.0 | 68 |
| d_736 | int64 | 0.0 | 87 |
| d_737 | int64 | 0.0 | 82 |
| d_738 | int64 | 0.0 | 62 |
| d_739 | int64 | 0.0 | 64 |
| d_740 | int64 | 0.0 | 67 |
| d_741 | int64 | 0.0 | 64 |
| d_742 | int64 | 0.0 | 74 |
| d_743 | int64 | 0.0 | 83 |
| d_744 | int64 | 0.0 | 73 |
| d_745 | int64 | 0.0 | 74 |
| d_746 | int64 | 0.0 | 72 |
| d_747 | int64 | 0.0 | 85 |
| d_748 | int64 | 0.0 | 68 |
| d_749 | int64 | 0.0 | 74 |
| d_750 | int64 | 0.0 | 81 |
| d_751 | int64 | 0.0 | 83 |
| d_752 | int64 | 0.0 | 66 |
| d_753 | int64 | 0.0 | 62 |
| d_754 | int64 | 0.0 | 61 |
| d_755 | int64 | 0.0 | 67 |
| d_756 | int64 | 0.0 | 68 |
| d_757 | int64 | 0.0 | 79 |
| d_758 | int64 | 0.0 | 78 |
| d_759 | int64 | 0.0 | 60 |
| d_760 | int64 | 0.0 | 55 |
| d_761 | int64 | 0.0 | 59 |
| d_762 | int64 | 0.0 | 59 |
| d_763 | int64 | 0.0 | 74 |
| d_764 | int64 | 0.0 | 87 |
| d_765 | int64 | 0.0 | 92 |
| d_766 | int64 | 0.0 | 72 |
| d_767 | int64 | 0.0 | 67 |
| d_768 | int64 | 0.0 | 65 |
| d_769 | int64 | 0.0 | 64 |
| d_770 | int64 | 0.0 | 68 |
| d_771 | int64 | 0.0 | 89 |
| d_772 | int64 | 0.0 | 80 |
| d_773 | int64 | 0.0 | 68 |
| d_774 | int64 | 0.0 | 67 |
| d_775 | int64 | 0.0 | 62 |
| d_776 | int64 | 0.0 | 67 |
| d_777 | int64 | 0.0 | 74 |
| d_778 | int64 | 0.0 | 81 |
| d_779 | int64 | 0.0 | 77 |
| d_780 | int64 | 0.0 | 64 |
| d_781 | int64 | 0.0 | 59 |
| d_782 | int64 | 0.0 | 58 |
| d_783 | int64 | 0.0 | 58 |
| d_784 | int64 | 0.0 | 65 |
| d_785 | int64 | 0.0 | 74 |
| d_786 | int64 | 0.0 | 73 |
| d_787 | int64 | 0.0 | 59 |
| d_788 | int64 | 0.0 | 63 |
| d_789 | int64 | 0.0 | 60 |
| d_790 | int64 | 0.0 | 63 |
| d_791 | int64 | 0.0 | 73 |
| d_792 | int64 | 0.0 | 91 |
| d_793 | int64 | 0.0 | 72 |
| d_794 | int64 | 0.0 | 69 |
| d_795 | int64 | 0.0 | 68 |
| d_796 | int64 | 0.0 | 70 |
| d_797 | int64 | 0.0 | 63 |
| d_798 | int64 | 0.0 | 69 |
| d_799 | int64 | 0.0 | 79 |
| d_800 | int64 | 0.0 | 84 |
| d_801 | int64 | 0.0 | 66 |
| d_802 | int64 | 0.0 | 69 |
| d_803 | int64 | 0.0 | 63 |
| d_804 | int64 | 0.0 | 66 |
| d_805 | int64 | 0.0 | 72 |
| d_806 | int64 | 0.0 | 78 |
| d_807 | int64 | 0.0 | 80 |
| d_808 | int64 | 0.0 | 69 |
| d_809 | int64 | 0.0 | 64 |
| d_810 | int64 | 0.0 | 56 |
| d_811 | int64 | 0.0 | 54 |
| d_812 | int64 | 0.0 | 64 |
| d_813 | int64 | 0.0 | 70 |
| d_814 | int64 | 0.0 | 74 |
| d_815 | int64 | 0.0 | 62 |
| d_816 | int64 | 0.0 | 61 |
| d_817 | int64 | 0.0 | 57 |
| d_818 | int64 | 0.0 | 58 |
| d_819 | int64 | 0.0 | 60 |
| d_820 | int64 | 0.0 | 62 |
| d_821 | int64 | 0.0 | 73 |
| d_822 | int64 | 0.0 | 55 |
| d_823 | int64 | 0.0 | 60 |
| d_824 | int64 | 0.0 | 65 |
| d_825 | int64 | 0.0 | 66 |
| d_826 | int64 | 0.0 | 72 |
| d_827 | int64 | 0.0 | 80 |
| d_828 | int64 | 0.0 | 72 |
| d_829 | int64 | 0.0 | 67 |
| d_830 | int64 | 0.0 | 64 |
| d_831 | int64 | 0.0 | 64 |
| d_832 | int64 | 0.0 | 65 |
| d_833 | int64 | 0.0 | 62 |
| d_834 | int64 | 0.0 | 85 |
| d_835 | int64 | 0.0 | 78 |
| d_836 | int64 | 0.0 | 71 |
| d_837 | int64 | 0.0 | 64 |
| d_838 | int64 | 0.0 | 68 |
| d_839 | int64 | 0.0 | 58 |
| d_840 | int64 | 0.0 | 63 |
| d_841 | int64 | 0.0 | 75 |
| d_842 | int64 | 0.0 | 83 |
| d_843 | int64 | 0.0 | 68 |
| d_844 | int64 | 0.0 | 61 |
| d_845 | int64 | 0.0 | 56 |
| d_846 | int64 | 0.0 | 59 |
| d_847 | int64 | 0.0 | 63 |
| d_848 | int64 | 0.0 | 78 |
| d_849 | int64 | 0.0 | 72 |
| d_850 | int64 | 0.0 | 72 |
| d_851 | int64 | 0.0 | 61 |
| d_852 | int64 | 0.0 | 54 |
| d_853 | int64 | 0.0 | 59 |
| d_854 | int64 | 0.0 | 68 |
| d_855 | int64 | 0.0 | 78 |
| d_856 | int64 | 0.0 | 87 |
| d_857 | int64 | 0.0 | 72 |
| d_858 | int64 | 0.0 | 66 |
| d_859 | int64 | 0.0 | 71 |
| d_860 | int64 | 0.0 | 65 |
| d_861 | int64 | 0.0 | 68 |
| d_862 | int64 | 0.0 | 81 |
| d_863 | int64 | 0.0 | 83 |
| d_864 | int64 | 0.0 | 71 |
| d_865 | int64 | 0.0 | 67 |
| d_866 | int64 | 0.0 | 66 |
| d_867 | int64 | 0.0 | 69 |
| d_868 | int64 | 0.0 | 75 |
| d_869 | int64 | 0.0 | 83 |
| d_870 | int64 | 0.0 | 81 |
| d_871 | int64 | 0.0 | 69 |
| d_872 | int64 | 0.0 | 63 |
| d_873 | int64 | 0.0 | 61 |
| d_874 | int64 | 0.0 | 63 |
| d_875 | int64 | 0.0 | 69 |
| d_876 | int64 | 0.0 | 79 |
| d_877 | int64 | 0.0 | 81 |
| d_878 | int64 | 0.0 | 64 |
| d_879 | int64 | 0.0 | 65 |
| d_880 | int64 | 0.0 | 64 |
| d_881 | int64 | 0.0 | 68 |
| d_882 | int64 | 0.0 | 77 |
| d_883 | int64 | 0.0 | 91 |
| d_884 | int64 | 0.0 | 93 |
| d_885 | int64 | 0.0 | 75 |
| d_886 | int64 | 0.0 | 72 |
| d_887 | int64 | 0.0 | 82 |
| d_888 | int64 | 0.0 | 86 |
| d_889 | int64 | 0.0 | 77 |
| d_890 | int64 | 0.0 | 81 |
| d_891 | int64 | 0.0 | 79 |
| d_892 | int64 | 0.0 | 73 |
| d_893 | int64 | 0.0 | 78 |
| d_894 | int64 | 0.0 | 68 |
| d_895 | int64 | 0.0 | 69 |
| d_896 | int64 | 0.0 | 75 |
| d_897 | int64 | 0.0 | 80 |
| d_898 | int64 | 0.0 | 86 |
| d_899 | int64 | 0.0 | 70 |
| d_900 | int64 | 0.0 | 68 |
| d_901 | int64 | 0.0 | 67 |
| d_902 | int64 | 0.0 | 72 |
| d_903 | int64 | 0.0 | 71 |
| d_904 | int64 | 0.0 | 77 |
| d_905 | int64 | 0.0 | 80 |
| d_906 | int64 | 0.0 | 66 |
| d_907 | int64 | 0.0 | 66 |
| d_908 | int64 | 0.0 | 62 |
| d_909 | int64 | 0.0 | 65 |
| d_910 | int64 | 0.0 | 68 |
| d_911 | int64 | 0.0 | 80 |
| d_912 | int64 | 0.0 | 80 |
| d_913 | int64 | 0.0 | 68 |
| d_914 | int64 | 0.0 | 60 |
| d_915 | int64 | 0.0 | 64 |
| d_916 | int64 | 0.0 | 76 |
| d_917 | int64 | 0.0 | 80 |
| d_918 | int64 | 0.0 | 89 |
| d_919 | int64 | 0.0 | 87 |
| d_920 | int64 | 0.0 | 82 |
| d_921 | int64 | 0.0 | 78 |
| d_922 | int64 | 0.0 | 78 |
| d_923 | int64 | 0.0 | 77 |
| d_924 | int64 | 0.0 | 79 |
| d_925 | int64 | 0.0 | 82 |
| d_926 | int64 | 0.0 | 96 |
| d_927 | int64 | 0.0 | 82 |
| d_928 | int64 | 0.0 | 75 |
| d_929 | int64 | 0.0 | 76 |
| d_930 | int64 | 0.0 | 78 |
| d_931 | int64 | 0.0 | 78 |
| d_932 | int64 | 0.0 | 82 |
| d_933 | int64 | 0.0 | 90 |
| d_934 | int64 | 0.0 | 77 |
| d_935 | int64 | 0.0 | 70 |
| d_936 | int64 | 0.0 | 69 |
| d_937 | int64 | 0.0 | 69 |
| d_938 | int64 | 0.0 | 81 |
| d_939 | int64 | 0.0 | 94 |
| d_940 | int64 | 0.0 | 97 |
| d_941 | int64 | 0.0 | 73 |
| d_942 | int64 | 0.0 | 76 |
| d_943 | int64 | 0.0 | 70 |
| d_944 | int64 | 0.0 | 71 |
| d_945 | int64 | 0.0 | 89 |
| d_946 | int64 | 0.0 | 91 |
| d_947 | int64 | 0.0 | 97 |
| d_948 | int64 | 0.0 | 91 |
| d_949 | int64 | 0.0 | 81 |
| d_950 | int64 | 0.0 | 71 |
| d_951 | int64 | 0.0 | 73 |
| d_952 | int64 | 0.0 | 80 |
| d_953 | int64 | 0.0 | 85 |
| d_954 | int64 | 0.0 | 94 |
| d_955 | int64 | 0.0 | 81 |
| d_956 | int64 | 0.0 | 78 |
| d_957 | int64 | 0.0 | 70 |
| d_958 | int64 | 0.0 | 78 |
| d_959 | int64 | 0.0 | 78 |
| d_960 | int64 | 0.0 | 88 |
| d_961 | int64 | 0.0 | 89 |
| d_962 | int64 | 0.0 | 70 |
| d_963 | int64 | 0.0 | 68 |
| d_964 | int64 | 0.0 | 63 |
| d_965 | int64 | 0.0 | 68 |
| d_966 | int64 | 0.0 | 70 |
| d_967 | int64 | 0.0 | 79 |
| d_968 | int64 | 0.0 | 81 |
| d_969 | int64 | 0.0 | 65 |
| d_970 | int64 | 0.0 | 65 |
| d_971 | int64 | 0.0 | 60 |
| d_972 | int64 | 0.0 | 62 |
| d_973 | int64 | 0.0 | 70 |
| d_974 | int64 | 0.0 | 78 |
| d_975 | int64 | 0.0 | 75 |
| d_976 | int64 | 0.0 | 64 |
| d_977 | int64 | 0.0 | 69 |
| d_978 | int64 | 0.0 | 68 |
| d_979 | int64 | 0.0 | 70 |
| d_980 | int64 | 0.0 | 70 |
| d_981 | int64 | 0.0 | 85 |
| d_982 | int64 | 0.0 | 90 |
| d_983 | int64 | 0.0 | 70 |
| d_984 | int64 | 0.0 | 68 |
| d_985 | int64 | 0.0 | 67 |
| d_986 | int64 | 0.0 | 69 |
| d_987 | int64 | 0.0 | 72 |
| d_988 | int64 | 0.0 | 83 |
| d_989 | int64 | 0.0 | 83 |
| d_990 | int64 | 0.0 | 69 |
| d_991 | int64 | 0.0 | 66 |
| d_992 | int64 | 0.0 | 62 |
| d_993 | int64 | 0.0 | 60 |
| d_994 | int64 | 0.0 | 58 |
| d_995 | int64 | 0.0 | 77 |
| d_996 | int64 | 0.0 | 73 |
| d_997 | int64 | 0.0 | 54 |
| d_998 | int64 | 0.0 | 55 |
| d_999 | int64 | 0.0 | 55 |
| d_1000 | int64 | 0.0 | 53 |
| d_1001 | int64 | 0.0 | 64 |
| d_1002 | int64 | 0.0 | 78 |
| d_1003 | int64 | 0.0 | 75 |
| d_1004 | int64 | 0.0 | 58 |
| d_1005 | int64 | 0.0 | 60 |
| d_1006 | int64 | 0.0 | 65 |
| d_1007 | int64 | 0.0 | 59 |
| d_1008 | int64 | 0.0 | 74 |
| d_1009 | int64 | 0.0 | 80 |
| d_1010 | int64 | 0.0 | 84 |
| d_1011 | int64 | 0.0 | 63 |
| d_1012 | int64 | 0.0 | 61 |
| d_1013 | int64 | 0.0 | 64 |
| d_1014 | int64 | 0.0 | 66 |
| d_1015 | int64 | 0.0 | 70 |
| d_1016 | int64 | 0.0 | 82 |
| d_1017 | int64 | 0.0 | 81 |
| d_1018 | int64 | 0.0 | 72 |
| d_1019 | int64 | 0.0 | 65 |
| d_1020 | int64 | 0.0 | 60 |
| d_1021 | int64 | 0.0 | 60 |
| d_1022 | int64 | 0.0 | 71 |
| d_1023 | int64 | 0.0 | 82 |
| d_1024 | int64 | 0.0 | 81 |
| d_1025 | int64 | 0.0 | 60 |
| d_1026 | int64 | 0.0 | 61 |
| d_1027 | int64 | 0.0 | 53 |
| d_1028 | int64 | 0.0 | 60 |
| d_1029 | int64 | 0.0 | 64 |
| d_1030 | int64 | 0.0 | 74 |
| d_1031 | int64 | 0.0 | 69 |
| d_1032 | int64 | 0.0 | 64 |
| d_1033 | int64 | 0.0 | 64 |
| d_1034 | int64 | 0.0 | 79 |
| d_1035 | int64 | 0.0 | 66 |
| d_1036 | int64 | 0.0 | 63 |
| d_1037 | int64 | 0.0 | 60 |
| d_1038 | int64 | 0.0 | 69 |
| d_1039 | int64 | 0.0 | 75 |
| d_1040 | int64 | 0.0 | 76 |
| d_1041 | int64 | 0.0 | 66 |
| d_1042 | int64 | 0.0 | 73 |
| d_1043 | int64 | 0.0 | 75 |
| d_1044 | int64 | 0.0 | 85 |
| d_1045 | int64 | 0.0 | 74 |
| d_1046 | int64 | 0.0 | 66 |
| d_1047 | int64 | 0.0 | 63 |
| d_1048 | int64 | 0.0 | 67 |
| d_1049 | int64 | 0.0 | 64 |
| d_1050 | int64 | 0.0 | 73 |
| d_1051 | int64 | 0.0 | 76 |
| d_1052 | int64 | 0.0 | 79 |
| d_1053 | int64 | 0.0 | 63 |
| d_1054 | int64 | 0.0 | 63 |
| d_1055 | int64 | 0.0 | 60 |
| d_1056 | int64 | 0.0 | 67 |
| d_1057 | int64 | 0.0 | 62 |
| d_1058 | int64 | 0.0 | 75 |
| d_1059 | int64 | 0.0 | 70 |
| d_1060 | int64 | 0.0 | 69 |
| d_1061 | int64 | 0.0 | 71 |
| d_1062 | int64 | 0.0 | 5 |
| d_1063 | int64 | 0.0 | 71 |
| d_1064 | int64 | 0.0 | 70 |
| d_1065 | int64 | 0.0 | 70 |
| d_1066 | int64 | 0.0 | 68 |
| d_1067 | int64 | 0.0 | 66 |
| d_1068 | int64 | 0.0 | 83 |
| d_1069 | int64 | 0.0 | 56 |
| d_1070 | int64 | 0.0 | 67 |
| d_1071 | int64 | 0.0 | 73 |
| d_1072 | int64 | 0.0 | 83 |
| d_1073 | int64 | 0.0 | 92 |
| d_1074 | int64 | 0.0 | 67 |
| d_1075 | int64 | 0.0 | 68 |
| d_1076 | int64 | 0.0 | 66 |
| d_1077 | int64 | 0.0 | 63 |
| d_1078 | int64 | 0.0 | 60 |
| d_1079 | int64 | 0.0 | 83 |
| d_1080 | int64 | 0.0 | 85 |
| d_1081 | int64 | 0.0 | 65 |
| d_1082 | int64 | 0.0 | 64 |
| d_1083 | int64 | 0.0 | 59 |
| d_1084 | int64 | 0.0 | 65 |
| d_1085 | int64 | 0.0 | 68 |
| d_1086 | int64 | 0.0 | 73 |
| d_1087 | int64 | 0.0 | 72 |
| d_1088 | int64 | 0.0 | 58 |
| d_1089 | int64 | 0.0 | 55 |
| d_1090 | int64 | 0.0 | 55 |
| d_1091 | int64 | 0.0 | 50 |
| d_1092 | int64 | 0.0 | 57 |
| d_1093 | int64 | 0.0 | 70 |
| d_1094 | int64 | 0.0 | 77 |
| d_1095 | int64 | 0.0 | 61 |
| d_1096 | int64 | 0.0 | 54 |
| d_1097 | int64 | 0.0 | 48 |
| d_1098 | int64 | 0.0 | 58 |
| d_1099 | int64 | 0.0 | 66 |
| d_1100 | int64 | 0.0 | 82 |
| d_1101 | int64 | 0.0 | 79 |
| d_1102 | int64 | 0.0 | 73 |
| d_1103 | int64 | 0.0 | 61 |
| d_1104 | int64 | 0.0 | 64 |
| d_1105 | int64 | 0.0 | 67 |
| d_1106 | int64 | 0.0 | 55 |
| d_1107 | int64 | 0.0 | 71 |
| d_1108 | int64 | 0.0 | 75 |
| d_1109 | int64 | 0.0 | 59 |
| d_1110 | int64 | 0.0 | 65 |
| d_1111 | int64 | 0.0 | 65 |
| d_1112 | int64 | 0.0 | 71 |
| d_1113 | int64 | 0.0 | 66 |
| d_1114 | int64 | 0.0 | 68 |
| d_1115 | int64 | 0.0 | 72 |
| d_1116 | int64 | 0.0 | 64 |
| d_1117 | int64 | 0.0 | 56 |
| d_1118 | int64 | 0.0 | 55 |
| d_1119 | int64 | 0.0 | 53 |
| d_1120 | int64 | 0.0 | 59 |
| d_1121 | int64 | 0.0 | 64 |
| d_1122 | int64 | 0.0 | 68 |
| d_1123 | int64 | 0.0 | 52 |
| d_1124 | int64 | 0.0 | 51 |
| d_1125 | int64 | 0.0 | 46 |
| d_1126 | int64 | 0.0 | 52 |
| d_1127 | int64 | 0.0 | 59 |
| d_1128 | int64 | 0.0 | 64 |
| d_1129 | int64 | 0.0 | 73 |
| d_1130 | int64 | 0.0 | 63 |
| d_1131 | int64 | 0.0 | 56 |
| d_1132 | int64 | 0.0 | 56 |
| d_1133 | int64 | 0.0 | 59 |
| d_1134 | int64 | 0.0 | 57 |
| d_1135 | int64 | 0.0 | 72 |
| d_1136 | int64 | 0.0 | 81 |
| d_1137 | int64 | 0.0 | 64 |
| d_1138 | int64 | 0.0 | 65 |
| d_1139 | int64 | 0.0 | 68 |
| d_1140 | int64 | 0.0 | 60 |
| d_1141 | int64 | 0.0 | 67 |
| d_1142 | int64 | 0.0 | 72 |
| d_1143 | int64 | 0.0 | 75 |
| d_1144 | int64 | 0.0 | 59 |
| d_1145 | int64 | 0.0 | 56 |
| d_1146 | int64 | 0.0 | 54 |
| d_1147 | int64 | 0.0 | 55 |
| d_1148 | int64 | 0.0 | 65 |
| d_1149 | int64 | 0.0 | 72 |
| d_1150 | int64 | 0.0 | 75 |
| d_1151 | int64 | 0.0 | 60 |
| d_1152 | int64 | 0.0 | 52 |
| d_1153 | int64 | 0.0 | 50 |
| d_1154 | int64 | 0.0 | 57 |
| d_1155 | int64 | 0.0 | 56 |
| d_1156 | int64 | 0.0 | 72 |
| d_1157 | int64 | 0.0 | 74 |
| d_1158 | int64 | 0.0 | 55 |
| d_1159 | int64 | 0.0 | 58 |
| d_1160 | int64 | 0.0 | 58 |
| d_1161 | int64 | 0.0 | 66 |
| d_1162 | int64 | 0.0 | 64 |
| d_1163 | int64 | 0.0 | 78 |
| d_1164 | int64 | 0.0 | 81 |
| d_1165 | int64 | 0.0 | 69 |
| d_1166 | int64 | 0.0 | 69 |
| d_1167 | int64 | 0.0 | 71 |
| d_1168 | int64 | 0.0 | 66 |
| d_1169 | int64 | 0.0 | 73 |
| d_1170 | int64 | 0.0 | 78 |
| d_1171 | int64 | 0.0 | 79 |
| d_1172 | int64 | 0.0 | 67 |
| d_1173 | int64 | 0.0 | 64 |
| d_1174 | int64 | 0.0 | 62 |
| d_1175 | int64 | 0.0 | 61 |
| d_1176 | int64 | 0.0 | 65 |
| d_1177 | int64 | 0.0 | 80 |
| d_1178 | int64 | 0.0 | 84 |
| d_1179 | int64 | 0.0 | 61 |
| d_1180 | int64 | 0.0 | 55 |
| d_1181 | int64 | 0.0 | 58 |
| d_1182 | int64 | 0.0 | 58 |
| d_1183 | int64 | 0.0 | 64 |
| d_1184 | int64 | 0.0 | 67 |
| d_1185 | int64 | 0.0 | 74 |
| d_1186 | int64 | 0.0 | 58 |
| d_1187 | int64 | 0.0 | 61 |
| d_1188 | int64 | 0.0 | 59 |
| d_1189 | int64 | 0.0 | 66 |
| d_1190 | int64 | 0.0 | 71 |
| d_1191 | int64 | 0.0 | 83 |
| d_1192 | int64 | 0.0 | 77 |
| d_1193 | int64 | 0.0 | 67 |
| d_1194 | int64 | 0.0 | 61 |
| d_1195 | int64 | 0.0 | 57 |
| d_1196 | int64 | 0.0 | 65 |
| d_1197 | int64 | 0.0 | 69 |
| d_1198 | int64 | 0.0 | 75 |
| d_1199 | int64 | 0.0 | 78 |
| d_1200 | int64 | 0.0 | 76 |
| d_1201 | int64 | 0.0 | 65 |
| d_1202 | int64 | 0.0 | 68 |
| d_1203 | int64 | 0.0 | 64 |
| d_1204 | int64 | 0.0 | 61 |
| d_1205 | int64 | 0.0 | 67 |
| d_1206 | int64 | 0.0 | 73 |
| d_1207 | int64 | 0.0 | 57 |
| d_1208 | int64 | 0.0 | 53 |
| d_1209 | int64 | 0.0 | 59 |
| d_1210 | int64 | 0.0 | 56 |
| d_1211 | int64 | 0.0 | 57 |
| d_1212 | int64 | 0.0 | 68 |
| d_1213 | int64 | 0.0 | 67 |
| d_1214 | int64 | 0.0 | 62 |
| d_1215 | int64 | 0.0 | 54 |
| d_1216 | int64 | 0.0 | 49 |
| d_1217 | int64 | 0.0 | 53 |
| d_1218 | int64 | 0.0 | 59 |
| d_1219 | int64 | 0.0 | 64 |
| d_1220 | int64 | 0.0 | 73 |
| d_1221 | int64 | 0.0 | 67 |
| d_1222 | int64 | 0.0 | 66 |
| d_1223 | int64 | 0.0 | 61 |
| d_1224 | int64 | 0.0 | 67 |
| d_1225 | int64 | 0.0 | 68 |
| d_1226 | int64 | 0.0 | 78 |
| d_1227 | int64 | 0.0 | 82 |
| d_1228 | int64 | 0.0 | 76 |
| d_1229 | int64 | 0.0 | 67 |
| d_1230 | int64 | 0.0 | 63 |
| d_1231 | int64 | 0.0 | 67 |
| d_1232 | int64 | 0.0 | 74 |
| d_1233 | int64 | 0.0 | 80 |
| d_1234 | int64 | 0.0 | 81 |
| d_1235 | int64 | 0.0 | 67 |
| d_1236 | int64 | 0.0 | 61 |
| d_1237 | int64 | 0.0 | 62 |
| d_1238 | int64 | 0.0 | 60 |
| d_1239 | int64 | 0.0 | 70 |
| d_1240 | int64 | 0.0 | 75 |
| d_1241 | int64 | 0.0 | 70 |
| d_1242 | int64 | 0.0 | 61 |
| d_1243 | int64 | 0.0 | 55 |
| d_1244 | int64 | 0.0 | 51 |
| d_1245 | int64 | 0.0 | 53 |
| d_1246 | int64 | 0.0 | 66 |
| d_1247 | int64 | 0.0 | 66 |
| d_1248 | int64 | 0.0 | 76 |
| d_1249 | int64 | 0.0 | 67 |
| d_1250 | int64 | 0.0 | 65 |
| d_1251 | int64 | 0.0 | 69 |
| d_1252 | int64 | 0.0 | 80 |
| d_1253 | int64 | 0.0 | 75 |
| d_1254 | int64 | 0.0 | 74 |
| d_1255 | int64 | 0.0 | 89 |
| d_1256 | int64 | 0.0 | 72 |
| d_1257 | int64 | 0.0 | 67 |
| d_1258 | int64 | 0.0 | 69 |
| d_1259 | int64 | 0.0 | 69 |
| d_1260 | int64 | 0.0 | 77 |
| d_1261 | int64 | 0.0 | 86 |
| d_1262 | int64 | 0.0 | 78 |
| d_1263 | int64 | 0.0 | 76 |
| d_1264 | int64 | 0.0 | 73 |
| d_1265 | int64 | 0.0 | 67 |
| d_1266 | int64 | 0.0 | 66 |
| d_1267 | int64 | 0.0 | 73 |
| d_1268 | int64 | 0.0 | 79 |
| d_1269 | int64 | 0.0 | 78 |
| d_1270 | int64 | 0.0 | 62 |
| d_1271 | int64 | 0.0 | 62 |
| d_1272 | int64 | 0.0 | 65 |
| d_1273 | int64 | 0.0 | 65 |
| d_1274 | int64 | 0.0 | 67 |
| d_1275 | int64 | 0.0 | 75 |
| d_1276 | int64 | 0.0 | 86 |
| d_1277 | int64 | 0.0 | 61 |
| d_1278 | int64 | 0.0 | 63 |
| d_1279 | int64 | 0.0 | 61 |
| d_1280 | int64 | 0.0 | 64 |
| d_1281 | int64 | 0.0 | 76 |
| d_1282 | int64 | 0.0 | 81 |
| d_1283 | int64 | 0.0 | 91 |
| d_1284 | int64 | 0.0 | 70 |
| d_1285 | int64 | 0.0 | 74 |
| d_1286 | int64 | 0.0 | 66 |
| d_1287 | int64 | 0.0 | 71 |
| d_1288 | int64 | 0.0 | 75 |
| d_1289 | int64 | 0.0 | 81 |
| d_1290 | int64 | 0.0 | 80 |
| d_1291 | int64 | 0.0 | 70 |
| d_1292 | int64 | 0.0 | 72 |
| d_1293 | int64 | 0.0 | 64 |
| d_1294 | int64 | 0.0 | 65 |
| d_1295 | int64 | 0.0 | 73 |
| d_1296 | int64 | 0.0 | 83 |
| d_1297 | int64 | 0.0 | 82 |
| d_1298 | int64 | 0.0 | 71 |
| d_1299 | int64 | 0.0 | 63 |
| d_1300 | int64 | 0.0 | 58 |
| d_1301 | int64 | 0.0 | 58 |
| d_1302 | int64 | 0.0 | 69 |
| d_1303 | int64 | 0.0 | 77 |
| d_1304 | int64 | 0.0 | 84 |
| d_1305 | int64 | 0.0 | 65 |
| d_1306 | int64 | 0.0 | 60 |
| d_1307 | int64 | 0.0 | 59 |
| d_1308 | int64 | 0.0 | 57 |
| d_1309 | int64 | 0.0 | 64 |
| d_1310 | int64 | 0.0 | 76 |
| d_1311 | int64 | 0.0 | 71 |
| d_1312 | int64 | 0.0 | 76 |
| d_1313 | int64 | 0.0 | 63 |
| d_1314 | int64 | 0.0 | 69 |
| d_1315 | int64 | 0.0 | 64 |
| d_1316 | int64 | 0.0 | 67 |
| d_1317 | int64 | 0.0 | 80 |
| d_1318 | int64 | 0.0 | 85 |
| d_1319 | int64 | 0.0 | 68 |
| d_1320 | int64 | 0.0 | 66 |
| d_1321 | int64 | 0.0 | 62 |
| d_1322 | int64 | 0.0 | 67 |
| d_1323 | int64 | 0.0 | 69 |
| d_1324 | int64 | 0.0 | 79 |
| d_1325 | int64 | 0.0 | 84 |
| d_1326 | int64 | 0.0 | 69 |
| d_1327 | int64 | 0.0 | 61 |
| d_1328 | int64 | 0.0 | 56 |
| d_1329 | int64 | 0.0 | 55 |
| d_1330 | int64 | 0.0 | 66 |
| d_1331 | int64 | 0.0 | 76 |
| d_1332 | int64 | 0.0 | 77 |
| d_1333 | int64 | 0.0 | 61 |
| d_1334 | int64 | 0.0 | 57 |
| d_1335 | int64 | 0.0 | 57 |
| d_1336 | int64 | 0.0 | 58 |
| d_1337 | int64 | 0.0 | 59 |
| d_1338 | int64 | 0.0 | 71 |
| d_1339 | int64 | 0.0 | 73 |
| d_1340 | int64 | 0.0 | 59 |
| d_1341 | int64 | 0.0 | 58 |
| d_1342 | int64 | 0.0 | 62 |
| d_1343 | int64 | 0.0 | 66 |
| d_1344 | int64 | 0.0 | 76 |
| d_1345 | int64 | 0.0 | 74 |
| d_1346 | int64 | 0.0 | 83 |
| d_1347 | int64 | 0.0 | 69 |
| d_1348 | int64 | 0.0 | 61 |
| d_1349 | int64 | 0.0 | 62 |
| d_1350 | int64 | 0.0 | 64 |
| d_1351 | int64 | 0.0 | 63 |
| d_1352 | int64 | 0.0 | 74 |
| d_1353 | int64 | 0.0 | 77 |
| d_1354 | int64 | 0.0 | 58 |
| d_1355 | int64 | 0.0 | 57 |
| d_1356 | int64 | 0.0 | 65 |
| d_1357 | int64 | 0.0 | 52 |
| d_1358 | int64 | 0.0 | 54 |
| d_1359 | int64 | 0.0 | 71 |
| d_1360 | int64 | 0.0 | 76 |
| d_1361 | int64 | 0.0 | 55 |
| d_1362 | int64 | 0.0 | 51 |
| d_1363 | int64 | 0.0 | 50 |
| d_1364 | int64 | 0.0 | 52 |
| d_1365 | int64 | 0.0 | 63 |
| d_1366 | int64 | 0.0 | 69 |
| d_1367 | int64 | 0.0 | 66 |
| d_1368 | int64 | 0.0 | 60 |
| d_1369 | int64 | 0.0 | 56 |
| d_1370 | int64 | 0.0 | 57 |
| d_1371 | int64 | 0.0 | 63 |
| d_1372 | int64 | 0.0 | 64 |
| d_1373 | int64 | 0.0 | 73 |
| d_1374 | int64 | 0.0 | 75 |
| d_1375 | int64 | 0.0 | 66 |
| d_1376 | int64 | 0.0 | 59 |
| d_1377 | int64 | 0.0 | 59 |
| d_1378 | int64 | 0.0 | 58 |
| d_1379 | int64 | 0.0 | 65 |
| d_1380 | int64 | 0.0 | 75 |
| d_1381 | int64 | 0.0 | 78 |
| d_1382 | int64 | 0.0 | 62 |
| d_1383 | int64 | 0.0 | 62 |
| d_1384 | int64 | 0.0 | 58 |
| d_1385 | int64 | 0.0 | 53 |
| d_1386 | int64 | 0.0 | 65 |
| d_1387 | int64 | 0.0 | 74 |
| d_1388 | int64 | 0.0 | 74 |
| d_1389 | int64 | 0.0 | 54 |
| d_1390 | int64 | 0.0 | 54 |
| d_1391 | int64 | 0.0 | 53 |
| d_1392 | int64 | 0.0 | 55 |
| d_1393 | int64 | 0.0 | 63 |
| d_1394 | int64 | 0.0 | 70 |
| d_1395 | int64 | 0.0 | 70 |
| d_1396 | int64 | 0.0 | 56 |
| d_1397 | int64 | 0.0 | 63 |
| d_1398 | int64 | 0.0 | 76 |
| d_1399 | int64 | 0.0 | 75 |
| d_1400 | int64 | 0.0 | 60 |
| d_1401 | int64 | 0.0 | 61 |
| d_1402 | int64 | 0.0 | 62 |
| d_1403 | int64 | 0.0 | 55 |
| d_1404 | int64 | 0.0 | 58 |
| d_1405 | int64 | 0.0 | 59 |
| d_1406 | int64 | 0.0 | 56 |
| d_1407 | int64 | 0.0 | 67 |
| d_1408 | int64 | 0.0 | 68 |
| d_1409 | int64 | 0.0 | 64 |
| d_1410 | int64 | 0.0 | 61 |
| d_1411 | int64 | 0.0 | 58 |
| d_1412 | int64 | 0.0 | 55 |
| d_1413 | int64 | 0.0 | 55 |
| d_1414 | int64 | 0.0 | 56 |
| d_1415 | int64 | 0.0 | 65 |
| d_1416 | int64 | 0.0 | 63 |
| d_1417 | int64 | 0.0 | 58 |
| d_1418 | int64 | 0.0 | 52 |
| d_1419 | int64 | 0.0 | 57 |
| d_1420 | int64 | 0.0 | 66 |
| d_1421 | int64 | 0.0 | 57 |
| d_1422 | int64 | 0.0 | 65 |
| d_1423 | int64 | 0.0 | 71 |
| d_1424 | int64 | 0.0 | 64 |
| d_1425 | int64 | 0.0 | 67 |
| d_1426 | int64 | 0.0 | 68 |
| d_1427 | int64 | 0.0 | 3 |
| d_1428 | int64 | 0.0 | 59 |
| d_1429 | int64 | 0.0 | 57 |
| d_1430 | int64 | 0.0 | 55 |
| d_1431 | int64 | 0.0 | 49 |
| d_1432 | int64 | 0.0 | 50 |
| d_1433 | int64 | 0.0 | 65 |
| d_1434 | int64 | 0.0 | 50 |
| d_1435 | int64 | 0.0 | 67 |
| d_1436 | int64 | 0.0 | 71 |
| d_1437 | int64 | 0.0 | 73 |
| d_1438 | int64 | 0.0 | 59 |
| d_1439 | int64 | 0.0 | 65 |
| d_1440 | int64 | 0.0 | 58 |
| d_1441 | int64 | 0.0 | 58 |
| d_1442 | int64 | 0.0 | 60 |
| d_1443 | int64 | 0.0 | 70 |
| d_1444 | int64 | 0.0 | 74 |
| d_1445 | int64 | 0.0 | 65 |
| d_1446 | int64 | 0.0 | 57 |
| d_1447 | int64 | 0.0 | 60 |
| d_1448 | int64 | 0.0 | 62 |
| d_1449 | int64 | 0.0 | 62 |
| d_1450 | int64 | 0.0 | 77 |
| d_1451 | int64 | 0.0 | 74 |
| d_1452 | int64 | 0.0 | 58 |
| d_1453 | int64 | 0.0 | 56 |
| d_1454 | int64 | 0.0 | 52 |
| d_1455 | int64 | 0.0 | 51 |
| d_1456 | int64 | 0.0 | 60 |
| d_1457 | int64 | 0.0 | 66 |
| d_1458 | int64 | 0.0 | 71 |
| d_1459 | int64 | 0.0 | 56 |
| d_1460 | int64 | 0.0 | 54 |
| d_1461 | int64 | 0.0 | 55 |
| d_1462 | int64 | 0.0 | 52 |
| d_1463 | int64 | 0.0 | 64 |
| d_1464 | int64 | 0.0 | 79 |
| d_1465 | int64 | 0.0 | 76 |
| d_1466 | int64 | 0.0 | 59 |
| d_1467 | int64 | 0.0 | 60 |
| d_1468 | int64 | 0.0 | 63 |
| d_1469 | int64 | 0.0 | 59 |
| d_1470 | int64 | 0.0 | 68 |
| d_1471 | int64 | 0.0 | 75 |
| d_1472 | int64 | 0.0 | 79 |
| d_1473 | int64 | 0.0 | 66 |
| d_1474 | int64 | 0.0 | 61 |
| d_1475 | int64 | 0.0 | 65 |
| d_1476 | int64 | 0.0 | 64 |
| d_1477 | int64 | 0.0 | 63 |
| d_1478 | int64 | 0.0 | 76 |
| d_1479 | int64 | 0.0 | 66 |
| d_1480 | int64 | 0.0 | 55 |
| d_1481 | int64 | 0.0 | 50 |
| d_1482 | int64 | 0.0 | 53 |
| d_1483 | int64 | 0.0 | 52 |
| d_1484 | int64 | 0.0 | 53 |
| d_1485 | int64 | 0.0 | 62 |
| d_1486 | int64 | 0.0 | 64 |
| d_1487 | int64 | 0.0 | 52 |
| d_1488 | int64 | 0.0 | 56 |
| d_1489 | int64 | 0.0 | 50 |
| d_1490 | int64 | 0.0 | 48 |
| d_1491 | int64 | 0.0 | 50 |
| d_1492 | int64 | 0.0 | 56 |
| d_1493 | int64 | 0.0 | 64 |
| d_1494 | int64 | 0.0 | 55 |
| d_1495 | int64 | 0.0 | 59 |
| d_1496 | int64 | 0.0 | 57 |
| d_1497 | int64 | 0.0 | 60 |
| d_1498 | int64 | 0.0 | 60 |
| d_1499 | int64 | 0.0 | 67 |
| d_1500 | int64 | 0.0 | 78 |
| d_1501 | int64 | 0.0 | 63 |
| d_1502 | int64 | 0.0 | 57 |
| d_1503 | int64 | 0.0 | 52 |
| d_1504 | int64 | 0.0 | 63 |
| d_1505 | int64 | 0.0 | 67 |
| d_1506 | int64 | 0.0 | 76 |
| d_1507 | int64 | 0.0 | 77 |
| d_1508 | int64 | 0.0 | 62 |
| d_1509 | int64 | 0.0 | 60 |
| d_1510 | int64 | 0.0 | 54 |
| d_1511 | int64 | 0.0 | 54 |
| d_1512 | int64 | 0.0 | 57 |
| d_1513 | int64 | 0.0 | 70 |
| d_1514 | int64 | 0.0 | 69 |
| d_1515 | int64 | 0.0 | 57 |
| d_1516 | int64 | 0.0 | 55 |
| d_1517 | int64 | 0.0 | 54 |
| d_1518 | int64 | 0.0 | 53 |
| d_1519 | int64 | 0.0 | 57 |
| d_1520 | int64 | 0.0 | 69 |
| d_1521 | int64 | 0.0 | 71 |
| d_1522 | int64 | 0.0 | 55 |
| d_1523 | int64 | 0.0 | 51 |
| d_1524 | int64 | 0.0 | 61 |
| d_1525 | int64 | 0.0 | 58 |
| d_1526 | int64 | 0.0 | 74 |
| d_1527 | int64 | 0.0 | 78 |
| d_1528 | int64 | 0.0 | 70 |
| d_1529 | int64 | 0.0 | 67 |
| d_1530 | int64 | 0.0 | 60 |
| d_1531 | int64 | 0.0 | 59 |
| d_1532 | int64 | 0.0 | 60 |
| d_1533 | int64 | 0.0 | 59 |
| d_1534 | int64 | 0.0 | 73 |
| d_1535 | int64 | 0.0 | 70 |
| d_1536 | int64 | 0.0 | 54 |
| d_1537 | int64 | 0.0 | 64 |
| d_1538 | int64 | 0.0 | 59 |
| d_1539 | int64 | 0.0 | 55 |
| d_1540 | int64 | 0.0 | 61 |
| d_1541 | int64 | 0.0 | 70 |
| d_1542 | int64 | 0.0 | 64 |
| d_1543 | int64 | 0.0 | 55 |
| d_1544 | int64 | 0.0 | 54 |
| d_1545 | int64 | 0.0 | 52 |
| d_1546 | int64 | 0.0 | 56 |
| d_1547 | int64 | 0.0 | 57 |
| d_1548 | int64 | 0.0 | 66 |
| d_1549 | int64 | 0.0 | 70 |
| d_1550 | int64 | 0.0 | 56 |
| d_1551 | int64 | 0.0 | 47 |
| d_1552 | int64 | 0.0 | 53 |
| d_1553 | int64 | 0.0 | 59 |
| d_1554 | int64 | 0.0 | 65 |
| d_1555 | int64 | 0.0 | 79 |
| d_1556 | int64 | 0.0 | 74 |
| d_1557 | int64 | 0.0 | 59 |
| d_1558 | int64 | 0.0 | 59 |
| d_1559 | int64 | 0.0 | 60 |
| d_1560 | int64 | 0.0 | 57 |
| d_1561 | int64 | 0.0 | 63 |
| d_1562 | int64 | 0.0 | 73 |
| d_1563 | int64 | 0.0 | 67 |
| d_1564 | int64 | 0.0 | 63 |
| d_1565 | int64 | 0.0 | 60 |
| d_1566 | int64 | 0.0 | 55 |
| d_1567 | int64 | 0.0 | 52 |
| d_1568 | int64 | 0.0 | 61 |
| d_1569 | int64 | 0.0 | 63 |
| d_1570 | int64 | 0.0 | 65 |
| d_1571 | int64 | 0.0 | 50 |
| d_1572 | int64 | 0.0 | 51 |
| d_1573 | int64 | 0.0 | 53 |
| d_1574 | int64 | 0.0 | 45 |
| d_1575 | int64 | 0.0 | 59 |
| d_1576 | int64 | 0.0 | 63 |
| d_1577 | int64 | 0.0 | 58 |
| d_1578 | int64 | 0.0 | 62 |
| d_1579 | int64 | 0.0 | 52 |
| d_1580 | int64 | 0.0 | 47 |
| d_1581 | int64 | 0.0 | 50 |
| d_1582 | int64 | 0.0 | 54 |
| d_1583 | int64 | 0.0 | 63 |
| d_1584 | int64 | 0.0 | 63 |
| d_1585 | int64 | 0.0 | 60 |
| d_1586 | int64 | 0.0 | 68 |
| d_1587 | int64 | 0.0 | 61 |
| d_1588 | int64 | 0.0 | 53 |
| d_1589 | int64 | 0.0 | 64 |
| d_1590 | int64 | 0.0 | 68 |
| d_1591 | int64 | 0.0 | 79 |
| d_1592 | int64 | 0.0 | 70 |
| d_1593 | int64 | 0.0 | 67 |
| d_1594 | int64 | 0.0 | 60 |
| d_1595 | int64 | 0.0 | 64 |
| d_1596 | int64 | 0.0 | 70 |
| d_1597 | int64 | 0.0 | 67 |
| d_1598 | int64 | 0.0 | 96 |
| d_1599 | int64 | 0.0 | 84 |
| d_1600 | int64 | 0.0 | 59 |
| d_1601 | int64 | 0.0 | 60 |
| d_1602 | int64 | 0.0 | 61 |
| d_1603 | int64 | 0.0 | 65 |
| d_1604 | int64 | 0.0 | 74 |
| d_1605 | int64 | 0.0 | 75 |
| d_1606 | int64 | 0.0 | 58 |
| d_1607 | int64 | 0.0 | 62 |
| d_1608 | int64 | 0.0 | 57 |
| d_1609 | int64 | 0.0 | 63 |
| d_1610 | int64 | 0.0 | 63 |
| d_1611 | int64 | 0.0 | 76 |
| d_1612 | int64 | 0.0 | 77 |
| d_1613 | int64 | 0.0 | 61 |
| d_1614 | int64 | 0.0 | 61 |
| d_1615 | int64 | 0.0 | 67 |
| d_1616 | int64 | 0.0 | 73 |
| d_1617 | int64 | 0.0 | 91 |
| d_1618 | int64 | 0.0 | 77 |
| d_1619 | int64 | 0.0 | 76 |
| d_1620 | int64 | 0.0 | 69 |
| d_1621 | int64 | 0.0 | 67 |
| d_1622 | int64 | 0.0 | 60 |
| d_1623 | int64 | 0.0 | 64 |
| d_1624 | int64 | 0.0 | 66 |
| d_1625 | int64 | 0.0 | 75 |
| d_1626 | int64 | 0.0 | 78 |
| d_1627 | int64 | 0.0 | 62 |
| d_1628 | int64 | 0.0 | 67 |
| d_1629 | int64 | 0.0 | 66 |
| d_1630 | int64 | 0.0 | 61 |
| d_1631 | int64 | 0.0 | 71 |
| d_1632 | int64 | 0.0 | 75 |
| d_1633 | int64 | 0.0 | 80 |
| d_1634 | int64 | 0.0 | 67 |
| d_1635 | int64 | 0.0 | 62 |
| d_1636 | int64 | 0.0 | 59 |
| d_1637 | int64 | 0.0 | 60 |
| d_1638 | int64 | 0.0 | 69 |
| d_1639 | int64 | 0.0 | 72 |
| d_1640 | int64 | 0.0 | 79 |
| d_1641 | int64 | 0.0 | 64 |
| d_1642 | int64 | 0.0 | 65 |
| d_1643 | int64 | 0.0 | 56 |
| d_1644 | int64 | 0.0 | 60 |
| d_1645 | int64 | 0.0 | 70 |
| d_1646 | int64 | 0.0 | 79 |
| d_1647 | int64 | 0.0 | 86 |
| d_1648 | int64 | 0.0 | 72 |
| d_1649 | int64 | 0.0 | 59 |
| d_1650 | int64 | 0.0 | 69 |
| d_1651 | int64 | 0.0 | 64 |
| d_1652 | int64 | 0.0 | 69 |
| d_1653 | int64 | 0.0 | 82 |
| d_1654 | int64 | 0.0 | 85 |
| d_1655 | int64 | 0.0 | 64 |
| d_1656 | int64 | 0.0 | 63 |
| d_1657 | int64 | 0.0 | 70 |
| d_1658 | int64 | 0.0 | 64 |
| d_1659 | int64 | 0.0 | 75 |
| d_1660 | int64 | 0.0 | 83 |
| d_1661 | int64 | 0.0 | 89 |
| d_1662 | int64 | 0.0 | 72 |
| d_1663 | int64 | 0.0 | 64 |
| d_1664 | int64 | 0.0 | 58 |
| d_1665 | int64 | 0.0 | 59 |
| d_1666 | int64 | 0.0 | 65 |
| d_1667 | int64 | 0.0 | 71 |
| d_1668 | int64 | 0.0 | 73 |
| d_1669 | int64 | 0.0 | 62 |
| d_1670 | int64 | 0.0 | 55 |
| d_1671 | int64 | 0.0 | 57 |
| d_1672 | int64 | 0.0 | 57 |
| d_1673 | int64 | 0.0 | 65 |
| d_1674 | int64 | 0.0 | 77 |
| d_1675 | int64 | 0.0 | 72 |
| d_1676 | int64 | 0.0 | 56 |
| d_1677 | int64 | 0.0 | 63 |
| d_1678 | int64 | 0.0 | 65 |
| d_1679 | int64 | 0.0 | 64 |
| d_1680 | int64 | 0.0 | 63 |
| d_1681 | int64 | 0.0 | 72 |
| d_1682 | int64 | 0.0 | 82 |
| d_1683 | int64 | 0.0 | 78 |
| d_1684 | int64 | 0.0 | 65 |
| d_1685 | int64 | 0.0 | 67 |
| d_1686 | int64 | 0.0 | 61 |
| d_1687 | int64 | 0.0 | 69 |
| d_1688 | int64 | 0.0 | 76 |
| d_1689 | int64 | 0.0 | 79 |
| d_1690 | int64 | 0.0 | 61 |
| d_1691 | int64 | 0.0 | 61 |
| d_1692 | int64 | 0.0 | 58 |
| d_1693 | int64 | 0.0 | 56 |
| d_1694 | int64 | 0.0 | 66 |
| d_1695 | int64 | 0.0 | 75 |
| d_1696 | int64 | 0.0 | 78 |
| d_1697 | int64 | 0.0 | 63 |
| d_1698 | int64 | 0.0 | 54 |
| d_1699 | int64 | 0.0 | 58 |
| d_1700 | int64 | 0.0 | 62 |
| d_1701 | int64 | 0.0 | 70 |
| d_1702 | int64 | 0.0 | 73 |
| d_1703 | int64 | 0.0 | 71 |
| d_1704 | int64 | 0.0 | 54 |
| d_1705 | int64 | 0.0 | 51 |
| d_1706 | int64 | 0.0 | 50 |
| d_1707 | int64 | 0.0 | 61 |
| d_1708 | int64 | 0.0 | 70 |
| d_1709 | int64 | 0.0 | 82 |
| d_1710 | int64 | 0.0 | 71 |
| d_1711 | int64 | 0.0 | 67 |
| d_1712 | int64 | 0.0 | 62 |
| d_1713 | int64 | 0.0 | 60 |
| d_1714 | int64 | 0.0 | 66 |
| d_1715 | int64 | 0.0 | 69 |
| d_1716 | int64 | 0.0 | 74 |
| d_1717 | int64 | 0.0 | 73 |
| d_1718 | int64 | 0.0 | 67 |
| d_1719 | int64 | 0.0 | 63 |
| d_1720 | int64 | 0.0 | 62 |
| d_1721 | int64 | 0.0 | 61 |
| d_1722 | int64 | 0.0 | 65 |
| d_1723 | int64 | 0.0 | 72 |
| d_1724 | int64 | 0.0 | 78 |
| d_1725 | int64 | 0.0 | 55 |
| d_1726 | int64 | 0.0 | 53 |
| d_1727 | int64 | 0.0 | 56 |
| d_1728 | int64 | 0.0 | 58 |
| d_1729 | int64 | 0.0 | 62 |
| d_1730 | int64 | 0.0 | 64 |
| d_1731 | int64 | 0.0 | 74 |
| d_1732 | int64 | 0.0 | 54 |
| d_1733 | int64 | 0.0 | 56 |
| d_1734 | int64 | 0.0 | 54 |
| d_1735 | int64 | 0.0 | 60 |
| d_1736 | int64 | 0.0 | 69 |
| d_1737 | int64 | 0.0 | 71 |
| d_1738 | int64 | 0.0 | 68 |
| d_1739 | int64 | 0.0 | 54 |
| d_1740 | int64 | 0.0 | 55 |
| d_1741 | int64 | 0.0 | 52 |
| d_1742 | int64 | 0.0 | 58 |
| d_1743 | int64 | 0.0 | 64 |
| d_1744 | int64 | 0.0 | 70 |
| d_1745 | int64 | 0.0 | 67 |
| d_1746 | int64 | 0.0 | 60 |
| d_1747 | int64 | 0.0 | 54 |
| d_1748 | int64 | 0.0 | 57 |
| d_1749 | int64 | 0.0 | 61 |
| d_1750 | int64 | 0.0 | 67 |
| d_1751 | int64 | 0.0 | 66 |
| d_1752 | int64 | 0.0 | 74 |
| d_1753 | int64 | 0.0 | 55 |
| d_1754 | int64 | 0.0 | 50 |
| d_1755 | int64 | 0.0 | 50 |
| d_1756 | int64 | 0.0 | 52 |
| d_1757 | int64 | 0.0 | 64 |
| d_1758 | int64 | 0.0 | 69 |
| d_1759 | int64 | 0.0 | 72 |
| d_1760 | int64 | 0.0 | 62 |
| d_1761 | int64 | 0.0 | 63 |
| d_1762 | int64 | 0.0 | 81 |
| d_1763 | int64 | 0.0 | 77 |
| d_1764 | int64 | 0.0 | 62 |
| d_1765 | int64 | 0.0 | 60 |
| d_1766 | int64 | 0.0 | 58 |
| d_1767 | int64 | 0.0 | 54 |
| d_1768 | int64 | 0.0 | 56 |
| d_1769 | int64 | 0.0 | 58 |
| d_1770 | int64 | 0.0 | 60 |
| d_1771 | int64 | 0.0 | 57 |
| d_1772 | int64 | 0.0 | 71 |
| d_1773 | int64 | 0.0 | 71 |
| d_1774 | int64 | 0.0 | 52 |
| d_1775 | int64 | 0.0 | 56 |
| d_1776 | int64 | 0.0 | 58 |
| d_1777 | int64 | 0.0 | 54 |
| d_1778 | int64 | 0.0 | 66 |
| d_1779 | int64 | 0.0 | 72 |
| d_1780 | int64 | 0.0 | 67 |
| d_1781 | int64 | 0.0 | 60 |
| d_1782 | int64 | 0.0 | 62 |
| d_1783 | int64 | 0.0 | 54 |
| d_1784 | int64 | 0.0 | 61 |
| d_1785 | int64 | 0.0 | 56 |
| d_1786 | int64 | 0.0 | 70 |
| d_1787 | int64 | 0.0 | 64 |
| d_1788 | int64 | 0.0 | 58 |
| d_1789 | int64 | 0.0 | 60 |
| d_1790 | int64 | 0.0 | 65 |
| d_1791 | int64 | 0.0 | 72 |
| d_1792 | int64 | 0.0 | 3 |
| d_1793 | int64 | 0.0 | 65 |
| d_1794 | int64 | 0.0 | 58 |
| d_1795 | int64 | 0.0 | 47 |
| d_1796 | int64 | 0.0 | 49 |
| d_1797 | int64 | 0.0 | 53 |
| d_1798 | int64 | 0.0 | 71 |
| d_1799 | int64 | 0.0 | 54 |
| d_1800 | int64 | 0.0 | 61 |
| d_1801 | int64 | 0.0 | 62 |
| d_1802 | int64 | 0.0 | 54 |
| d_1803 | int64 | 0.0 | 56 |
| d_1804 | int64 | 0.0 | 53 |
| d_1805 | int64 | 0.0 | 65 |
| d_1806 | int64 | 0.0 | 64 |
| d_1807 | int64 | 0.0 | 77 |
| d_1808 | int64 | 0.0 | 70 |
| d_1809 | int64 | 0.0 | 65 |
| d_1810 | int64 | 0.0 | 58 |
| d_1811 | int64 | 0.0 | 54 |
| d_1812 | int64 | 0.0 | 58 |
| d_1813 | int64 | 0.0 | 64 |
| d_1814 | int64 | 0.0 | 71 |
| d_1815 | int64 | 0.0 | 67 |
| d_1816 | int64 | 0.0 | 59 |
| d_1817 | int64 | 0.0 | 56 |
| d_1818 | int64 | 0.0 | 55 |
| d_1819 | int64 | 0.0 | 57 |
| d_1820 | int64 | 0.0 | 57 |
| d_1821 | int64 | 0.0 | 70 |
| d_1822 | int64 | 0.0 | 70 |
| d_1823 | int64 | 0.0 | 55 |
| d_1824 | int64 | 0.0 | 49 |
| d_1825 | int64 | 0.0 | 51 |
| d_1826 | int64 | 0.0 | 49 |
| d_1827 | int64 | 0.0 | 57 |
| d_1828 | int64 | 0.0 | 72 |
| d_1829 | int64 | 0.0 | 69 |
| d_1830 | int64 | 0.0 | 64 |
| d_1831 | int64 | 0.0 | 54 |
| d_1832 | int64 | 0.0 | 66 |
| d_1833 | int64 | 0.0 | 59 |
| d_1834 | int64 | 0.0 | 65 |
| d_1835 | int64 | 0.0 | 78 |
| d_1836 | int64 | 0.0 | 73 |
| d_1837 | int64 | 0.0 | 58 |
| d_1838 | int64 | 0.0 | 58 |
| d_1839 | int64 | 0.0 | 66 |
| d_1840 | int64 | 0.0 | 68 |
| d_1841 | int64 | 0.0 | 70 |
| d_1842 | int64 | 0.0 | 77 |
| d_1843 | int64 | 0.0 | 72 |
| d_1844 | int64 | 0.0 | 76 |
| d_1845 | int64 | 0.0 | 64 |
| d_1846 | int64 | 0.0 | 62 |
| d_1847 | int64 | 0.0 | 60 |
| d_1848 | int64 | 0.0 | 64 |
| d_1849 | int64 | 0.0 | 75 |
| d_1850 | int64 | 0.0 | 76 |
| d_1851 | int64 | 0.0 | 55 |
| d_1852 | int64 | 0.0 | 56 |
| d_1853 | int64 | 0.0 | 55 |
| d_1854 | int64 | 0.0 | 58 |
| d_1855 | int64 | 0.0 | 58 |
| d_1856 | int64 | 0.0 | 67 |
| d_1857 | int64 | 0.0 | 69 |
| d_1858 | int64 | 0.0 | 55 |
| d_1859 | int64 | 0.0 | 58 |
| d_1860 | int64 | 0.0 | 59 |
| d_1861 | int64 | 0.0 | 61 |
| d_1862 | int64 | 0.0 | 63 |
| d_1863 | int64 | 0.0 | 72 |
| d_1864 | int64 | 0.0 | 76 |
| d_1865 | int64 | 0.0 | 60 |
| d_1866 | int64 | 0.0 | 63 |
| d_1867 | int64 | 0.0 | 58 |
| d_1868 | int64 | 0.0 | 57 |
| d_1869 | int64 | 0.0 | 61 |
| d_1870 | int64 | 0.0 | 73 |
| d_1871 | int64 | 0.0 | 74 |
| d_1872 | int64 | 0.0 | 62 |
| d_1873 | int64 | 0.0 | 62 |
| d_1874 | int64 | 0.0 | 61 |
| d_1875 | int64 | 0.0 | 60 |
| d_1876 | int64 | 0.0 | 61 |
| d_1877 | int64 | 0.0 | 64 |
| d_1878 | int64 | 0.0 | 72 |
| d_1879 | int64 | 0.0 | 54 |
| d_1880 | int64 | 0.0 | 53 |
| d_1881 | int64 | 0.0 | 53 |
| d_1882 | int64 | 0.0 | 55 |
| d_1883 | int64 | 0.0 | 73 |
| d_1884 | int64 | 0.0 | 85 |
| d_1885 | int64 | 0.0 | 82 |
| d_1886 | int64 | 0.0 | 55 |
| d_1887 | int64 | 0.0 | 55 |
| d_1888 | int64 | 0.0 | 56 |
| d_1889 | int64 | 0.0 | 56 |
| d_1890 | int64 | 0.0 | 64 |
| d_1891 | int64 | 0.0 | 77 |
| d_1892 | int64 | 0.0 | 75 |
| d_1893 | int64 | 0.0 | 61 |
| d_1894 | int64 | 0.0 | 63 |
| d_1895 | int64 | 0.0 | 61 |
| d_1896 | int64 | 0.0 | 60 |
| d_1897 | int64 | 0.0 | 70 |
| d_1898 | int64 | 0.0 | 80 |
| d_1899 | int64 | 0.0 | 72 |
| d_1900 | int64 | 0.0 | 64 |
| d_1901 | int64 | 0.0 | 59 |
| d_1902 | int64 | 0.0 | 55 |
| d_1903 | int64 | 0.0 | 63 |
| d_1904 | int64 | 0.0 | 69 |
| d_1905 | int64 | 0.0 | 71 |
| d_1906 | int64 | 0.0 | 77 |
| d_1907 | int64 | 0.0 | 61 |
| d_1908 | int64 | 0.0 | 57 |
| d_1909 | int64 | 0.0 | 53 |
| d_1910 | int64 | 0.0 | 57 |
| d_1911 | int64 | 0.0 | 61 |
| d_1912 | int64 | 0.0 | 73 |
| d_1913 | int64 | 0.0 | 65 |
| d_1914 | int64 | 0.0 | 58 |
| d_1915 | int64 | 0.0 | 53 |
| d_1916 | int64 | 0.0 | 54 |
| d_1917 | int64 | 0.0 | 57 |
| d_1918 | int64 | 0.0 | 64 |
| d_1919 | int64 | 0.0 | 69 |
| d_1920 | int64 | 0.0 | 71 |
| d_1921 | int64 | 0.0 | 59 |
| d_1922 | int64 | 0.0 | 61 |
| d_1923 | int64 | 0.0 | 61 |
| d_1924 | int64 | 0.0 | 62 |
| d_1925 | int64 | 0.0 | 70 |
| d_1926 | int64 | 0.0 | 77 |
| d_1927 | int64 | 0.0 | 71 |
| d_1928 | int64 | 0.0 | 68 |
| d_1929 | int64 | 0.0 | 56 |
| d_1930 | int64 | 0.0 | 62 |
| d_1931 | int64 | 0.0 | 61 |
| d_1932 | int64 | 0.0 | 66 |
| d_1933 | int64 | 0.0 | 78 |
| d_1934 | int64 | 0.0 | 77 |
| d_1935 | int64 | 0.0 | 59 |
| d_1936 | int64 | 0.0 | 59 |
| d_1937 | int64 | 0.0 | 56 |
| d_1938 | int64 | 0.0 | 54 |
| d_1939 | int64 | 0.0 | 64 |
| d_1940 | int64 | 0.0 | 67 |
| d_1941 | int64 | 0.0 | 76 |

### `data\raw\m5\sales_train_validation.csv`

Size: 120007726 bytes. Profiled rows: 30490. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| id | str | 0.0 | 30490 |
| item_id | str | 0.0 | 3049 |
| dept_id | str | 0.0 | 7 |
| cat_id | str | 0.0 | 3 |
| store_id | str | 0.0 | 10 |
| state_id | str | 0.0 | 3 |
| d_1 | int64 | 0.0 | 84 |
| d_2 | int64 | 0.0 | 82 |
| d_3 | int64 | 0.0 | 72 |
| d_4 | int64 | 0.0 | 79 |
| d_5 | int64 | 0.0 | 63 |
| d_6 | int64 | 0.0 | 84 |
| d_7 | int64 | 0.0 | 85 |
| d_8 | int64 | 0.0 | 100 |
| d_9 | int64 | 0.0 | 91 |
| d_10 | int64 | 0.0 | 73 |
| d_11 | int64 | 0.0 | 68 |
| d_12 | int64 | 0.0 | 69 |
| d_13 | int64 | 0.0 | 65 |
| d_14 | int64 | 0.0 | 68 |
| d_15 | int64 | 0.0 | 81 |
| d_16 | int64 | 0.0 | 82 |
| d_17 | int64 | 0.0 | 61 |
| d_18 | int64 | 0.0 | 67 |
| d_19 | int64 | 0.0 | 60 |
| d_20 | int64 | 0.0 | 52 |
| d_21 | int64 | 0.0 | 62 |
| d_22 | int64 | 0.0 | 75 |
| d_23 | int64 | 0.0 | 64 |
| d_24 | int64 | 0.0 | 60 |
| d_25 | int64 | 0.0 | 58 |
| d_26 | int64 | 0.0 | 54 |
| d_27 | int64 | 0.0 | 53 |
| d_28 | int64 | 0.0 | 56 |
| d_29 | int64 | 0.0 | 65 |
| d_30 | int64 | 0.0 | 71 |
| d_31 | int64 | 0.0 | 54 |
| d_32 | int64 | 0.0 | 60 |
| d_33 | int64 | 0.0 | 55 |
| d_34 | int64 | 0.0 | 61 |
| d_35 | int64 | 0.0 | 62 |
| d_36 | int64 | 0.0 | 73 |
| d_37 | int64 | 0.0 | 80 |
| d_38 | int64 | 0.0 | 60 |
| d_39 | int64 | 0.0 | 58 |
| d_40 | int64 | 0.0 | 58 |
| d_41 | int64 | 0.0 | 59 |
| d_42 | int64 | 0.0 | 63 |
| d_43 | int64 | 0.0 | 74 |
| d_44 | int64 | 0.0 | 71 |
| d_45 | int64 | 0.0 | 62 |
| d_46 | int64 | 0.0 | 65 |
| d_47 | int64 | 0.0 | 56 |
| d_48 | int64 | 0.0 | 61 |
| d_49 | int64 | 0.0 | 58 |
| d_50 | int64 | 0.0 | 71 |
| d_51 | int64 | 0.0 | 70 |
| d_52 | int64 | 0.0 | 59 |
| d_53 | int64 | 0.0 | 56 |
| d_54 | int64 | 0.0 | 55 |
| d_55 | int64 | 0.0 | 54 |
| d_56 | int64 | 0.0 | 60 |
| d_57 | int64 | 0.0 | 70 |
| d_58 | int64 | 0.0 | 64 |
| d_59 | int64 | 0.0 | 56 |
| d_60 | int64 | 0.0 | 49 |
| d_61 | int64 | 0.0 | 51 |
| d_62 | int64 | 0.0 | 60 |
| d_63 | int64 | 0.0 | 69 |
| d_64 | int64 | 0.0 | 72 |
| d_65 | int64 | 0.0 | 75 |
| d_66 | int64 | 0.0 | 66 |
| d_67 | int64 | 0.0 | 65 |
| d_68 | int64 | 0.0 | 62 |
| d_69 | int64 | 0.0 | 57 |
| d_70 | int64 | 0.0 | 58 |
| d_71 | int64 | 0.0 | 71 |
| d_72 | int64 | 0.0 | 74 |
| d_73 | int64 | 0.0 | 64 |
| d_74 | int64 | 0.0 | 61 |
| d_75 | int64 | 0.0 | 59 |
| d_76 | int64 | 0.0 | 58 |
| d_77 | int64 | 0.0 | 65 |
| d_78 | int64 | 0.0 | 69 |
| d_79 | int64 | 0.0 | 75 |
| d_80 | int64 | 0.0 | 62 |
| d_81 | int64 | 0.0 | 58 |
| d_82 | int64 | 0.0 | 56 |
| d_83 | int64 | 0.0 | 57 |
| d_84 | int64 | 0.0 | 68 |
| d_85 | int64 | 0.0 | 73 |
| d_86 | int64 | 0.0 | 69 |
| d_87 | int64 | 0.0 | 51 |
| d_88 | int64 | 0.0 | 52 |
| d_89 | int64 | 0.0 | 52 |
| d_90 | int64 | 0.0 | 48 |
| d_91 | int64 | 0.0 | 59 |
| d_92 | int64 | 0.0 | 70 |
| d_93 | int64 | 0.0 | 77 |
| d_94 | int64 | 0.0 | 60 |
| d_95 | int64 | 0.0 | 61 |
| d_96 | int64 | 0.0 | 53 |
| d_97 | int64 | 0.0 | 57 |
| d_98 | int64 | 0.0 | 64 |
| d_99 | int64 | 0.0 | 73 |
| d_100 | int64 | 0.0 | 67 |
| d_101 | int64 | 0.0 | 67 |
| d_102 | int64 | 0.0 | 63 |
| d_103 | int64 | 0.0 | 62 |
| d_104 | int64 | 0.0 | 63 |
| d_105 | int64 | 0.0 | 64 |
| d_106 | int64 | 0.0 | 67 |
| d_107 | int64 | 0.0 | 75 |
| d_108 | int64 | 0.0 | 59 |
| d_109 | int64 | 0.0 | 50 |
| d_110 | int64 | 0.0 | 47 |
| d_111 | int64 | 0.0 | 51 |
| d_112 | int64 | 0.0 | 60 |
| d_113 | int64 | 0.0 | 66 |
| d_114 | int64 | 0.0 | 65 |
| d_115 | int64 | 0.0 | 58 |
| d_116 | int64 | 0.0 | 55 |
| d_117 | int64 | 0.0 | 54 |
| d_118 | int64 | 0.0 | 57 |
| d_119 | int64 | 0.0 | 60 |
| d_120 | int64 | 0.0 | 63 |
| d_121 | int64 | 0.0 | 64 |
| d_122 | int64 | 0.0 | 62 |
| d_123 | int64 | 0.0 | 56 |
| d_124 | int64 | 0.0 | 64 |
| d_125 | int64 | 0.0 | 57 |
| d_126 | int64 | 0.0 | 66 |
| d_127 | int64 | 0.0 | 76 |
| d_128 | int64 | 0.0 | 79 |
| d_129 | int64 | 0.0 | 69 |
| d_130 | int64 | 0.0 | 66 |
| d_131 | int64 | 0.0 | 64 |
| d_132 | int64 | 0.0 | 65 |
| d_133 | int64 | 0.0 | 67 |
| d_134 | int64 | 0.0 | 73 |
| d_135 | int64 | 0.0 | 80 |
| d_136 | int64 | 0.0 | 67 |
| d_137 | int64 | 0.0 | 67 |
| d_138 | int64 | 0.0 | 65 |
| d_139 | int64 | 0.0 | 58 |
| d_140 | int64 | 0.0 | 65 |
| d_141 | int64 | 0.0 | 77 |
| d_142 | int64 | 0.0 | 69 |
| d_143 | int64 | 0.0 | 66 |
| d_144 | int64 | 0.0 | 68 |
| d_145 | int64 | 0.0 | 55 |
| d_146 | int64 | 0.0 | 61 |
| d_147 | int64 | 0.0 | 66 |
| d_148 | int64 | 0.0 | 65 |
| d_149 | int64 | 0.0 | 68 |
| d_150 | int64 | 0.0 | 61 |
| d_151 | int64 | 0.0 | 57 |
| d_152 | int64 | 0.0 | 58 |
| d_153 | int64 | 0.0 | 59 |
| d_154 | int64 | 0.0 | 78 |
| d_155 | int64 | 0.0 | 85 |
| d_156 | int64 | 0.0 | 80 |
| d_157 | int64 | 0.0 | 69 |
| d_158 | int64 | 0.0 | 69 |
| d_159 | int64 | 0.0 | 65 |
| d_160 | int64 | 0.0 | 65 |
| d_161 | int64 | 0.0 | 67 |
| d_162 | int64 | 0.0 | 76 |
| d_163 | int64 | 0.0 | 74 |
| d_164 | int64 | 0.0 | 68 |
| d_165 | int64 | 0.0 | 63 |
| d_166 | int64 | 0.0 | 57 |
| d_167 | int64 | 0.0 | 63 |
| d_168 | int64 | 0.0 | 66 |
| d_169 | int64 | 0.0 | 73 |
| d_170 | int64 | 0.0 | 74 |
| d_171 | int64 | 0.0 | 66 |
| d_172 | int64 | 0.0 | 57 |
| d_173 | int64 | 0.0 | 60 |
| d_174 | int64 | 0.0 | 61 |
| d_175 | int64 | 0.0 | 67 |
| d_176 | int64 | 0.0 | 75 |
| d_177 | int64 | 0.0 | 72 |
| d_178 | int64 | 0.0 | 58 |
| d_179 | int64 | 0.0 | 54 |
| d_180 | int64 | 0.0 | 55 |
| d_181 | int64 | 0.0 | 52 |
| d_182 | int64 | 0.0 | 61 |
| d_183 | int64 | 0.0 | 66 |
| d_184 | int64 | 0.0 | 69 |
| d_185 | int64 | 0.0 | 65 |
| d_186 | int64 | 0.0 | 67 |
| d_187 | int64 | 0.0 | 74 |
| d_188 | int64 | 0.0 | 63 |
| d_189 | int64 | 0.0 | 73 |
| d_190 | int64 | 0.0 | 78 |
| d_191 | int64 | 0.0 | 78 |
| d_192 | int64 | 0.0 | 72 |
| d_193 | int64 | 0.0 | 67 |
| d_194 | int64 | 0.0 | 69 |
| d_195 | int64 | 0.0 | 63 |
| d_196 | int64 | 0.0 | 72 |
| d_197 | int64 | 0.0 | 77 |
| d_198 | int64 | 0.0 | 85 |
| d_199 | int64 | 0.0 | 78 |
| d_200 | int64 | 0.0 | 69 |
| d_201 | int64 | 0.0 | 59 |
| d_202 | int64 | 0.0 | 58 |
| d_203 | int64 | 0.0 | 71 |
| d_204 | int64 | 0.0 | 80 |
| d_205 | int64 | 0.0 | 78 |
| d_206 | int64 | 0.0 | 63 |
| d_207 | int64 | 0.0 | 58 |
| d_208 | int64 | 0.0 | 59 |
| d_209 | int64 | 0.0 | 51 |
| d_210 | int64 | 0.0 | 61 |
| d_211 | int64 | 0.0 | 69 |
| d_212 | int64 | 0.0 | 73 |
| d_213 | int64 | 0.0 | 54 |
| d_214 | int64 | 0.0 | 56 |
| d_215 | int64 | 0.0 | 60 |
| d_216 | int64 | 0.0 | 66 |
| d_217 | int64 | 0.0 | 73 |
| d_218 | int64 | 0.0 | 80 |
| d_219 | int64 | 0.0 | 64 |
| d_220 | int64 | 0.0 | 71 |
| d_221 | int64 | 0.0 | 66 |
| d_222 | int64 | 0.0 | 59 |
| d_223 | int64 | 0.0 | 59 |
| d_224 | int64 | 0.0 | 69 |
| d_225 | int64 | 0.0 | 75 |
| d_226 | int64 | 0.0 | 77 |
| d_227 | int64 | 0.0 | 65 |
| d_228 | int64 | 0.0 | 62 |
| d_229 | int64 | 0.0 | 60 |
| d_230 | int64 | 0.0 | 63 |
| d_231 | int64 | 0.0 | 61 |
| d_232 | int64 | 0.0 | 68 |
| d_233 | int64 | 0.0 | 66 |
| d_234 | int64 | 0.0 | 59 |
| d_235 | int64 | 0.0 | 56 |
| d_236 | int64 | 0.0 | 61 |
| d_237 | int64 | 0.0 | 53 |
| d_238 | int64 | 0.0 | 64 |
| d_239 | int64 | 0.0 | 75 |
| d_240 | int64 | 0.0 | 81 |
| d_241 | int64 | 0.0 | 63 |
| d_242 | int64 | 0.0 | 62 |
| d_243 | int64 | 0.0 | 59 |
| d_244 | int64 | 0.0 | 61 |
| d_245 | int64 | 0.0 | 73 |
| d_246 | int64 | 0.0 | 85 |
| d_247 | int64 | 0.0 | 81 |
| d_248 | int64 | 0.0 | 76 |
| d_249 | int64 | 0.0 | 71 |
| d_250 | int64 | 0.0 | 71 |
| d_251 | int64 | 0.0 | 68 |
| d_252 | int64 | 0.0 | 74 |
| d_253 | int64 | 0.0 | 84 |
| d_254 | int64 | 0.0 | 82 |
| d_255 | int64 | 0.0 | 69 |
| d_256 | int64 | 0.0 | 70 |
| d_257 | int64 | 0.0 | 68 |
| d_258 | int64 | 0.0 | 67 |
| d_259 | int64 | 0.0 | 72 |
| d_260 | int64 | 0.0 | 82 |
| d_261 | int64 | 0.0 | 79 |
| d_262 | int64 | 0.0 | 64 |
| d_263 | int64 | 0.0 | 62 |
| d_264 | int64 | 0.0 | 58 |
| d_265 | int64 | 0.0 | 62 |
| d_266 | int64 | 0.0 | 71 |
| d_267 | int64 | 0.0 | 74 |
| d_268 | int64 | 0.0 | 72 |
| d_269 | int64 | 0.0 | 60 |
| d_270 | int64 | 0.0 | 60 |
| d_271 | int64 | 0.0 | 59 |
| d_272 | int64 | 0.0 | 62 |
| d_273 | int64 | 0.0 | 72 |
| d_274 | int64 | 0.0 | 76 |
| d_275 | int64 | 0.0 | 75 |
| d_276 | int64 | 0.0 | 59 |
| d_277 | int64 | 0.0 | 67 |
| d_278 | int64 | 0.0 | 64 |
| d_279 | int64 | 0.0 | 69 |
| d_280 | int64 | 0.0 | 70 |
| d_281 | int64 | 0.0 | 86 |
| d_282 | int64 | 0.0 | 86 |
| d_283 | int64 | 0.0 | 68 |
| d_284 | int64 | 0.0 | 69 |
| d_285 | int64 | 0.0 | 68 |
| d_286 | int64 | 0.0 | 68 |
| d_287 | int64 | 0.0 | 72 |
| d_288 | int64 | 0.0 | 83 |
| d_289 | int64 | 0.0 | 77 |
| d_290 | int64 | 0.0 | 66 |
| d_291 | int64 | 0.0 | 64 |
| d_292 | int64 | 0.0 | 59 |
| d_293 | int64 | 0.0 | 59 |
| d_294 | int64 | 0.0 | 69 |
| d_295 | int64 | 0.0 | 82 |
| d_296 | int64 | 0.0 | 76 |
| d_297 | int64 | 0.0 | 67 |
| d_298 | int64 | 0.0 | 73 |
| d_299 | int64 | 0.0 | 88 |
| d_300 | int64 | 0.0 | 78 |
| d_301 | int64 | 0.0 | 81 |
| d_302 | int64 | 0.0 | 66 |
| d_303 | int64 | 0.0 | 65 |
| d_304 | int64 | 0.0 | 57 |
| d_305 | int64 | 0.0 | 56 |
| d_306 | int64 | 0.0 | 53 |
| d_307 | int64 | 0.0 | 64 |
| d_308 | int64 | 0.0 | 76 |
| d_309 | int64 | 0.0 | 85 |
| d_310 | int64 | 0.0 | 80 |
| d_311 | int64 | 0.0 | 68 |
| d_312 | int64 | 0.0 | 68 |
| d_313 | int64 | 0.0 | 64 |
| d_314 | int64 | 0.0 | 67 |
| d_315 | int64 | 0.0 | 70 |
| d_316 | int64 | 0.0 | 75 |
| d_317 | int64 | 0.0 | 81 |
| d_318 | int64 | 0.0 | 70 |
| d_319 | int64 | 0.0 | 63 |
| d_320 | int64 | 0.0 | 71 |
| d_321 | int64 | 0.0 | 72 |
| d_322 | int64 | 0.0 | 73 |
| d_323 | int64 | 0.0 | 83 |
| d_324 | int64 | 0.0 | 74 |
| d_325 | int64 | 0.0 | 68 |
| d_326 | int64 | 0.0 | 65 |
| d_327 | int64 | 0.0 | 68 |
| d_328 | int64 | 0.0 | 70 |
| d_329 | int64 | 0.0 | 86 |
| d_330 | int64 | 0.0 | 84 |
| d_331 | int64 | 0.0 | 3 |
| d_332 | int64 | 0.0 | 66 |
| d_333 | int64 | 0.0 | 60 |
| d_334 | int64 | 0.0 | 59 |
| d_335 | int64 | 0.0 | 59 |
| d_336 | int64 | 0.0 | 77 |
| d_337 | int64 | 0.0 | 84 |
| d_338 | int64 | 0.0 | 58 |
| d_339 | int64 | 0.0 | 72 |
| d_340 | int64 | 0.0 | 68 |
| d_341 | int64 | 0.0 | 65 |
| d_342 | int64 | 0.0 | 70 |
| d_343 | int64 | 0.0 | 70 |
| d_344 | int64 | 0.0 | 81 |
| d_345 | int64 | 0.0 | 77 |
| d_346 | int64 | 0.0 | 68 |
| d_347 | int64 | 0.0 | 67 |
| d_348 | int64 | 0.0 | 68 |
| d_349 | int64 | 0.0 | 57 |
| d_350 | int64 | 0.0 | 69 |
| d_351 | int64 | 0.0 | 83 |
| d_352 | int64 | 0.0 | 80 |
| d_353 | int64 | 0.0 | 65 |
| d_354 | int64 | 0.0 | 56 |
| d_355 | int64 | 0.0 | 59 |
| d_356 | int64 | 0.0 | 56 |
| d_357 | int64 | 0.0 | 66 |
| d_358 | int64 | 0.0 | 78 |
| d_359 | int64 | 0.0 | 71 |
| d_360 | int64 | 0.0 | 57 |
| d_361 | int64 | 0.0 | 52 |
| d_362 | int64 | 0.0 | 55 |
| d_363 | int64 | 0.0 | 54 |
| d_364 | int64 | 0.0 | 67 |
| d_365 | int64 | 0.0 | 73 |
| d_366 | int64 | 0.0 | 73 |
| d_367 | int64 | 0.0 | 54 |
| d_368 | int64 | 0.0 | 59 |
| d_369 | int64 | 0.0 | 68 |
| d_370 | int64 | 0.0 | 68 |
| d_371 | int64 | 0.0 | 79 |
| d_372 | int64 | 0.0 | 85 |
| d_373 | int64 | 0.0 | 83 |
| d_374 | int64 | 0.0 | 70 |
| d_375 | int64 | 0.0 | 65 |
| d_376 | int64 | 0.0 | 67 |
| d_377 | int64 | 0.0 | 75 |
| d_378 | int64 | 0.0 | 70 |
| d_379 | int64 | 0.0 | 88 |
| d_380 | int64 | 0.0 | 90 |
| d_381 | int64 | 0.0 | 71 |
| d_382 | int64 | 0.0 | 63 |
| d_383 | int64 | 0.0 | 64 |
| d_384 | int64 | 0.0 | 54 |
| d_385 | int64 | 0.0 | 61 |
| d_386 | int64 | 0.0 | 78 |
| d_387 | int64 | 0.0 | 81 |
| d_388 | int64 | 0.0 | 66 |
| d_389 | int64 | 0.0 | 64 |
| d_390 | int64 | 0.0 | 56 |
| d_391 | int64 | 0.0 | 61 |
| d_392 | int64 | 0.0 | 72 |
| d_393 | int64 | 0.0 | 80 |
| d_394 | int64 | 0.0 | 83 |
| d_395 | int64 | 0.0 | 70 |
| d_396 | int64 | 0.0 | 59 |
| d_397 | int64 | 0.0 | 60 |
| d_398 | int64 | 0.0 | 69 |
| d_399 | int64 | 0.0 | 73 |
| d_400 | int64 | 0.0 | 88 |
| d_401 | int64 | 0.0 | 86 |
| d_402 | int64 | 0.0 | 76 |
| d_403 | int64 | 0.0 | 77 |
| d_404 | int64 | 0.0 | 69 |
| d_405 | int64 | 0.0 | 69 |
| d_406 | int64 | 0.0 | 73 |
| d_407 | int64 | 0.0 | 78 |
| d_408 | int64 | 0.0 | 90 |
| d_409 | int64 | 0.0 | 71 |
| d_410 | int64 | 0.0 | 69 |
| d_411 | int64 | 0.0 | 68 |
| d_412 | int64 | 0.0 | 72 |
| d_413 | int64 | 0.0 | 72 |
| d_414 | int64 | 0.0 | 81 |
| d_415 | int64 | 0.0 | 80 |
| d_416 | int64 | 0.0 | 65 |
| d_417 | int64 | 0.0 | 64 |
| d_418 | int64 | 0.0 | 61 |
| d_419 | int64 | 0.0 | 62 |
| d_420 | int64 | 0.0 | 68 |
| d_421 | int64 | 0.0 | 80 |
| d_422 | int64 | 0.0 | 85 |
| d_423 | int64 | 0.0 | 64 |
| d_424 | int64 | 0.0 | 59 |
| d_425 | int64 | 0.0 | 56 |
| d_426 | int64 | 0.0 | 48 |
| d_427 | int64 | 0.0 | 71 |
| d_428 | int64 | 0.0 | 77 |
| d_429 | int64 | 0.0 | 82 |
| d_430 | int64 | 0.0 | 74 |
| d_431 | int64 | 0.0 | 75 |
| d_432 | int64 | 0.0 | 68 |
| d_433 | int64 | 0.0 | 74 |
| d_434 | int64 | 0.0 | 84 |
| d_435 | int64 | 0.0 | 100 |
| d_436 | int64 | 0.0 | 91 |
| d_437 | int64 | 0.0 | 73 |
| d_438 | int64 | 0.0 | 66 |
| d_439 | int64 | 0.0 | 68 |
| d_440 | int64 | 0.0 | 65 |
| d_441 | int64 | 0.0 | 72 |
| d_442 | int64 | 0.0 | 84 |
| d_443 | int64 | 0.0 | 85 |
| d_444 | int64 | 0.0 | 62 |
| d_445 | int64 | 0.0 | 62 |
| d_446 | int64 | 0.0 | 60 |
| d_447 | int64 | 0.0 | 61 |
| d_448 | int64 | 0.0 | 66 |
| d_449 | int64 | 0.0 | 85 |
| d_450 | int64 | 0.0 | 83 |
| d_451 | int64 | 0.0 | 65 |
| d_452 | int64 | 0.0 | 61 |
| d_453 | int64 | 0.0 | 58 |
| d_454 | int64 | 0.0 | 62 |
| d_455 | int64 | 0.0 | 64 |
| d_456 | int64 | 0.0 | 76 |
| d_457 | int64 | 0.0 | 77 |
| d_458 | int64 | 0.0 | 64 |
| d_459 | int64 | 0.0 | 66 |
| d_460 | int64 | 0.0 | 69 |
| d_461 | int64 | 0.0 | 76 |
| d_462 | int64 | 0.0 | 74 |
| d_463 | int64 | 0.0 | 87 |
| d_464 | int64 | 0.0 | 87 |
| d_465 | int64 | 0.0 | 78 |
| d_466 | int64 | 0.0 | 71 |
| d_467 | int64 | 0.0 | 68 |
| d_468 | int64 | 0.0 | 73 |
| d_469 | int64 | 0.0 | 79 |
| d_470 | int64 | 0.0 | 93 |
| d_471 | int64 | 0.0 | 83 |
| d_472 | int64 | 0.0 | 76 |
| d_473 | int64 | 0.0 | 76 |
| d_474 | int64 | 0.0 | 71 |
| d_475 | int64 | 0.0 | 64 |
| d_476 | int64 | 0.0 | 81 |
| d_477 | int64 | 0.0 | 86 |
| d_478 | int64 | 0.0 | 86 |
| d_479 | int64 | 0.0 | 62 |
| d_480 | int64 | 0.0 | 68 |
| d_481 | int64 | 0.0 | 62 |
| d_482 | int64 | 0.0 | 66 |
| d_483 | int64 | 0.0 | 80 |
| d_484 | int64 | 0.0 | 83 |
| d_485 | int64 | 0.0 | 82 |
| d_486 | int64 | 0.0 | 80 |
| d_487 | int64 | 0.0 | 69 |
| d_488 | int64 | 0.0 | 63 |
| d_489 | int64 | 0.0 | 66 |
| d_490 | int64 | 0.0 | 80 |
| d_491 | int64 | 0.0 | 92 |
| d_492 | int64 | 0.0 | 90 |
| d_493 | int64 | 0.0 | 75 |
| d_494 | int64 | 0.0 | 72 |
| d_495 | int64 | 0.0 | 79 |
| d_496 | int64 | 0.0 | 71 |
| d_497 | int64 | 0.0 | 79 |
| d_498 | int64 | 0.0 | 91 |
| d_499 | int64 | 0.0 | 98 |
| d_500 | int64 | 0.0 | 85 |
| d_501 | int64 | 0.0 | 77 |
| d_502 | int64 | 0.0 | 67 |
| d_503 | int64 | 0.0 | 75 |
| d_504 | int64 | 0.0 | 93 |
| d_505 | int64 | 0.0 | 94 |
| d_506 | int64 | 0.0 | 94 |
| d_507 | int64 | 0.0 | 73 |
| d_508 | int64 | 0.0 | 71 |
| d_509 | int64 | 0.0 | 68 |
| d_510 | int64 | 0.0 | 69 |
| d_511 | int64 | 0.0 | 85 |
| d_512 | int64 | 0.0 | 86 |
| d_513 | int64 | 0.0 | 90 |
| d_514 | int64 | 0.0 | 73 |
| d_515 | int64 | 0.0 | 70 |
| d_516 | int64 | 0.0 | 67 |
| d_517 | int64 | 0.0 | 70 |
| d_518 | int64 | 0.0 | 83 |
| d_519 | int64 | 0.0 | 88 |
| d_520 | int64 | 0.0 | 81 |
| d_521 | int64 | 0.0 | 80 |
| d_522 | int64 | 0.0 | 91 |
| d_523 | int64 | 0.0 | 77 |
| d_524 | int64 | 0.0 | 78 |
| d_525 | int64 | 0.0 | 91 |
| d_526 | int64 | 0.0 | 91 |
| d_527 | int64 | 0.0 | 87 |
| d_528 | int64 | 0.0 | 75 |
| d_529 | int64 | 0.0 | 68 |
| d_530 | int64 | 0.0 | 77 |
| d_531 | int64 | 0.0 | 73 |
| d_532 | int64 | 0.0 | 76 |
| d_533 | int64 | 0.0 | 88 |
| d_534 | int64 | 0.0 | 92 |
| d_535 | int64 | 0.0 | 76 |
| d_536 | int64 | 0.0 | 74 |
| d_537 | int64 | 0.0 | 67 |
| d_538 | int64 | 0.0 | 66 |
| d_539 | int64 | 0.0 | 73 |
| d_540 | int64 | 0.0 | 86 |
| d_541 | int64 | 0.0 | 85 |
| d_542 | int64 | 0.0 | 70 |
| d_543 | int64 | 0.0 | 66 |
| d_544 | int64 | 0.0 | 67 |
| d_545 | int64 | 0.0 | 66 |
| d_546 | int64 | 0.0 | 72 |
| d_547 | int64 | 0.0 | 77 |
| d_548 | int64 | 0.0 | 76 |
| d_549 | int64 | 0.0 | 65 |
| d_550 | int64 | 0.0 | 68 |
| d_551 | int64 | 0.0 | 75 |
| d_552 | int64 | 0.0 | 81 |
| d_553 | int64 | 0.0 | 87 |
| d_554 | int64 | 0.0 | 84 |
| d_555 | int64 | 0.0 | 90 |
| d_556 | int64 | 0.0 | 83 |
| d_557 | int64 | 0.0 | 74 |
| d_558 | int64 | 0.0 | 78 |
| d_559 | int64 | 0.0 | 80 |
| d_560 | int64 | 0.0 | 84 |
| d_561 | int64 | 0.0 | 95 |
| d_562 | int64 | 0.0 | 94 |
| d_563 | int64 | 0.0 | 80 |
| d_564 | int64 | 0.0 | 76 |
| d_565 | int64 | 0.0 | 76 |
| d_566 | int64 | 0.0 | 75 |
| d_567 | int64 | 0.0 | 77 |
| d_568 | int64 | 0.0 | 81 |
| d_569 | int64 | 0.0 | 86 |
| d_570 | int64 | 0.0 | 69 |
| d_571 | int64 | 0.0 | 67 |
| d_572 | int64 | 0.0 | 59 |
| d_573 | int64 | 0.0 | 59 |
| d_574 | int64 | 0.0 | 72 |
| d_575 | int64 | 0.0 | 82 |
| d_576 | int64 | 0.0 | 82 |
| d_577 | int64 | 0.0 | 69 |
| d_578 | int64 | 0.0 | 69 |
| d_579 | int64 | 0.0 | 63 |
| d_580 | int64 | 0.0 | 68 |
| d_581 | int64 | 0.0 | 78 |
| d_582 | int64 | 0.0 | 84 |
| d_583 | int64 | 0.0 | 93 |
| d_584 | int64 | 0.0 | 93 |
| d_585 | int64 | 0.0 | 75 |
| d_586 | int64 | 0.0 | 70 |
| d_587 | int64 | 0.0 | 73 |
| d_588 | int64 | 0.0 | 73 |
| d_589 | int64 | 0.0 | 83 |
| d_590 | int64 | 0.0 | 88 |
| d_591 | int64 | 0.0 | 72 |
| d_592 | int64 | 0.0 | 69 |
| d_593 | int64 | 0.0 | 72 |
| d_594 | int64 | 0.0 | 67 |
| d_595 | int64 | 0.0 | 80 |
| d_596 | int64 | 0.0 | 91 |
| d_597 | int64 | 0.0 | 81 |
| d_598 | int64 | 0.0 | 61 |
| d_599 | int64 | 0.0 | 59 |
| d_600 | int64 | 0.0 | 56 |
| d_601 | int64 | 0.0 | 62 |
| d_602 | int64 | 0.0 | 67 |
| d_603 | int64 | 0.0 | 83 |
| d_604 | int64 | 0.0 | 80 |
| d_605 | int64 | 0.0 | 63 |
| d_606 | int64 | 0.0 | 62 |
| d_607 | int64 | 0.0 | 60 |
| d_608 | int64 | 0.0 | 55 |
| d_609 | int64 | 0.0 | 68 |
| d_610 | int64 | 0.0 | 83 |
| d_611 | int64 | 0.0 | 84 |
| d_612 | int64 | 0.0 | 73 |
| d_613 | int64 | 0.0 | 79 |
| d_614 | int64 | 0.0 | 70 |
| d_615 | int64 | 0.0 | 66 |
| d_616 | int64 | 0.0 | 70 |
| d_617 | int64 | 0.0 | 84 |
| d_618 | int64 | 0.0 | 76 |
| d_619 | int64 | 0.0 | 75 |
| d_620 | int64 | 0.0 | 70 |
| d_621 | int64 | 0.0 | 67 |
| d_622 | int64 | 0.0 | 67 |
| d_623 | int64 | 0.0 | 73 |
| d_624 | int64 | 0.0 | 79 |
| d_625 | int64 | 0.0 | 86 |
| d_626 | int64 | 0.0 | 72 |
| d_627 | int64 | 0.0 | 60 |
| d_628 | int64 | 0.0 | 59 |
| d_629 | int64 | 0.0 | 61 |
| d_630 | int64 | 0.0 | 62 |
| d_631 | int64 | 0.0 | 69 |
| d_632 | int64 | 0.0 | 73 |
| d_633 | int64 | 0.0 | 58 |
| d_634 | int64 | 0.0 | 58 |
| d_635 | int64 | 0.0 | 61 |
| d_636 | int64 | 0.0 | 53 |
| d_637 | int64 | 0.0 | 63 |
| d_638 | int64 | 0.0 | 75 |
| d_639 | int64 | 0.0 | 73 |
| d_640 | int64 | 0.0 | 58 |
| d_641 | int64 | 0.0 | 59 |
| d_642 | int64 | 0.0 | 61 |
| d_643 | int64 | 0.0 | 68 |
| d_644 | int64 | 0.0 | 69 |
| d_645 | int64 | 0.0 | 86 |
| d_646 | int64 | 0.0 | 83 |
| d_647 | int64 | 0.0 | 67 |
| d_648 | int64 | 0.0 | 66 |
| d_649 | int64 | 0.0 | 61 |
| d_650 | int64 | 0.0 | 62 |
| d_651 | int64 | 0.0 | 68 |
| d_652 | int64 | 0.0 | 80 |
| d_653 | int64 | 0.0 | 80 |
| d_654 | int64 | 0.0 | 64 |
| d_655 | int64 | 0.0 | 59 |
| d_656 | int64 | 0.0 | 64 |
| d_657 | int64 | 0.0 | 63 |
| d_658 | int64 | 0.0 | 65 |
| d_659 | int64 | 0.0 | 78 |
| d_660 | int64 | 0.0 | 76 |
| d_661 | int64 | 0.0 | 60 |
| d_662 | int64 | 0.0 | 70 |
| d_663 | int64 | 0.0 | 84 |
| d_664 | int64 | 0.0 | 81 |
| d_665 | int64 | 0.0 | 71 |
| d_666 | int64 | 0.0 | 66 |
| d_667 | int64 | 0.0 | 62 |
| d_668 | int64 | 0.0 | 52 |
| d_669 | int64 | 0.0 | 50 |
| d_670 | int64 | 0.0 | 53 |
| d_671 | int64 | 0.0 | 53 |
| d_672 | int64 | 0.0 | 65 |
| d_673 | int64 | 0.0 | 77 |
| d_674 | int64 | 0.0 | 78 |
| d_675 | int64 | 0.0 | 72 |
| d_676 | int64 | 0.0 | 59 |
| d_677 | int64 | 0.0 | 68 |
| d_678 | int64 | 0.0 | 65 |
| d_679 | int64 | 0.0 | 65 |
| d_680 | int64 | 0.0 | 79 |
| d_681 | int64 | 0.0 | 77 |
| d_682 | int64 | 0.0 | 65 |
| d_683 | int64 | 0.0 | 64 |
| d_684 | int64 | 0.0 | 66 |
| d_685 | int64 | 0.0 | 63 |
| d_686 | int64 | 0.0 | 71 |
| d_687 | int64 | 0.0 | 83 |
| d_688 | int64 | 0.0 | 82 |
| d_689 | int64 | 0.0 | 63 |
| d_690 | int64 | 0.0 | 61 |
| d_691 | int64 | 0.0 | 70 |
| d_692 | int64 | 0.0 | 68 |
| d_693 | int64 | 0.0 | 75 |
| d_694 | int64 | 0.0 | 85 |
| d_695 | int64 | 0.0 | 87 |
| d_696 | int64 | 0.0 | 88 |
| d_697 | int64 | 0.0 | 2 |
| d_698 | int64 | 0.0 | 67 |
| d_699 | int64 | 0.0 | 62 |
| d_700 | int64 | 0.0 | 65 |
| d_701 | int64 | 0.0 | 72 |
| d_702 | int64 | 0.0 | 74 |
| d_703 | int64 | 0.0 | 82 |
| d_704 | int64 | 0.0 | 58 |
| d_705 | int64 | 0.0 | 68 |
| d_706 | int64 | 0.0 | 75 |
| d_707 | int64 | 0.0 | 66 |
| d_708 | int64 | 0.0 | 85 |
| d_709 | int64 | 0.0 | 82 |
| d_710 | int64 | 0.0 | 68 |
| d_711 | int64 | 0.0 | 69 |
| d_712 | int64 | 0.0 | 63 |
| d_713 | int64 | 0.0 | 64 |
| d_714 | int64 | 0.0 | 65 |
| d_715 | int64 | 0.0 | 91 |
| d_716 | int64 | 0.0 | 78 |
| d_717 | int64 | 0.0 | 66 |
| d_718 | int64 | 0.0 | 67 |
| d_719 | int64 | 0.0 | 57 |
| d_720 | int64 | 0.0 | 56 |
| d_721 | int64 | 0.0 | 63 |
| d_722 | int64 | 0.0 | 76 |
| d_723 | int64 | 0.0 | 71 |
| d_724 | int64 | 0.0 | 59 |
| d_725 | int64 | 0.0 | 56 |
| d_726 | int64 | 0.0 | 51 |
| d_727 | int64 | 0.0 | 52 |
| d_728 | int64 | 0.0 | 56 |
| d_729 | int64 | 0.0 | 72 |
| d_730 | int64 | 0.0 | 70 |
| d_731 | int64 | 0.0 | 54 |
| d_732 | int64 | 0.0 | 58 |
| d_733 | int64 | 0.0 | 49 |
| d_734 | int64 | 0.0 | 54 |
| d_735 | int64 | 0.0 | 68 |
| d_736 | int64 | 0.0 | 87 |
| d_737 | int64 | 0.0 | 82 |
| d_738 | int64 | 0.0 | 62 |
| d_739 | int64 | 0.0 | 64 |
| d_740 | int64 | 0.0 | 67 |
| d_741 | int64 | 0.0 | 64 |
| d_742 | int64 | 0.0 | 74 |
| d_743 | int64 | 0.0 | 83 |
| d_744 | int64 | 0.0 | 73 |
| d_745 | int64 | 0.0 | 74 |
| d_746 | int64 | 0.0 | 72 |
| d_747 | int64 | 0.0 | 85 |
| d_748 | int64 | 0.0 | 68 |
| d_749 | int64 | 0.0 | 74 |
| d_750 | int64 | 0.0 | 81 |
| d_751 | int64 | 0.0 | 83 |
| d_752 | int64 | 0.0 | 66 |
| d_753 | int64 | 0.0 | 62 |
| d_754 | int64 | 0.0 | 61 |
| d_755 | int64 | 0.0 | 67 |
| d_756 | int64 | 0.0 | 68 |
| d_757 | int64 | 0.0 | 79 |
| d_758 | int64 | 0.0 | 78 |
| d_759 | int64 | 0.0 | 60 |
| d_760 | int64 | 0.0 | 55 |
| d_761 | int64 | 0.0 | 59 |
| d_762 | int64 | 0.0 | 59 |
| d_763 | int64 | 0.0 | 74 |
| d_764 | int64 | 0.0 | 87 |
| d_765 | int64 | 0.0 | 92 |
| d_766 | int64 | 0.0 | 72 |
| d_767 | int64 | 0.0 | 67 |
| d_768 | int64 | 0.0 | 65 |
| d_769 | int64 | 0.0 | 64 |
| d_770 | int64 | 0.0 | 68 |
| d_771 | int64 | 0.0 | 89 |
| d_772 | int64 | 0.0 | 80 |
| d_773 | int64 | 0.0 | 68 |
| d_774 | int64 | 0.0 | 67 |
| d_775 | int64 | 0.0 | 62 |
| d_776 | int64 | 0.0 | 67 |
| d_777 | int64 | 0.0 | 74 |
| d_778 | int64 | 0.0 | 81 |
| d_779 | int64 | 0.0 | 77 |
| d_780 | int64 | 0.0 | 64 |
| d_781 | int64 | 0.0 | 59 |
| d_782 | int64 | 0.0 | 58 |
| d_783 | int64 | 0.0 | 58 |
| d_784 | int64 | 0.0 | 65 |
| d_785 | int64 | 0.0 | 74 |
| d_786 | int64 | 0.0 | 73 |
| d_787 | int64 | 0.0 | 59 |
| d_788 | int64 | 0.0 | 63 |
| d_789 | int64 | 0.0 | 60 |
| d_790 | int64 | 0.0 | 63 |
| d_791 | int64 | 0.0 | 73 |
| d_792 | int64 | 0.0 | 91 |
| d_793 | int64 | 0.0 | 72 |
| d_794 | int64 | 0.0 | 69 |
| d_795 | int64 | 0.0 | 68 |
| d_796 | int64 | 0.0 | 70 |
| d_797 | int64 | 0.0 | 63 |
| d_798 | int64 | 0.0 | 69 |
| d_799 | int64 | 0.0 | 79 |
| d_800 | int64 | 0.0 | 84 |
| d_801 | int64 | 0.0 | 66 |
| d_802 | int64 | 0.0 | 69 |
| d_803 | int64 | 0.0 | 63 |
| d_804 | int64 | 0.0 | 66 |
| d_805 | int64 | 0.0 | 72 |
| d_806 | int64 | 0.0 | 78 |
| d_807 | int64 | 0.0 | 80 |
| d_808 | int64 | 0.0 | 69 |
| d_809 | int64 | 0.0 | 64 |
| d_810 | int64 | 0.0 | 56 |
| d_811 | int64 | 0.0 | 54 |
| d_812 | int64 | 0.0 | 64 |
| d_813 | int64 | 0.0 | 70 |
| d_814 | int64 | 0.0 | 74 |
| d_815 | int64 | 0.0 | 62 |
| d_816 | int64 | 0.0 | 61 |
| d_817 | int64 | 0.0 | 57 |
| d_818 | int64 | 0.0 | 58 |
| d_819 | int64 | 0.0 | 60 |
| d_820 | int64 | 0.0 | 62 |
| d_821 | int64 | 0.0 | 73 |
| d_822 | int64 | 0.0 | 55 |
| d_823 | int64 | 0.0 | 60 |
| d_824 | int64 | 0.0 | 65 |
| d_825 | int64 | 0.0 | 66 |
| d_826 | int64 | 0.0 | 72 |
| d_827 | int64 | 0.0 | 80 |
| d_828 | int64 | 0.0 | 72 |
| d_829 | int64 | 0.0 | 67 |
| d_830 | int64 | 0.0 | 64 |
| d_831 | int64 | 0.0 | 64 |
| d_832 | int64 | 0.0 | 65 |
| d_833 | int64 | 0.0 | 62 |
| d_834 | int64 | 0.0 | 85 |
| d_835 | int64 | 0.0 | 78 |
| d_836 | int64 | 0.0 | 71 |
| d_837 | int64 | 0.0 | 64 |
| d_838 | int64 | 0.0 | 68 |
| d_839 | int64 | 0.0 | 58 |
| d_840 | int64 | 0.0 | 63 |
| d_841 | int64 | 0.0 | 75 |
| d_842 | int64 | 0.0 | 83 |
| d_843 | int64 | 0.0 | 68 |
| d_844 | int64 | 0.0 | 61 |
| d_845 | int64 | 0.0 | 56 |
| d_846 | int64 | 0.0 | 59 |
| d_847 | int64 | 0.0 | 63 |
| d_848 | int64 | 0.0 | 78 |
| d_849 | int64 | 0.0 | 72 |
| d_850 | int64 | 0.0 | 72 |
| d_851 | int64 | 0.0 | 61 |
| d_852 | int64 | 0.0 | 54 |
| d_853 | int64 | 0.0 | 59 |
| d_854 | int64 | 0.0 | 68 |
| d_855 | int64 | 0.0 | 78 |
| d_856 | int64 | 0.0 | 87 |
| d_857 | int64 | 0.0 | 72 |
| d_858 | int64 | 0.0 | 66 |
| d_859 | int64 | 0.0 | 71 |
| d_860 | int64 | 0.0 | 65 |
| d_861 | int64 | 0.0 | 68 |
| d_862 | int64 | 0.0 | 81 |
| d_863 | int64 | 0.0 | 83 |
| d_864 | int64 | 0.0 | 71 |
| d_865 | int64 | 0.0 | 67 |
| d_866 | int64 | 0.0 | 66 |
| d_867 | int64 | 0.0 | 69 |
| d_868 | int64 | 0.0 | 75 |
| d_869 | int64 | 0.0 | 83 |
| d_870 | int64 | 0.0 | 81 |
| d_871 | int64 | 0.0 | 69 |
| d_872 | int64 | 0.0 | 63 |
| d_873 | int64 | 0.0 | 61 |
| d_874 | int64 | 0.0 | 63 |
| d_875 | int64 | 0.0 | 69 |
| d_876 | int64 | 0.0 | 79 |
| d_877 | int64 | 0.0 | 81 |
| d_878 | int64 | 0.0 | 64 |
| d_879 | int64 | 0.0 | 65 |
| d_880 | int64 | 0.0 | 64 |
| d_881 | int64 | 0.0 | 68 |
| d_882 | int64 | 0.0 | 77 |
| d_883 | int64 | 0.0 | 91 |
| d_884 | int64 | 0.0 | 93 |
| d_885 | int64 | 0.0 | 75 |
| d_886 | int64 | 0.0 | 72 |
| d_887 | int64 | 0.0 | 82 |
| d_888 | int64 | 0.0 | 86 |
| d_889 | int64 | 0.0 | 77 |
| d_890 | int64 | 0.0 | 81 |
| d_891 | int64 | 0.0 | 79 |
| d_892 | int64 | 0.0 | 73 |
| d_893 | int64 | 0.0 | 78 |
| d_894 | int64 | 0.0 | 68 |
| d_895 | int64 | 0.0 | 69 |
| d_896 | int64 | 0.0 | 75 |
| d_897 | int64 | 0.0 | 80 |
| d_898 | int64 | 0.0 | 86 |
| d_899 | int64 | 0.0 | 70 |
| d_900 | int64 | 0.0 | 68 |
| d_901 | int64 | 0.0 | 67 |
| d_902 | int64 | 0.0 | 72 |
| d_903 | int64 | 0.0 | 71 |
| d_904 | int64 | 0.0 | 77 |
| d_905 | int64 | 0.0 | 80 |
| d_906 | int64 | 0.0 | 66 |
| d_907 | int64 | 0.0 | 66 |
| d_908 | int64 | 0.0 | 62 |
| d_909 | int64 | 0.0 | 65 |
| d_910 | int64 | 0.0 | 68 |
| d_911 | int64 | 0.0 | 80 |
| d_912 | int64 | 0.0 | 80 |
| d_913 | int64 | 0.0 | 68 |
| d_914 | int64 | 0.0 | 60 |
| d_915 | int64 | 0.0 | 64 |
| d_916 | int64 | 0.0 | 76 |
| d_917 | int64 | 0.0 | 80 |
| d_918 | int64 | 0.0 | 89 |
| d_919 | int64 | 0.0 | 87 |
| d_920 | int64 | 0.0 | 82 |
| d_921 | int64 | 0.0 | 78 |
| d_922 | int64 | 0.0 | 78 |
| d_923 | int64 | 0.0 | 77 |
| d_924 | int64 | 0.0 | 79 |
| d_925 | int64 | 0.0 | 82 |
| d_926 | int64 | 0.0 | 96 |
| d_927 | int64 | 0.0 | 82 |
| d_928 | int64 | 0.0 | 75 |
| d_929 | int64 | 0.0 | 76 |
| d_930 | int64 | 0.0 | 78 |
| d_931 | int64 | 0.0 | 78 |
| d_932 | int64 | 0.0 | 82 |
| d_933 | int64 | 0.0 | 90 |
| d_934 | int64 | 0.0 | 77 |
| d_935 | int64 | 0.0 | 70 |
| d_936 | int64 | 0.0 | 69 |
| d_937 | int64 | 0.0 | 69 |
| d_938 | int64 | 0.0 | 81 |
| d_939 | int64 | 0.0 | 94 |
| d_940 | int64 | 0.0 | 97 |
| d_941 | int64 | 0.0 | 73 |
| d_942 | int64 | 0.0 | 76 |
| d_943 | int64 | 0.0 | 70 |
| d_944 | int64 | 0.0 | 71 |
| d_945 | int64 | 0.0 | 89 |
| d_946 | int64 | 0.0 | 91 |
| d_947 | int64 | 0.0 | 97 |
| d_948 | int64 | 0.0 | 91 |
| d_949 | int64 | 0.0 | 81 |
| d_950 | int64 | 0.0 | 71 |
| d_951 | int64 | 0.0 | 73 |
| d_952 | int64 | 0.0 | 80 |
| d_953 | int64 | 0.0 | 85 |
| d_954 | int64 | 0.0 | 94 |
| d_955 | int64 | 0.0 | 81 |
| d_956 | int64 | 0.0 | 78 |
| d_957 | int64 | 0.0 | 70 |
| d_958 | int64 | 0.0 | 78 |
| d_959 | int64 | 0.0 | 78 |
| d_960 | int64 | 0.0 | 88 |
| d_961 | int64 | 0.0 | 89 |
| d_962 | int64 | 0.0 | 70 |
| d_963 | int64 | 0.0 | 68 |
| d_964 | int64 | 0.0 | 63 |
| d_965 | int64 | 0.0 | 68 |
| d_966 | int64 | 0.0 | 70 |
| d_967 | int64 | 0.0 | 79 |
| d_968 | int64 | 0.0 | 81 |
| d_969 | int64 | 0.0 | 65 |
| d_970 | int64 | 0.0 | 65 |
| d_971 | int64 | 0.0 | 60 |
| d_972 | int64 | 0.0 | 62 |
| d_973 | int64 | 0.0 | 70 |
| d_974 | int64 | 0.0 | 78 |
| d_975 | int64 | 0.0 | 75 |
| d_976 | int64 | 0.0 | 64 |
| d_977 | int64 | 0.0 | 69 |
| d_978 | int64 | 0.0 | 68 |
| d_979 | int64 | 0.0 | 70 |
| d_980 | int64 | 0.0 | 70 |
| d_981 | int64 | 0.0 | 85 |
| d_982 | int64 | 0.0 | 90 |
| d_983 | int64 | 0.0 | 70 |
| d_984 | int64 | 0.0 | 68 |
| d_985 | int64 | 0.0 | 67 |
| d_986 | int64 | 0.0 | 69 |
| d_987 | int64 | 0.0 | 72 |
| d_988 | int64 | 0.0 | 83 |
| d_989 | int64 | 0.0 | 83 |
| d_990 | int64 | 0.0 | 69 |
| d_991 | int64 | 0.0 | 66 |
| d_992 | int64 | 0.0 | 62 |
| d_993 | int64 | 0.0 | 60 |
| d_994 | int64 | 0.0 | 58 |
| d_995 | int64 | 0.0 | 77 |
| d_996 | int64 | 0.0 | 73 |
| d_997 | int64 | 0.0 | 54 |
| d_998 | int64 | 0.0 | 55 |
| d_999 | int64 | 0.0 | 55 |
| d_1000 | int64 | 0.0 | 53 |
| d_1001 | int64 | 0.0 | 64 |
| d_1002 | int64 | 0.0 | 78 |
| d_1003 | int64 | 0.0 | 75 |
| d_1004 | int64 | 0.0 | 58 |
| d_1005 | int64 | 0.0 | 60 |
| d_1006 | int64 | 0.0 | 65 |
| d_1007 | int64 | 0.0 | 59 |
| d_1008 | int64 | 0.0 | 74 |
| d_1009 | int64 | 0.0 | 80 |
| d_1010 | int64 | 0.0 | 84 |
| d_1011 | int64 | 0.0 | 63 |
| d_1012 | int64 | 0.0 | 61 |
| d_1013 | int64 | 0.0 | 64 |
| d_1014 | int64 | 0.0 | 66 |
| d_1015 | int64 | 0.0 | 70 |
| d_1016 | int64 | 0.0 | 82 |
| d_1017 | int64 | 0.0 | 81 |
| d_1018 | int64 | 0.0 | 72 |
| d_1019 | int64 | 0.0 | 65 |
| d_1020 | int64 | 0.0 | 60 |
| d_1021 | int64 | 0.0 | 60 |
| d_1022 | int64 | 0.0 | 71 |
| d_1023 | int64 | 0.0 | 82 |
| d_1024 | int64 | 0.0 | 81 |
| d_1025 | int64 | 0.0 | 60 |
| d_1026 | int64 | 0.0 | 61 |
| d_1027 | int64 | 0.0 | 53 |
| d_1028 | int64 | 0.0 | 60 |
| d_1029 | int64 | 0.0 | 64 |
| d_1030 | int64 | 0.0 | 74 |
| d_1031 | int64 | 0.0 | 69 |
| d_1032 | int64 | 0.0 | 64 |
| d_1033 | int64 | 0.0 | 64 |
| d_1034 | int64 | 0.0 | 79 |
| d_1035 | int64 | 0.0 | 66 |
| d_1036 | int64 | 0.0 | 63 |
| d_1037 | int64 | 0.0 | 60 |
| d_1038 | int64 | 0.0 | 69 |
| d_1039 | int64 | 0.0 | 75 |
| d_1040 | int64 | 0.0 | 76 |
| d_1041 | int64 | 0.0 | 66 |
| d_1042 | int64 | 0.0 | 73 |
| d_1043 | int64 | 0.0 | 75 |
| d_1044 | int64 | 0.0 | 85 |
| d_1045 | int64 | 0.0 | 74 |
| d_1046 | int64 | 0.0 | 66 |
| d_1047 | int64 | 0.0 | 63 |
| d_1048 | int64 | 0.0 | 67 |
| d_1049 | int64 | 0.0 | 64 |
| d_1050 | int64 | 0.0 | 73 |
| d_1051 | int64 | 0.0 | 76 |
| d_1052 | int64 | 0.0 | 79 |
| d_1053 | int64 | 0.0 | 63 |
| d_1054 | int64 | 0.0 | 63 |
| d_1055 | int64 | 0.0 | 60 |
| d_1056 | int64 | 0.0 | 67 |
| d_1057 | int64 | 0.0 | 62 |
| d_1058 | int64 | 0.0 | 75 |
| d_1059 | int64 | 0.0 | 70 |
| d_1060 | int64 | 0.0 | 69 |
| d_1061 | int64 | 0.0 | 71 |
| d_1062 | int64 | 0.0 | 5 |
| d_1063 | int64 | 0.0 | 71 |
| d_1064 | int64 | 0.0 | 70 |
| d_1065 | int64 | 0.0 | 70 |
| d_1066 | int64 | 0.0 | 68 |
| d_1067 | int64 | 0.0 | 66 |
| d_1068 | int64 | 0.0 | 83 |
| d_1069 | int64 | 0.0 | 56 |
| d_1070 | int64 | 0.0 | 67 |
| d_1071 | int64 | 0.0 | 73 |
| d_1072 | int64 | 0.0 | 83 |
| d_1073 | int64 | 0.0 | 92 |
| d_1074 | int64 | 0.0 | 67 |
| d_1075 | int64 | 0.0 | 68 |
| d_1076 | int64 | 0.0 | 66 |
| d_1077 | int64 | 0.0 | 63 |
| d_1078 | int64 | 0.0 | 60 |
| d_1079 | int64 | 0.0 | 83 |
| d_1080 | int64 | 0.0 | 85 |
| d_1081 | int64 | 0.0 | 65 |
| d_1082 | int64 | 0.0 | 64 |
| d_1083 | int64 | 0.0 | 59 |
| d_1084 | int64 | 0.0 | 65 |
| d_1085 | int64 | 0.0 | 68 |
| d_1086 | int64 | 0.0 | 73 |
| d_1087 | int64 | 0.0 | 72 |
| d_1088 | int64 | 0.0 | 58 |
| d_1089 | int64 | 0.0 | 55 |
| d_1090 | int64 | 0.0 | 55 |
| d_1091 | int64 | 0.0 | 50 |
| d_1092 | int64 | 0.0 | 57 |
| d_1093 | int64 | 0.0 | 70 |
| d_1094 | int64 | 0.0 | 77 |
| d_1095 | int64 | 0.0 | 61 |
| d_1096 | int64 | 0.0 | 54 |
| d_1097 | int64 | 0.0 | 48 |
| d_1098 | int64 | 0.0 | 58 |
| d_1099 | int64 | 0.0 | 66 |
| d_1100 | int64 | 0.0 | 82 |
| d_1101 | int64 | 0.0 | 79 |
| d_1102 | int64 | 0.0 | 73 |
| d_1103 | int64 | 0.0 | 61 |
| d_1104 | int64 | 0.0 | 64 |
| d_1105 | int64 | 0.0 | 67 |
| d_1106 | int64 | 0.0 | 55 |
| d_1107 | int64 | 0.0 | 71 |
| d_1108 | int64 | 0.0 | 75 |
| d_1109 | int64 | 0.0 | 59 |
| d_1110 | int64 | 0.0 | 65 |
| d_1111 | int64 | 0.0 | 65 |
| d_1112 | int64 | 0.0 | 71 |
| d_1113 | int64 | 0.0 | 66 |
| d_1114 | int64 | 0.0 | 68 |
| d_1115 | int64 | 0.0 | 72 |
| d_1116 | int64 | 0.0 | 64 |
| d_1117 | int64 | 0.0 | 56 |
| d_1118 | int64 | 0.0 | 55 |
| d_1119 | int64 | 0.0 | 53 |
| d_1120 | int64 | 0.0 | 59 |
| d_1121 | int64 | 0.0 | 64 |
| d_1122 | int64 | 0.0 | 68 |
| d_1123 | int64 | 0.0 | 52 |
| d_1124 | int64 | 0.0 | 51 |
| d_1125 | int64 | 0.0 | 46 |
| d_1126 | int64 | 0.0 | 52 |
| d_1127 | int64 | 0.0 | 59 |
| d_1128 | int64 | 0.0 | 64 |
| d_1129 | int64 | 0.0 | 73 |
| d_1130 | int64 | 0.0 | 63 |
| d_1131 | int64 | 0.0 | 56 |
| d_1132 | int64 | 0.0 | 56 |
| d_1133 | int64 | 0.0 | 59 |
| d_1134 | int64 | 0.0 | 57 |
| d_1135 | int64 | 0.0 | 72 |
| d_1136 | int64 | 0.0 | 81 |
| d_1137 | int64 | 0.0 | 64 |
| d_1138 | int64 | 0.0 | 65 |
| d_1139 | int64 | 0.0 | 68 |
| d_1140 | int64 | 0.0 | 60 |
| d_1141 | int64 | 0.0 | 67 |
| d_1142 | int64 | 0.0 | 72 |
| d_1143 | int64 | 0.0 | 75 |
| d_1144 | int64 | 0.0 | 59 |
| d_1145 | int64 | 0.0 | 56 |
| d_1146 | int64 | 0.0 | 54 |
| d_1147 | int64 | 0.0 | 55 |
| d_1148 | int64 | 0.0 | 65 |
| d_1149 | int64 | 0.0 | 72 |
| d_1150 | int64 | 0.0 | 75 |
| d_1151 | int64 | 0.0 | 60 |
| d_1152 | int64 | 0.0 | 52 |
| d_1153 | int64 | 0.0 | 50 |
| d_1154 | int64 | 0.0 | 57 |
| d_1155 | int64 | 0.0 | 56 |
| d_1156 | int64 | 0.0 | 72 |
| d_1157 | int64 | 0.0 | 74 |
| d_1158 | int64 | 0.0 | 55 |
| d_1159 | int64 | 0.0 | 58 |
| d_1160 | int64 | 0.0 | 58 |
| d_1161 | int64 | 0.0 | 66 |
| d_1162 | int64 | 0.0 | 64 |
| d_1163 | int64 | 0.0 | 78 |
| d_1164 | int64 | 0.0 | 81 |
| d_1165 | int64 | 0.0 | 69 |
| d_1166 | int64 | 0.0 | 69 |
| d_1167 | int64 | 0.0 | 71 |
| d_1168 | int64 | 0.0 | 66 |
| d_1169 | int64 | 0.0 | 73 |
| d_1170 | int64 | 0.0 | 78 |
| d_1171 | int64 | 0.0 | 79 |
| d_1172 | int64 | 0.0 | 67 |
| d_1173 | int64 | 0.0 | 64 |
| d_1174 | int64 | 0.0 | 62 |
| d_1175 | int64 | 0.0 | 61 |
| d_1176 | int64 | 0.0 | 65 |
| d_1177 | int64 | 0.0 | 80 |
| d_1178 | int64 | 0.0 | 84 |
| d_1179 | int64 | 0.0 | 61 |
| d_1180 | int64 | 0.0 | 55 |
| d_1181 | int64 | 0.0 | 58 |
| d_1182 | int64 | 0.0 | 58 |
| d_1183 | int64 | 0.0 | 64 |
| d_1184 | int64 | 0.0 | 67 |
| d_1185 | int64 | 0.0 | 74 |
| d_1186 | int64 | 0.0 | 58 |
| d_1187 | int64 | 0.0 | 61 |
| d_1188 | int64 | 0.0 | 59 |
| d_1189 | int64 | 0.0 | 66 |
| d_1190 | int64 | 0.0 | 71 |
| d_1191 | int64 | 0.0 | 83 |
| d_1192 | int64 | 0.0 | 77 |
| d_1193 | int64 | 0.0 | 67 |
| d_1194 | int64 | 0.0 | 61 |
| d_1195 | int64 | 0.0 | 57 |
| d_1196 | int64 | 0.0 | 65 |
| d_1197 | int64 | 0.0 | 69 |
| d_1198 | int64 | 0.0 | 75 |
| d_1199 | int64 | 0.0 | 78 |
| d_1200 | int64 | 0.0 | 76 |
| d_1201 | int64 | 0.0 | 65 |
| d_1202 | int64 | 0.0 | 68 |
| d_1203 | int64 | 0.0 | 64 |
| d_1204 | int64 | 0.0 | 61 |
| d_1205 | int64 | 0.0 | 67 |
| d_1206 | int64 | 0.0 | 73 |
| d_1207 | int64 | 0.0 | 57 |
| d_1208 | int64 | 0.0 | 53 |
| d_1209 | int64 | 0.0 | 59 |
| d_1210 | int64 | 0.0 | 56 |
| d_1211 | int64 | 0.0 | 57 |
| d_1212 | int64 | 0.0 | 68 |
| d_1213 | int64 | 0.0 | 67 |
| d_1214 | int64 | 0.0 | 62 |
| d_1215 | int64 | 0.0 | 54 |
| d_1216 | int64 | 0.0 | 49 |
| d_1217 | int64 | 0.0 | 53 |
| d_1218 | int64 | 0.0 | 59 |
| d_1219 | int64 | 0.0 | 64 |
| d_1220 | int64 | 0.0 | 73 |
| d_1221 | int64 | 0.0 | 67 |
| d_1222 | int64 | 0.0 | 66 |
| d_1223 | int64 | 0.0 | 61 |
| d_1224 | int64 | 0.0 | 67 |
| d_1225 | int64 | 0.0 | 68 |
| d_1226 | int64 | 0.0 | 78 |
| d_1227 | int64 | 0.0 | 82 |
| d_1228 | int64 | 0.0 | 76 |
| d_1229 | int64 | 0.0 | 67 |
| d_1230 | int64 | 0.0 | 63 |
| d_1231 | int64 | 0.0 | 67 |
| d_1232 | int64 | 0.0 | 74 |
| d_1233 | int64 | 0.0 | 80 |
| d_1234 | int64 | 0.0 | 81 |
| d_1235 | int64 | 0.0 | 67 |
| d_1236 | int64 | 0.0 | 61 |
| d_1237 | int64 | 0.0 | 62 |
| d_1238 | int64 | 0.0 | 60 |
| d_1239 | int64 | 0.0 | 70 |
| d_1240 | int64 | 0.0 | 75 |
| d_1241 | int64 | 0.0 | 70 |
| d_1242 | int64 | 0.0 | 61 |
| d_1243 | int64 | 0.0 | 55 |
| d_1244 | int64 | 0.0 | 51 |
| d_1245 | int64 | 0.0 | 53 |
| d_1246 | int64 | 0.0 | 66 |
| d_1247 | int64 | 0.0 | 66 |
| d_1248 | int64 | 0.0 | 76 |
| d_1249 | int64 | 0.0 | 67 |
| d_1250 | int64 | 0.0 | 65 |
| d_1251 | int64 | 0.0 | 69 |
| d_1252 | int64 | 0.0 | 80 |
| d_1253 | int64 | 0.0 | 75 |
| d_1254 | int64 | 0.0 | 74 |
| d_1255 | int64 | 0.0 | 89 |
| d_1256 | int64 | 0.0 | 72 |
| d_1257 | int64 | 0.0 | 67 |
| d_1258 | int64 | 0.0 | 69 |
| d_1259 | int64 | 0.0 | 69 |
| d_1260 | int64 | 0.0 | 77 |
| d_1261 | int64 | 0.0 | 86 |
| d_1262 | int64 | 0.0 | 78 |
| d_1263 | int64 | 0.0 | 76 |
| d_1264 | int64 | 0.0 | 73 |
| d_1265 | int64 | 0.0 | 67 |
| d_1266 | int64 | 0.0 | 66 |
| d_1267 | int64 | 0.0 | 73 |
| d_1268 | int64 | 0.0 | 79 |
| d_1269 | int64 | 0.0 | 78 |
| d_1270 | int64 | 0.0 | 62 |
| d_1271 | int64 | 0.0 | 62 |
| d_1272 | int64 | 0.0 | 65 |
| d_1273 | int64 | 0.0 | 65 |
| d_1274 | int64 | 0.0 | 67 |
| d_1275 | int64 | 0.0 | 75 |
| d_1276 | int64 | 0.0 | 86 |
| d_1277 | int64 | 0.0 | 61 |
| d_1278 | int64 | 0.0 | 63 |
| d_1279 | int64 | 0.0 | 61 |
| d_1280 | int64 | 0.0 | 64 |
| d_1281 | int64 | 0.0 | 76 |
| d_1282 | int64 | 0.0 | 81 |
| d_1283 | int64 | 0.0 | 91 |
| d_1284 | int64 | 0.0 | 70 |
| d_1285 | int64 | 0.0 | 74 |
| d_1286 | int64 | 0.0 | 66 |
| d_1287 | int64 | 0.0 | 71 |
| d_1288 | int64 | 0.0 | 75 |
| d_1289 | int64 | 0.0 | 81 |
| d_1290 | int64 | 0.0 | 80 |
| d_1291 | int64 | 0.0 | 70 |
| d_1292 | int64 | 0.0 | 72 |
| d_1293 | int64 | 0.0 | 64 |
| d_1294 | int64 | 0.0 | 65 |
| d_1295 | int64 | 0.0 | 73 |
| d_1296 | int64 | 0.0 | 83 |
| d_1297 | int64 | 0.0 | 82 |
| d_1298 | int64 | 0.0 | 71 |
| d_1299 | int64 | 0.0 | 63 |
| d_1300 | int64 | 0.0 | 58 |
| d_1301 | int64 | 0.0 | 58 |
| d_1302 | int64 | 0.0 | 69 |
| d_1303 | int64 | 0.0 | 77 |
| d_1304 | int64 | 0.0 | 84 |
| d_1305 | int64 | 0.0 | 65 |
| d_1306 | int64 | 0.0 | 60 |
| d_1307 | int64 | 0.0 | 59 |
| d_1308 | int64 | 0.0 | 57 |
| d_1309 | int64 | 0.0 | 64 |
| d_1310 | int64 | 0.0 | 76 |
| d_1311 | int64 | 0.0 | 71 |
| d_1312 | int64 | 0.0 | 76 |
| d_1313 | int64 | 0.0 | 63 |
| d_1314 | int64 | 0.0 | 69 |
| d_1315 | int64 | 0.0 | 64 |
| d_1316 | int64 | 0.0 | 67 |
| d_1317 | int64 | 0.0 | 80 |
| d_1318 | int64 | 0.0 | 85 |
| d_1319 | int64 | 0.0 | 68 |
| d_1320 | int64 | 0.0 | 66 |
| d_1321 | int64 | 0.0 | 62 |
| d_1322 | int64 | 0.0 | 67 |
| d_1323 | int64 | 0.0 | 69 |
| d_1324 | int64 | 0.0 | 79 |
| d_1325 | int64 | 0.0 | 84 |
| d_1326 | int64 | 0.0 | 69 |
| d_1327 | int64 | 0.0 | 61 |
| d_1328 | int64 | 0.0 | 56 |
| d_1329 | int64 | 0.0 | 55 |
| d_1330 | int64 | 0.0 | 66 |
| d_1331 | int64 | 0.0 | 76 |
| d_1332 | int64 | 0.0 | 77 |
| d_1333 | int64 | 0.0 | 61 |
| d_1334 | int64 | 0.0 | 57 |
| d_1335 | int64 | 0.0 | 57 |
| d_1336 | int64 | 0.0 | 58 |
| d_1337 | int64 | 0.0 | 59 |
| d_1338 | int64 | 0.0 | 71 |
| d_1339 | int64 | 0.0 | 73 |
| d_1340 | int64 | 0.0 | 59 |
| d_1341 | int64 | 0.0 | 58 |
| d_1342 | int64 | 0.0 | 62 |
| d_1343 | int64 | 0.0 | 66 |
| d_1344 | int64 | 0.0 | 76 |
| d_1345 | int64 | 0.0 | 74 |
| d_1346 | int64 | 0.0 | 83 |
| d_1347 | int64 | 0.0 | 69 |
| d_1348 | int64 | 0.0 | 61 |
| d_1349 | int64 | 0.0 | 62 |
| d_1350 | int64 | 0.0 | 64 |
| d_1351 | int64 | 0.0 | 63 |
| d_1352 | int64 | 0.0 | 74 |
| d_1353 | int64 | 0.0 | 77 |
| d_1354 | int64 | 0.0 | 58 |
| d_1355 | int64 | 0.0 | 57 |
| d_1356 | int64 | 0.0 | 65 |
| d_1357 | int64 | 0.0 | 52 |
| d_1358 | int64 | 0.0 | 54 |
| d_1359 | int64 | 0.0 | 71 |
| d_1360 | int64 | 0.0 | 76 |
| d_1361 | int64 | 0.0 | 55 |
| d_1362 | int64 | 0.0 | 51 |
| d_1363 | int64 | 0.0 | 50 |
| d_1364 | int64 | 0.0 | 52 |
| d_1365 | int64 | 0.0 | 63 |
| d_1366 | int64 | 0.0 | 69 |
| d_1367 | int64 | 0.0 | 66 |
| d_1368 | int64 | 0.0 | 60 |
| d_1369 | int64 | 0.0 | 56 |
| d_1370 | int64 | 0.0 | 57 |
| d_1371 | int64 | 0.0 | 63 |
| d_1372 | int64 | 0.0 | 64 |
| d_1373 | int64 | 0.0 | 73 |
| d_1374 | int64 | 0.0 | 75 |
| d_1375 | int64 | 0.0 | 66 |
| d_1376 | int64 | 0.0 | 59 |
| d_1377 | int64 | 0.0 | 59 |
| d_1378 | int64 | 0.0 | 58 |
| d_1379 | int64 | 0.0 | 65 |
| d_1380 | int64 | 0.0 | 75 |
| d_1381 | int64 | 0.0 | 78 |
| d_1382 | int64 | 0.0 | 62 |
| d_1383 | int64 | 0.0 | 62 |
| d_1384 | int64 | 0.0 | 58 |
| d_1385 | int64 | 0.0 | 53 |
| d_1386 | int64 | 0.0 | 65 |
| d_1387 | int64 | 0.0 | 74 |
| d_1388 | int64 | 0.0 | 74 |
| d_1389 | int64 | 0.0 | 54 |
| d_1390 | int64 | 0.0 | 54 |
| d_1391 | int64 | 0.0 | 53 |
| d_1392 | int64 | 0.0 | 55 |
| d_1393 | int64 | 0.0 | 63 |
| d_1394 | int64 | 0.0 | 70 |
| d_1395 | int64 | 0.0 | 70 |
| d_1396 | int64 | 0.0 | 56 |
| d_1397 | int64 | 0.0 | 63 |
| d_1398 | int64 | 0.0 | 76 |
| d_1399 | int64 | 0.0 | 75 |
| d_1400 | int64 | 0.0 | 60 |
| d_1401 | int64 | 0.0 | 61 |
| d_1402 | int64 | 0.0 | 62 |
| d_1403 | int64 | 0.0 | 55 |
| d_1404 | int64 | 0.0 | 58 |
| d_1405 | int64 | 0.0 | 59 |
| d_1406 | int64 | 0.0 | 56 |
| d_1407 | int64 | 0.0 | 67 |
| d_1408 | int64 | 0.0 | 68 |
| d_1409 | int64 | 0.0 | 64 |
| d_1410 | int64 | 0.0 | 61 |
| d_1411 | int64 | 0.0 | 58 |
| d_1412 | int64 | 0.0 | 55 |
| d_1413 | int64 | 0.0 | 55 |
| d_1414 | int64 | 0.0 | 56 |
| d_1415 | int64 | 0.0 | 65 |
| d_1416 | int64 | 0.0 | 63 |
| d_1417 | int64 | 0.0 | 58 |
| d_1418 | int64 | 0.0 | 52 |
| d_1419 | int64 | 0.0 | 57 |
| d_1420 | int64 | 0.0 | 66 |
| d_1421 | int64 | 0.0 | 57 |
| d_1422 | int64 | 0.0 | 65 |
| d_1423 | int64 | 0.0 | 71 |
| d_1424 | int64 | 0.0 | 64 |
| d_1425 | int64 | 0.0 | 67 |
| d_1426 | int64 | 0.0 | 68 |
| d_1427 | int64 | 0.0 | 3 |
| d_1428 | int64 | 0.0 | 59 |
| d_1429 | int64 | 0.0 | 57 |
| d_1430 | int64 | 0.0 | 55 |
| d_1431 | int64 | 0.0 | 49 |
| d_1432 | int64 | 0.0 | 50 |
| d_1433 | int64 | 0.0 | 65 |
| d_1434 | int64 | 0.0 | 50 |
| d_1435 | int64 | 0.0 | 67 |
| d_1436 | int64 | 0.0 | 71 |
| d_1437 | int64 | 0.0 | 73 |
| d_1438 | int64 | 0.0 | 59 |
| d_1439 | int64 | 0.0 | 65 |
| d_1440 | int64 | 0.0 | 58 |
| d_1441 | int64 | 0.0 | 58 |
| d_1442 | int64 | 0.0 | 60 |
| d_1443 | int64 | 0.0 | 70 |
| d_1444 | int64 | 0.0 | 74 |
| d_1445 | int64 | 0.0 | 65 |
| d_1446 | int64 | 0.0 | 57 |
| d_1447 | int64 | 0.0 | 60 |
| d_1448 | int64 | 0.0 | 62 |
| d_1449 | int64 | 0.0 | 62 |
| d_1450 | int64 | 0.0 | 77 |
| d_1451 | int64 | 0.0 | 74 |
| d_1452 | int64 | 0.0 | 58 |
| d_1453 | int64 | 0.0 | 56 |
| d_1454 | int64 | 0.0 | 52 |
| d_1455 | int64 | 0.0 | 51 |
| d_1456 | int64 | 0.0 | 60 |
| d_1457 | int64 | 0.0 | 66 |
| d_1458 | int64 | 0.0 | 71 |
| d_1459 | int64 | 0.0 | 56 |
| d_1460 | int64 | 0.0 | 54 |
| d_1461 | int64 | 0.0 | 55 |
| d_1462 | int64 | 0.0 | 52 |
| d_1463 | int64 | 0.0 | 64 |
| d_1464 | int64 | 0.0 | 79 |
| d_1465 | int64 | 0.0 | 76 |
| d_1466 | int64 | 0.0 | 59 |
| d_1467 | int64 | 0.0 | 60 |
| d_1468 | int64 | 0.0 | 63 |
| d_1469 | int64 | 0.0 | 59 |
| d_1470 | int64 | 0.0 | 68 |
| d_1471 | int64 | 0.0 | 75 |
| d_1472 | int64 | 0.0 | 79 |
| d_1473 | int64 | 0.0 | 66 |
| d_1474 | int64 | 0.0 | 61 |
| d_1475 | int64 | 0.0 | 65 |
| d_1476 | int64 | 0.0 | 64 |
| d_1477 | int64 | 0.0 | 63 |
| d_1478 | int64 | 0.0 | 76 |
| d_1479 | int64 | 0.0 | 66 |
| d_1480 | int64 | 0.0 | 55 |
| d_1481 | int64 | 0.0 | 50 |
| d_1482 | int64 | 0.0 | 53 |
| d_1483 | int64 | 0.0 | 52 |
| d_1484 | int64 | 0.0 | 53 |
| d_1485 | int64 | 0.0 | 62 |
| d_1486 | int64 | 0.0 | 64 |
| d_1487 | int64 | 0.0 | 52 |
| d_1488 | int64 | 0.0 | 56 |
| d_1489 | int64 | 0.0 | 50 |
| d_1490 | int64 | 0.0 | 48 |
| d_1491 | int64 | 0.0 | 50 |
| d_1492 | int64 | 0.0 | 56 |
| d_1493 | int64 | 0.0 | 64 |
| d_1494 | int64 | 0.0 | 55 |
| d_1495 | int64 | 0.0 | 59 |
| d_1496 | int64 | 0.0 | 57 |
| d_1497 | int64 | 0.0 | 60 |
| d_1498 | int64 | 0.0 | 60 |
| d_1499 | int64 | 0.0 | 67 |
| d_1500 | int64 | 0.0 | 78 |
| d_1501 | int64 | 0.0 | 63 |
| d_1502 | int64 | 0.0 | 57 |
| d_1503 | int64 | 0.0 | 52 |
| d_1504 | int64 | 0.0 | 63 |
| d_1505 | int64 | 0.0 | 67 |
| d_1506 | int64 | 0.0 | 76 |
| d_1507 | int64 | 0.0 | 77 |
| d_1508 | int64 | 0.0 | 62 |
| d_1509 | int64 | 0.0 | 60 |
| d_1510 | int64 | 0.0 | 54 |
| d_1511 | int64 | 0.0 | 54 |
| d_1512 | int64 | 0.0 | 57 |
| d_1513 | int64 | 0.0 | 70 |
| d_1514 | int64 | 0.0 | 69 |
| d_1515 | int64 | 0.0 | 57 |
| d_1516 | int64 | 0.0 | 55 |
| d_1517 | int64 | 0.0 | 54 |
| d_1518 | int64 | 0.0 | 53 |
| d_1519 | int64 | 0.0 | 57 |
| d_1520 | int64 | 0.0 | 69 |
| d_1521 | int64 | 0.0 | 71 |
| d_1522 | int64 | 0.0 | 55 |
| d_1523 | int64 | 0.0 | 51 |
| d_1524 | int64 | 0.0 | 61 |
| d_1525 | int64 | 0.0 | 58 |
| d_1526 | int64 | 0.0 | 74 |
| d_1527 | int64 | 0.0 | 78 |
| d_1528 | int64 | 0.0 | 70 |
| d_1529 | int64 | 0.0 | 67 |
| d_1530 | int64 | 0.0 | 60 |
| d_1531 | int64 | 0.0 | 59 |
| d_1532 | int64 | 0.0 | 60 |
| d_1533 | int64 | 0.0 | 59 |
| d_1534 | int64 | 0.0 | 73 |
| d_1535 | int64 | 0.0 | 70 |
| d_1536 | int64 | 0.0 | 54 |
| d_1537 | int64 | 0.0 | 64 |
| d_1538 | int64 | 0.0 | 59 |
| d_1539 | int64 | 0.0 | 55 |
| d_1540 | int64 | 0.0 | 61 |
| d_1541 | int64 | 0.0 | 70 |
| d_1542 | int64 | 0.0 | 64 |
| d_1543 | int64 | 0.0 | 55 |
| d_1544 | int64 | 0.0 | 54 |
| d_1545 | int64 | 0.0 | 52 |
| d_1546 | int64 | 0.0 | 56 |
| d_1547 | int64 | 0.0 | 57 |
| d_1548 | int64 | 0.0 | 66 |
| d_1549 | int64 | 0.0 | 70 |
| d_1550 | int64 | 0.0 | 56 |
| d_1551 | int64 | 0.0 | 47 |
| d_1552 | int64 | 0.0 | 53 |
| d_1553 | int64 | 0.0 | 59 |
| d_1554 | int64 | 0.0 | 65 |
| d_1555 | int64 | 0.0 | 79 |
| d_1556 | int64 | 0.0 | 74 |
| d_1557 | int64 | 0.0 | 59 |
| d_1558 | int64 | 0.0 | 59 |
| d_1559 | int64 | 0.0 | 60 |
| d_1560 | int64 | 0.0 | 57 |
| d_1561 | int64 | 0.0 | 63 |
| d_1562 | int64 | 0.0 | 73 |
| d_1563 | int64 | 0.0 | 67 |
| d_1564 | int64 | 0.0 | 63 |
| d_1565 | int64 | 0.0 | 60 |
| d_1566 | int64 | 0.0 | 55 |
| d_1567 | int64 | 0.0 | 52 |
| d_1568 | int64 | 0.0 | 61 |
| d_1569 | int64 | 0.0 | 63 |
| d_1570 | int64 | 0.0 | 65 |
| d_1571 | int64 | 0.0 | 50 |
| d_1572 | int64 | 0.0 | 51 |
| d_1573 | int64 | 0.0 | 53 |
| d_1574 | int64 | 0.0 | 45 |
| d_1575 | int64 | 0.0 | 59 |
| d_1576 | int64 | 0.0 | 63 |
| d_1577 | int64 | 0.0 | 58 |
| d_1578 | int64 | 0.0 | 62 |
| d_1579 | int64 | 0.0 | 52 |
| d_1580 | int64 | 0.0 | 47 |
| d_1581 | int64 | 0.0 | 50 |
| d_1582 | int64 | 0.0 | 54 |
| d_1583 | int64 | 0.0 | 63 |
| d_1584 | int64 | 0.0 | 63 |
| d_1585 | int64 | 0.0 | 60 |
| d_1586 | int64 | 0.0 | 68 |
| d_1587 | int64 | 0.0 | 61 |
| d_1588 | int64 | 0.0 | 53 |
| d_1589 | int64 | 0.0 | 64 |
| d_1590 | int64 | 0.0 | 68 |
| d_1591 | int64 | 0.0 | 79 |
| d_1592 | int64 | 0.0 | 70 |
| d_1593 | int64 | 0.0 | 67 |
| d_1594 | int64 | 0.0 | 60 |
| d_1595 | int64 | 0.0 | 64 |
| d_1596 | int64 | 0.0 | 70 |
| d_1597 | int64 | 0.0 | 67 |
| d_1598 | int64 | 0.0 | 96 |
| d_1599 | int64 | 0.0 | 84 |
| d_1600 | int64 | 0.0 | 59 |
| d_1601 | int64 | 0.0 | 60 |
| d_1602 | int64 | 0.0 | 61 |
| d_1603 | int64 | 0.0 | 65 |
| d_1604 | int64 | 0.0 | 74 |
| d_1605 | int64 | 0.0 | 75 |
| d_1606 | int64 | 0.0 | 58 |
| d_1607 | int64 | 0.0 | 62 |
| d_1608 | int64 | 0.0 | 57 |
| d_1609 | int64 | 0.0 | 63 |
| d_1610 | int64 | 0.0 | 63 |
| d_1611 | int64 | 0.0 | 76 |
| d_1612 | int64 | 0.0 | 77 |
| d_1613 | int64 | 0.0 | 61 |
| d_1614 | int64 | 0.0 | 61 |
| d_1615 | int64 | 0.0 | 67 |
| d_1616 | int64 | 0.0 | 73 |
| d_1617 | int64 | 0.0 | 91 |
| d_1618 | int64 | 0.0 | 77 |
| d_1619 | int64 | 0.0 | 76 |
| d_1620 | int64 | 0.0 | 69 |
| d_1621 | int64 | 0.0 | 67 |
| d_1622 | int64 | 0.0 | 60 |
| d_1623 | int64 | 0.0 | 64 |
| d_1624 | int64 | 0.0 | 66 |
| d_1625 | int64 | 0.0 | 75 |
| d_1626 | int64 | 0.0 | 78 |
| d_1627 | int64 | 0.0 | 62 |
| d_1628 | int64 | 0.0 | 67 |
| d_1629 | int64 | 0.0 | 66 |
| d_1630 | int64 | 0.0 | 61 |
| d_1631 | int64 | 0.0 | 71 |
| d_1632 | int64 | 0.0 | 75 |
| d_1633 | int64 | 0.0 | 80 |
| d_1634 | int64 | 0.0 | 67 |
| d_1635 | int64 | 0.0 | 62 |
| d_1636 | int64 | 0.0 | 59 |
| d_1637 | int64 | 0.0 | 60 |
| d_1638 | int64 | 0.0 | 69 |
| d_1639 | int64 | 0.0 | 72 |
| d_1640 | int64 | 0.0 | 79 |
| d_1641 | int64 | 0.0 | 64 |
| d_1642 | int64 | 0.0 | 65 |
| d_1643 | int64 | 0.0 | 56 |
| d_1644 | int64 | 0.0 | 60 |
| d_1645 | int64 | 0.0 | 70 |
| d_1646 | int64 | 0.0 | 79 |
| d_1647 | int64 | 0.0 | 86 |
| d_1648 | int64 | 0.0 | 72 |
| d_1649 | int64 | 0.0 | 59 |
| d_1650 | int64 | 0.0 | 69 |
| d_1651 | int64 | 0.0 | 64 |
| d_1652 | int64 | 0.0 | 69 |
| d_1653 | int64 | 0.0 | 82 |
| d_1654 | int64 | 0.0 | 85 |
| d_1655 | int64 | 0.0 | 64 |
| d_1656 | int64 | 0.0 | 63 |
| d_1657 | int64 | 0.0 | 70 |
| d_1658 | int64 | 0.0 | 64 |
| d_1659 | int64 | 0.0 | 75 |
| d_1660 | int64 | 0.0 | 83 |
| d_1661 | int64 | 0.0 | 89 |
| d_1662 | int64 | 0.0 | 72 |
| d_1663 | int64 | 0.0 | 64 |
| d_1664 | int64 | 0.0 | 58 |
| d_1665 | int64 | 0.0 | 59 |
| d_1666 | int64 | 0.0 | 65 |
| d_1667 | int64 | 0.0 | 71 |
| d_1668 | int64 | 0.0 | 73 |
| d_1669 | int64 | 0.0 | 62 |
| d_1670 | int64 | 0.0 | 55 |
| d_1671 | int64 | 0.0 | 57 |
| d_1672 | int64 | 0.0 | 57 |
| d_1673 | int64 | 0.0 | 65 |
| d_1674 | int64 | 0.0 | 77 |
| d_1675 | int64 | 0.0 | 72 |
| d_1676 | int64 | 0.0 | 56 |
| d_1677 | int64 | 0.0 | 63 |
| d_1678 | int64 | 0.0 | 65 |
| d_1679 | int64 | 0.0 | 64 |
| d_1680 | int64 | 0.0 | 63 |
| d_1681 | int64 | 0.0 | 72 |
| d_1682 | int64 | 0.0 | 82 |
| d_1683 | int64 | 0.0 | 78 |
| d_1684 | int64 | 0.0 | 65 |
| d_1685 | int64 | 0.0 | 67 |
| d_1686 | int64 | 0.0 | 61 |
| d_1687 | int64 | 0.0 | 69 |
| d_1688 | int64 | 0.0 | 76 |
| d_1689 | int64 | 0.0 | 79 |
| d_1690 | int64 | 0.0 | 61 |
| d_1691 | int64 | 0.0 | 61 |
| d_1692 | int64 | 0.0 | 58 |
| d_1693 | int64 | 0.0 | 56 |
| d_1694 | int64 | 0.0 | 66 |
| d_1695 | int64 | 0.0 | 75 |
| d_1696 | int64 | 0.0 | 78 |
| d_1697 | int64 | 0.0 | 63 |
| d_1698 | int64 | 0.0 | 54 |
| d_1699 | int64 | 0.0 | 58 |
| d_1700 | int64 | 0.0 | 62 |
| d_1701 | int64 | 0.0 | 70 |
| d_1702 | int64 | 0.0 | 73 |
| d_1703 | int64 | 0.0 | 71 |
| d_1704 | int64 | 0.0 | 54 |
| d_1705 | int64 | 0.0 | 51 |
| d_1706 | int64 | 0.0 | 50 |
| d_1707 | int64 | 0.0 | 61 |
| d_1708 | int64 | 0.0 | 70 |
| d_1709 | int64 | 0.0 | 82 |
| d_1710 | int64 | 0.0 | 71 |
| d_1711 | int64 | 0.0 | 67 |
| d_1712 | int64 | 0.0 | 62 |
| d_1713 | int64 | 0.0 | 60 |
| d_1714 | int64 | 0.0 | 66 |
| d_1715 | int64 | 0.0 | 69 |
| d_1716 | int64 | 0.0 | 74 |
| d_1717 | int64 | 0.0 | 73 |
| d_1718 | int64 | 0.0 | 67 |
| d_1719 | int64 | 0.0 | 63 |
| d_1720 | int64 | 0.0 | 62 |
| d_1721 | int64 | 0.0 | 61 |
| d_1722 | int64 | 0.0 | 65 |
| d_1723 | int64 | 0.0 | 72 |
| d_1724 | int64 | 0.0 | 78 |
| d_1725 | int64 | 0.0 | 55 |
| d_1726 | int64 | 0.0 | 53 |
| d_1727 | int64 | 0.0 | 56 |
| d_1728 | int64 | 0.0 | 58 |
| d_1729 | int64 | 0.0 | 62 |
| d_1730 | int64 | 0.0 | 64 |
| d_1731 | int64 | 0.0 | 74 |
| d_1732 | int64 | 0.0 | 54 |
| d_1733 | int64 | 0.0 | 56 |
| d_1734 | int64 | 0.0 | 54 |
| d_1735 | int64 | 0.0 | 60 |
| d_1736 | int64 | 0.0 | 69 |
| d_1737 | int64 | 0.0 | 71 |
| d_1738 | int64 | 0.0 | 68 |
| d_1739 | int64 | 0.0 | 54 |
| d_1740 | int64 | 0.0 | 55 |
| d_1741 | int64 | 0.0 | 52 |
| d_1742 | int64 | 0.0 | 58 |
| d_1743 | int64 | 0.0 | 64 |
| d_1744 | int64 | 0.0 | 70 |
| d_1745 | int64 | 0.0 | 67 |
| d_1746 | int64 | 0.0 | 60 |
| d_1747 | int64 | 0.0 | 54 |
| d_1748 | int64 | 0.0 | 57 |
| d_1749 | int64 | 0.0 | 61 |
| d_1750 | int64 | 0.0 | 67 |
| d_1751 | int64 | 0.0 | 66 |
| d_1752 | int64 | 0.0 | 74 |
| d_1753 | int64 | 0.0 | 55 |
| d_1754 | int64 | 0.0 | 50 |
| d_1755 | int64 | 0.0 | 50 |
| d_1756 | int64 | 0.0 | 52 |
| d_1757 | int64 | 0.0 | 64 |
| d_1758 | int64 | 0.0 | 69 |
| d_1759 | int64 | 0.0 | 72 |
| d_1760 | int64 | 0.0 | 62 |
| d_1761 | int64 | 0.0 | 63 |
| d_1762 | int64 | 0.0 | 81 |
| d_1763 | int64 | 0.0 | 77 |
| d_1764 | int64 | 0.0 | 62 |
| d_1765 | int64 | 0.0 | 60 |
| d_1766 | int64 | 0.0 | 58 |
| d_1767 | int64 | 0.0 | 54 |
| d_1768 | int64 | 0.0 | 56 |
| d_1769 | int64 | 0.0 | 58 |
| d_1770 | int64 | 0.0 | 60 |
| d_1771 | int64 | 0.0 | 57 |
| d_1772 | int64 | 0.0 | 71 |
| d_1773 | int64 | 0.0 | 71 |
| d_1774 | int64 | 0.0 | 52 |
| d_1775 | int64 | 0.0 | 56 |
| d_1776 | int64 | 0.0 | 58 |
| d_1777 | int64 | 0.0 | 54 |
| d_1778 | int64 | 0.0 | 66 |
| d_1779 | int64 | 0.0 | 72 |
| d_1780 | int64 | 0.0 | 67 |
| d_1781 | int64 | 0.0 | 60 |
| d_1782 | int64 | 0.0 | 62 |
| d_1783 | int64 | 0.0 | 54 |
| d_1784 | int64 | 0.0 | 61 |
| d_1785 | int64 | 0.0 | 56 |
| d_1786 | int64 | 0.0 | 70 |
| d_1787 | int64 | 0.0 | 64 |
| d_1788 | int64 | 0.0 | 58 |
| d_1789 | int64 | 0.0 | 60 |
| d_1790 | int64 | 0.0 | 65 |
| d_1791 | int64 | 0.0 | 72 |
| d_1792 | int64 | 0.0 | 3 |
| d_1793 | int64 | 0.0 | 65 |
| d_1794 | int64 | 0.0 | 58 |
| d_1795 | int64 | 0.0 | 47 |
| d_1796 | int64 | 0.0 | 49 |
| d_1797 | int64 | 0.0 | 53 |
| d_1798 | int64 | 0.0 | 71 |
| d_1799 | int64 | 0.0 | 54 |
| d_1800 | int64 | 0.0 | 61 |
| d_1801 | int64 | 0.0 | 62 |
| d_1802 | int64 | 0.0 | 54 |
| d_1803 | int64 | 0.0 | 56 |
| d_1804 | int64 | 0.0 | 53 |
| d_1805 | int64 | 0.0 | 65 |
| d_1806 | int64 | 0.0 | 64 |
| d_1807 | int64 | 0.0 | 77 |
| d_1808 | int64 | 0.0 | 70 |
| d_1809 | int64 | 0.0 | 65 |
| d_1810 | int64 | 0.0 | 58 |
| d_1811 | int64 | 0.0 | 54 |
| d_1812 | int64 | 0.0 | 58 |
| d_1813 | int64 | 0.0 | 64 |
| d_1814 | int64 | 0.0 | 71 |
| d_1815 | int64 | 0.0 | 67 |
| d_1816 | int64 | 0.0 | 59 |
| d_1817 | int64 | 0.0 | 56 |
| d_1818 | int64 | 0.0 | 55 |
| d_1819 | int64 | 0.0 | 57 |
| d_1820 | int64 | 0.0 | 57 |
| d_1821 | int64 | 0.0 | 70 |
| d_1822 | int64 | 0.0 | 70 |
| d_1823 | int64 | 0.0 | 55 |
| d_1824 | int64 | 0.0 | 49 |
| d_1825 | int64 | 0.0 | 51 |
| d_1826 | int64 | 0.0 | 49 |
| d_1827 | int64 | 0.0 | 57 |
| d_1828 | int64 | 0.0 | 72 |
| d_1829 | int64 | 0.0 | 69 |
| d_1830 | int64 | 0.0 | 64 |
| d_1831 | int64 | 0.0 | 54 |
| d_1832 | int64 | 0.0 | 66 |
| d_1833 | int64 | 0.0 | 59 |
| d_1834 | int64 | 0.0 | 65 |
| d_1835 | int64 | 0.0 | 78 |
| d_1836 | int64 | 0.0 | 73 |
| d_1837 | int64 | 0.0 | 58 |
| d_1838 | int64 | 0.0 | 58 |
| d_1839 | int64 | 0.0 | 66 |
| d_1840 | int64 | 0.0 | 68 |
| d_1841 | int64 | 0.0 | 70 |
| d_1842 | int64 | 0.0 | 77 |
| d_1843 | int64 | 0.0 | 72 |
| d_1844 | int64 | 0.0 | 76 |
| d_1845 | int64 | 0.0 | 64 |
| d_1846 | int64 | 0.0 | 62 |
| d_1847 | int64 | 0.0 | 60 |
| d_1848 | int64 | 0.0 | 64 |
| d_1849 | int64 | 0.0 | 75 |
| d_1850 | int64 | 0.0 | 76 |
| d_1851 | int64 | 0.0 | 55 |
| d_1852 | int64 | 0.0 | 56 |
| d_1853 | int64 | 0.0 | 55 |
| d_1854 | int64 | 0.0 | 58 |
| d_1855 | int64 | 0.0 | 58 |
| d_1856 | int64 | 0.0 | 67 |
| d_1857 | int64 | 0.0 | 69 |
| d_1858 | int64 | 0.0 | 55 |
| d_1859 | int64 | 0.0 | 58 |
| d_1860 | int64 | 0.0 | 59 |
| d_1861 | int64 | 0.0 | 61 |
| d_1862 | int64 | 0.0 | 63 |
| d_1863 | int64 | 0.0 | 72 |
| d_1864 | int64 | 0.0 | 76 |
| d_1865 | int64 | 0.0 | 60 |
| d_1866 | int64 | 0.0 | 63 |
| d_1867 | int64 | 0.0 | 58 |
| d_1868 | int64 | 0.0 | 57 |
| d_1869 | int64 | 0.0 | 61 |
| d_1870 | int64 | 0.0 | 73 |
| d_1871 | int64 | 0.0 | 74 |
| d_1872 | int64 | 0.0 | 62 |
| d_1873 | int64 | 0.0 | 62 |
| d_1874 | int64 | 0.0 | 61 |
| d_1875 | int64 | 0.0 | 60 |
| d_1876 | int64 | 0.0 | 61 |
| d_1877 | int64 | 0.0 | 64 |
| d_1878 | int64 | 0.0 | 72 |
| d_1879 | int64 | 0.0 | 54 |
| d_1880 | int64 | 0.0 | 53 |
| d_1881 | int64 | 0.0 | 53 |
| d_1882 | int64 | 0.0 | 55 |
| d_1883 | int64 | 0.0 | 73 |
| d_1884 | int64 | 0.0 | 85 |
| d_1885 | int64 | 0.0 | 82 |
| d_1886 | int64 | 0.0 | 55 |
| d_1887 | int64 | 0.0 | 55 |
| d_1888 | int64 | 0.0 | 56 |
| d_1889 | int64 | 0.0 | 56 |
| d_1890 | int64 | 0.0 | 64 |
| d_1891 | int64 | 0.0 | 77 |
| d_1892 | int64 | 0.0 | 75 |
| d_1893 | int64 | 0.0 | 61 |
| d_1894 | int64 | 0.0 | 63 |
| d_1895 | int64 | 0.0 | 61 |
| d_1896 | int64 | 0.0 | 60 |
| d_1897 | int64 | 0.0 | 70 |
| d_1898 | int64 | 0.0 | 80 |
| d_1899 | int64 | 0.0 | 72 |
| d_1900 | int64 | 0.0 | 64 |
| d_1901 | int64 | 0.0 | 59 |
| d_1902 | int64 | 0.0 | 55 |
| d_1903 | int64 | 0.0 | 63 |
| d_1904 | int64 | 0.0 | 69 |
| d_1905 | int64 | 0.0 | 71 |
| d_1906 | int64 | 0.0 | 77 |
| d_1907 | int64 | 0.0 | 61 |
| d_1908 | int64 | 0.0 | 57 |
| d_1909 | int64 | 0.0 | 53 |
| d_1910 | int64 | 0.0 | 57 |
| d_1911 | int64 | 0.0 | 61 |
| d_1912 | int64 | 0.0 | 73 |
| d_1913 | int64 | 0.0 | 65 |

### `data\raw\m5\sample_submission.csv`

Size: 5228786 bytes. Profiled rows: 60980. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| id | str | 0.0 | 60980 |
| F1 | int64 | 0.0 | 1 |
| F2 | int64 | 0.0 | 1 |
| F3 | int64 | 0.0 | 1 |
| F4 | int64 | 0.0 | 1 |
| F5 | int64 | 0.0 | 1 |
| F6 | int64 | 0.0 | 1 |
| F7 | int64 | 0.0 | 1 |
| F8 | int64 | 0.0 | 1 |
| F9 | int64 | 0.0 | 1 |
| F10 | int64 | 0.0 | 1 |
| F11 | int64 | 0.0 | 1 |
| F12 | int64 | 0.0 | 1 |
| F13 | int64 | 0.0 | 1 |
| F14 | int64 | 0.0 | 1 |
| F15 | int64 | 0.0 | 1 |
| F16 | int64 | 0.0 | 1 |
| F17 | int64 | 0.0 | 1 |
| F18 | int64 | 0.0 | 1 |
| F19 | int64 | 0.0 | 1 |
| F20 | int64 | 0.0 | 1 |
| F21 | int64 | 0.0 | 1 |
| F22 | int64 | 0.0 | 1 |
| F23 | int64 | 0.0 | 1 |
| F24 | int64 | 0.0 | 1 |
| F25 | int64 | 0.0 | 1 |
| F26 | int64 | 0.0 | 1 |
| F27 | int64 | 0.0 | 1 |
| F28 | int64 | 0.0 | 1 |

### `data\raw\m5\sell_prices.csv`

Size: 203395785 bytes. Profiled rows: 250000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| store_id | str | 0.0 | 1 |
| item_id | str | 0.0 | 1111 |
| wm_yr_wk | int64 | 0.0 | 282 |
| sell_price | float64 | 0.0 | 474 |

## online_retail_ii

- Status: `profiled`
- URL: https://archive.ics.uci.edu/dataset/502/online+retail+ii
- Provenance: real retail transactions
- License: CC BY 4.0
- Redistribution: with attribution
- Intended use: orders/baskets
- Grain: must be confirmed per file from columns and source documentation
- Limitations: Profiles are bounded samples; semantic keys require source-specific review.
- Files: 1

### `online_retail_II.xlsx`

Size: 45622418 bytes. Profiled rows: 250000. Duplicates in profile: 2959.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| Invoice | object | 0.0 | 14439 |
| StockCode | object | 0.0 | 4226 |
| Description | object | 0.784 | 3941 |
| Quantity | int64 | 0.0 | 609 |
| InvoiceDate | datetime64[us] | 0.0 | 12589 |
| Price | float64 | 0.0 | 1014 |
| Customer ID | float64 | 22.048 | 3010 |
| Country | str | 0.0 | 32 |

## retail_fmcg_2024

- Status: `profiled`
- URL: https://www.kaggle.com/datasets/arannayavadebnath/retail-fmcg-sales-dataset-2024
- Provenance: synthetic
- License: not identified
- Redistribution: verify Kaggle dataset license
- Intended use: margin, stock and channel donor
- Grain: must be confirmed per file from columns and source documentation
- Limitations: Profiles are bounded samples; semantic keys require source-specific review.
- Files: 2

### `data\raw\retail_fmcg_2024\Indian FMCG Retail Sales  Customer  Inventory (2024).csv`

Size: 20462735 bytes. Profiled rows: 100000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| Invoice_ID | int64 | 0.0 | 99938 |
| Invoice_Date | str | 0.0 | 91057 |
| City | str | 0.0 | 8 |
| Store_Format | str | 0.0 | 3 |
| Category | str | 0.0 | 8 |
| Brand | str | 0.0 | 8 |
| Channel | str | 0.0 | 3 |
| Payment_Mode | str | 0.0 | 4 |
| Units | int64 | 0.0 | 5 |
| Cost_Price | float64 | 0.0 | 100000 |
| Selling_Price | float64 | 0.0 | 100000 |
| Revenue | float64 | 0.0 | 100000 |
| Cost | float64 | 0.0 | 100000 |
| Margin | float64 | 0.0 | 100000 |
| Margin_% | float64 | 0.0 | 100000 |
| Stock_On_Hand | int64 | 0.0 | 450 |
| Reorder_Level | int64 | 0.0 | 60 |
| Lead_Time_Days | int64 | 0.0 | 12 |
| Customer_Age | float64 | 40.081 | 47 |
| Customer_Gender | str | 5.048 | 3 |
| Loyalty_Flag | int64 | 0.0 | 2 |

### `data\raw\retail_fmcg_2024\Retail FMCG Sales Dataset - Overview.docx`

Size: 22010 bytes. Profiled rows: n/a. Duplicates in profile: n/a.

## retail_warehouse

- Status: `profiled`
- URL: https://www.kaggle.com/datasets/datarspectrum/retail-data-warehouse-12-table-1m-rows-dataset
- Provenance: synthetic educational
- License: not identified
- Redistribution: verify Kaggle dataset license
- Intended use: schema/cardinality reference
- Grain: must be confirmed per file from columns and source documentation
- Limitations: Profiles are bounded samples; semantic keys require source-specific review.
- Files: 12

### `data\raw\retail_warehouse\categories.csv`

Size: 308 bytes. Profiled rows: 30. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| category_id | int64 | 0.0 | 30 |
| category_name | str | 0.0 | 30 |

### `data\raw\retail_warehouse\customers.csv`

Size: 1188794 bytes. Profiled rows: 50000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| customer_id | int64 | 0.0 | 50000 |
| city | str | 0.0 | 4 |
| signup_date | str | 0.0 | 1827 |

### `data\raw\retail_warehouse\employees.csv`

Size: 12837 bytes. Profiled rows: 1000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| employee_id | int64 | 0.0 | 1000 |
| store_id | int64 | 0.0 | 100 |
| salary | int64 | 0.0 | 992 |

### `data\raw\retail_warehouse\order_items.csv`

Size: 15089776 bytes. Profiled rows: 250000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| order_item_id | int64 | 0.0 | 250000 |
| order_id | int64 | 0.0 | 169743 |
| product_id | int64 | 0.0 | 10000 |
| qty | int64 | 0.0 | 4 |
| price | int64 | 0.0 | 4900 |

### `data\raw\retail_warehouse\orders.csv`

Size: 8744243 bytes. Profiled rows: 250000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| order_id | int64 | 0.0 | 250000 |
| customer_id | int64 | 0.0 | 49670 |
| store_id | int64 | 0.0 | 100 |
| order_date | str | 0.0 | 1462 |
| promotion_id | int64 | 0.0 | 50 |

### `data\raw\retail_warehouse\payments.csv`

Size: 5615313 bytes. Profiled rows: 250000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| payment_id | int64 | 0.0 | 250000 |
| order_id | int64 | 0.0 | 250000 |
| amount | int64 | 0.0 | 19900 |

### `data\raw\retail_warehouse\products.csv`

Size: 158657 bytes. Profiled rows: 10000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| product_id | int64 | 0.0 | 10000 |
| category_id | int64 | 0.0 | 30 |
| supplier_id | int64 | 0.0 | 200 |
| price | int64 | 0.0 | 4268 |

### `data\raw\retail_warehouse\promotions.csv`

Size: 301 bytes. Profiled rows: 50. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| promotion_id | int64 | 0.0 | 50 |
| discount | int64 | 0.0 | 27 |

### `data\raw\retail_warehouse\returns.csv`

Size: 517411 bytes. Profiled rows: 30000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| return_id | int64 | 0.0 | 30000 |
| order_item_id | int64 | 0.0 | 29251 |
| refund | int64 | 0.0 | 4937 |

### `data\raw\retail_warehouse\shipments.csv`

Size: 6277977 bytes. Profiled rows: 250000. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| shipment_id | int64 | 0.0 | 250000 |
| order_id | int64 | 0.0 | 250000 |
| status | str | 0.0 | 3 |

### `data\raw\retail_warehouse\stores.csv`

Size: 994 bytes. Profiled rows: 100. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| store_id | int64 | 0.0 | 100 |
| city | str | 0.0 | 4 |

### `data\raw\retail_warehouse\suppliers.csv`

Size: 1762 bytes. Profiled rows: 200. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| supplier_id | int64 | 0.0 | 200 |
| country | str | 0.0 | 3 |

## supply_chain_inventory

- Status: `profiled`
- URL: https://www.kaggle.com/datasets/ziya07/high-dimensional-supply-chain-inventory-dataset
- Provenance: synthetic
- License: not identified
- Redistribution: verify Kaggle dataset license
- Intended use: inventory and lead-time donor
- Grain: must be confirmed per file from columns and source documentation
- Limitations: Profiles are bounded samples; semantic keys require source-specific review.
- Files: 1

### `data\raw\supply_chain_inventory\supply_chain_dataset1.csv`

Size: 6552486 bytes. Profiled rows: 91250. Duplicates in profile: 0.

| Column | Type | Null % | Unique |
|---|---:|---:|---:|
| Date | str | 0.0 | 365 |
| SKU_ID | str | 0.0 | 50 |
| Warehouse_ID | str | 0.0 | 5 |
| Supplier_ID | str | 0.0 | 10 |
| Region | str | 0.0 | 4 |
| Units_Sold | int64 | 0.0 | 58 |
| Inventory_Level | int64 | 0.0 | 781 |
| Supplier_Lead_Time_Days | int64 | 0.0 | 13 |
| Reorder_Point | int64 | 0.0 | 142 |
| Order_Quantity | int64 | 0.0 | 301 |
| Unit_Cost | float64 | 0.0 | 230 |
| Unit_Price | float64 | 0.0 | 227 |
| Promotion_Flag | int64 | 0.0 | 2 |
| Stockout_Flag | int64 | 0.0 | 1 |
| Demand_Forecast | float64 | 0.0 | 4736 |
