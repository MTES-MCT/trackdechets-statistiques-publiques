SELECT id,
    "created_at"
FROM "trusted_zone_trackdechets"."user"
WHERE "is_active" = True
    and "created_at" <= CURRENT_DATE - cast(
        extract(
            dow
            FROM CURRENT_DATE
        ) AS int
    )