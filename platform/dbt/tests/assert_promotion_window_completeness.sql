select *
from {{ ref('mart_promotion_performance') }}
where
    pre_window_complete != (pre_observed_days = pre_expected_days)
    or during_window_complete != (during_observed_days = during_expected_days)
    or post_window_complete != (post_observed_days = post_expected_days)
    or (not pre_window_complete and pre_realized_units is not null)
    or (not during_window_complete and during_realized_units is not null)
    or (not post_window_complete and post_realized_units is not null)
