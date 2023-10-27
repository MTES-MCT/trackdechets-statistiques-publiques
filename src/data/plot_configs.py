COLORS = ["#000091", "#5E2A2B", "#66673D", "#E4794A", "#60E0EB", "#009099"]

WEEKLY_BS_STATS_PLOT_CONFIGS = [
    {
        "column_counts": "creations",
        "column_quantity": "quantite_tracee",
        "counts_line_config": {
            "name": "État initial",
            "suffix": "traçés",
            "text_position": "top center",
        },
        "quantity_line_config": {
            "name": "Quantité initiale",
            "suffix": "tonnes tracées",
            "text_position": "top center",
        },
        "color": COLORS[0],
    },
    {
        "column_counts": "envois",
        "column_quantity": "quantite_envoyee",
        "counts_line_config": {
            "name": "Pris en charge par le transporteur",
            "suffix": "pris en charge par le transporteur",
            "text_position": "middle top",
        },
        "quantity_line_config": {
            "name": "Prise en charge par le transporteur",
            "suffix": "tonnes prises en charge par le transporteur",
            "text_position": "middle top",
        },
        "color": COLORS[1],
        "visible": "legendonly",
    },
    {
        "column_counts": "receptions",
        "column_quantity": "quantite_recue",
        "counts_line_config": {
            "name": "Reçu par le destinataire",
            "suffix": "reçus par le destinataire",
            "text_position": "middle bottom",
        },
        "quantity_line_config": {
            "name": "Reçue par le destinataire",
            "suffix": "tonnes reçues par le destinataire",
            "text_position": "middle bottom",
        },
        "color": COLORS[2],
    },
    {
        "column_counts": "traitements",
        "column_quantity": "quantite_traitee",
        "counts_line_config": {
            "name": "Traité",
            "suffix": "marqués comme traités",
            "text_position": "bottom center",
        },
        "quantity_line_config": {
            "name": "Traitée",
            "suffix": "tonnes traitées",
            "text_position": "bottom center",
        },
        "color": COLORS[3],
    },
    {
        "column_counts": "traitements_operations_non_finales",
        "column_quantity": "quantite_traitee_operations_non_finales",
        "counts_line_config": {
            "name": "Traité (traitement intermédiaire)",
            "suffix": "en traitement intermédiaire",
            "text_position": "bottom center",
        },
        "color": COLORS[4],
        "quantity_line_config": {
            "name": "Traitée (traitement intermédiaire)",
            "suffix": "tonnes traitées en traitement intermédiaire",
            "text_position": "bottom center",
        },
        "visible": "legendonly",
    },
    {
        "column_counts": "traitements_operations_finales",
        "column_quantity": "quantite_traitee_operations_finales",
        "counts_line_config": {
            "name": "Traité (traitement final)",
            "suffix": "en traitement final",
            "text_position": "bottom center",
        },
        "color": COLORS[5],
        "quantity_line_config": {
            "name": "Traitée (traitement final)",
            "suffix": "tonnes traitées en traitement final",
            "text_position": "bottom center",
        },
        "visible": "legendonly",
    },
]

WEEKLY_BSFF_STATS_PLOT_CONFIGS = [
    {
        "column_counts": "creations_bordereaux",
        "column_quantity": "quantite_tracee",
        "counts_line_config": {
            "name": "État initial",
            "suffix": "traçés",
            "text_position": "top center",
        },
        "quantity_line_config": {
            "name": "Quantité initiale",
            "suffix": "tonnes tracées",
            "text_position": "top center",
        },
        "color": COLORS[0],
    },
    {
        "column_counts": "envois_bordereaux",
        "column_quantity": "quantite_envoyee",
        "counts_line_config": {
            "name": "Pris en charge par le transporteur",
            "suffix": "pris en charge par le transporteur",
            "text_position": "middle top",
        },
        "quantity_line_config": {
            "name": "Prise en charge par le transporteur",
            "suffix": "tonnes prises en charge par le transporteur",
            "text_position": "middle top",
        },
        "color": COLORS[1],
        "visible": "legendonly",
    },
    {
        "column_counts": "receptions_bordereaux",
        "column_quantity": "quantite_recue",
        "counts_line_config": {
            "name": "Reçu par le destinataire",
            "suffix": "reçus par le destinataire",
            "text_position": "middle bottom",
        },
        "quantity_line_config": {
            "name": "Reçue par le destinataire",
            "suffix": "tonnes reçues par le destinataire",
            "text_position": "middle bottom",
        },
        "color": COLORS[2],
    },
    {
        "column_counts": "traitements_contenants",
        "column_quantity": "quantite_traitee",
        "counts_line_config": {
            "name": "Traité",
            "suffix": "marqués comme traités",
            "text_position": "bottom center",
        },
        "quantity_line_config": {
            "name": "Traitée",
            "suffix": "tonnes traitées",
            "text_position": "bottom center",
        },
        "color": COLORS[3],
    },
    {
        "column_counts": "traitements_contenants_operations_non_finales",
        "column_quantity": "quantite_traitee_operations_non_finales",
        "counts_line_config": {
            "name": "Traité (traitement intermédiaire)",
            "suffix": "en traitement intermédiaire",
            "text_position": "bottom center",
        },
        "quantity_line_config": {
            "name": "Traitée (traitement intermédiaire)",
            "suffix": "tonnes traitées en traitement intermédiaire",
            "text_position": "bottom center",
        },
        "color": COLORS[4],
        "visible": "legendonly",
    },
    {
        "column_counts": "traitements_contenants_operations_finales",
        "column_quantity": "quantite_traitee_operations_finales",
        "counts_line_config": {
            "name": "Traité (traitement final)",
            "suffix": "en traitement final",
            "text_position": "bottom center",
        },
        "quantity_line_config": {
            "name": "Traitée (traitement final)",
            "suffix": "tonnes traitées en traitement final",
            "text_position": "bottom center",
        },
        "color": COLORS[5],
        "visible": "legendonly",
    },
]
