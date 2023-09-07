select id,
    "created_at",
    "is_draft",
    "transporter_transport_taken_over_at" as "sent_at",
    "destination_reception_date" as "received_at",
    "destination_operation_signature_date" as "processed_at",
    "status",
    case
        when "destination_reception_weight" > 60 then "destination_reception_weight" / 1000
        else "destination_reception_weight"
    END as "quantity",
    "destination_operation_code" as "processing_operation",
    "waste_code",
    "emitter_company_siret" as "emitter_siret",
    emitter_departement,
    emitter_region,
    emitter_naf,
    destination_company_siret,
    destination_departement,
    destination_region,
    destination_naf
from "refined_zone_enriched"."bsff_enriched"
where "is_deleted" = false
    and "created_at" >= '2022-01-03'
    /* First day of the first week of the year */
    and "created_at" <= CURRENT_DATE - cast(
        extract(
            dow
            from CURRENT_DATE
        ) as int
    )
    /* Due to pandas timestamp limitations */
    and (
        (
            "transporter_transport_taken_over_at" >= '1970-01-01'
            and "transporter_transport_taken_over_at" < '2262-04-11'
        )
        or "transporter_transport_taken_over_at" is null
    )
    and (
        (
            "destination_reception_date" >= '1970-01-01'
            and "destination_reception_date" < '2262-04-11'
        )
        or "destination_reception_date" is null
    )
    and (
        (
            "destination_operation_signature_date" >= '1970-01-01'
            and "destination_operation_signature_date" < '2262-04-11'
        )
        or "destination_operation_signature_date" is null
    )