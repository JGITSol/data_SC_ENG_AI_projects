{{
    config(
        materialized='table',
        tags=['marts', 'facts']
    )
}}

WITH trips AS (
    SELECT * FROM {{ ref('stg_trips') }}
),

final AS (
    SELECT
        {{ dbt_utils.generate_surrogate_key(['t.pickup_datetime', 't.vendor_id', 't.pickup_location_id']) }} AS trip_id,
        t.vendor_id,
        t.pickup_location_id,
        t.dropoff_location_id,
        t.pickup_datetime,
        t.dropoff_datetime,
        EXTRACT(EPOCH FROM (t.dropoff_datetime - t.pickup_datetime)) / 60 AS trip_duration_minutes,
        t.trip_distance_miles,
        t.passenger_count,
        CASE 
            WHEN trip_duration_minutes > 0 
            THEN t.trip_distance_miles / (trip_duration_minutes / 60.0)
            ELSE NULL 
        END AS average_speed_mph,
        EXTRACT(HOUR FROM t.pickup_datetime) AS pickup_hour,
        EXTRACT(DOW FROM t.pickup_datetime) AS pickup_day_of_week,
        DATE(t.pickup_datetime) AS pickup_date,
        CASE 
            WHEN EXTRACT(DOW FROM t.pickup_datetime) IN (0, 6) THEN TRUE 
            ELSE FALSE 
        END AS is_weekend,
        t.fare_amount,
        t.extra_charges,
        t.mta_tax,
        t.tip_amount,
        t.tolls_amount,
        t.improvement_surcharge,
        t.congestion_surcharge,
        t.total_amount,
        CASE 
            WHEN t.fare_amount > 0 
            THEN (t.tip_amount / t.fare_amount) * 100 
            ELSE 0 
        END AS tip_percentage,
        t.processed_at,
        CURRENT_TIMESTAMP AS dbt_updated_at
    FROM trips t
)

SELECT * FROM final
