select promotion_id as promotion_key,* from {{ source('raw','promotions') }}

