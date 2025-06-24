"""This modules contains all the functions to create the Plotly figure needed or the App."""

from datetime import datetime, timedelta

import plotly.graph_objects as go
import polars as pl

from data.plot_configs import (
    WEEKLY_BS_STATS_PLOT_CONFIGS,
    WEEKLY_BSFF_PACKAGINGS_STATS_PLOT_CONFIGS,
    WEEKLY_BSFF_STATS_PLOT_CONFIGS,
)

from .page_utils import break_long_line, format_number

gridcolor = "#ccc"


def create_weekly_created_figure(data: pl.DataFrame, stat_column: str) -> go.Figure:
    """Creates the figure showing number of weekly created companies, users...

    Parameters
    ----------
    data: DataFrame
        DataFrame containing the data to plot. Must have 'id' and 'at' columns.

    Returns
    -------
    Plotly Figure Object
        Figure object ready to be plotted.
    """
    data = data.sort("semaine")
    data = data.to_dict(as_series=False)

    texts = []
    texts += [""] * (len(data[stat_column]) - 1) + [format_number(data[stat_column][-1])]

    hovertexts = [
        f"Semaine du {at:%d/%m} au {at + timedelta(days=6):%d/%m}<br><b>{format_number(count)}</b> créations"
        for at, count in zip(data["semaine"], data[stat_column])
    ]

    fig = go.Figure(
        [
            go.Scatter(
                x=data["semaine"],
                y=data[stat_column],
                text=texts,
                mode="lines+markers+text",
                hovertext=hovertexts,
                hoverinfo="text",
                textposition="middle right",
                textfont_size=15,
                line_shape="spline",
                line_smoothing=0.3,
                line_width=3,
            )
        ]
    )

    # handle ticks to start at first day of the first complete week of the year
    min_x = min(data["semaine"])
    max_x = max(data["semaine"])

    current_year = max(data["semaine"]).year
    breaks = []
    for i in range(1, min_x.day):
        breaks.append(datetime(current_year, 1, i))

    fig.update_layout(
        xaxis_title="Semaine de création",
        showlegend=False,
        paper_bgcolor="#fff",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, r=50, l=25),
    )
    fig.update_yaxes(side="right")

    delta = max_x - min_x

    fig.update_xaxes(
        range=[min_x - max(delta * 0.05, timedelta(days=2)), max_x + delta * 0.1],
        rangebreaks=[dict(values=breaks)],
        gridcolor="#ccc",
    )
    fig.update_yaxes(gridcolor="#ccc")
    return fig


def create_weekly_scatter_figure(
    bs_weekly_data: pl.DataFrame,
    metric_type: str,
    bs_type: str,
) -> go.Figure:
    """Creates a scatter figure showing the weekly number of 'bordereaux' by status (created, sent..)

    Parameters
    ----------
    bs_weekly_data: DataFrame
        DataFrame containing the count and quantities for a particular
        type of 'bordereau'.
    bs_type: str
        Type of 'bordereau'. Eg : BSDD, BSDA...
    lines_configs: list of dicts
        Configuration for the different traces. One config per line in the resulting figure.
    Returns
    -------
    Plotly Figure Object
        Figure object ready to be plotted.
    """

    if len(bs_weekly_data) == 0:
        return go.Figure()

    match bs_type:
        case "BSFF":
            plot_configs = WEEKLY_BSFF_STATS_PLOT_CONFIGS
        case "BSFF PACKAGINGS":
            plot_configs = WEEKLY_BSFF_PACKAGINGS_STATS_PLOT_CONFIGS
        case _:
            plot_configs = WEEKLY_BS_STATS_PLOT_CONFIGS

    scatter_list = []

    y_title = None
    legend_title = "Statut du bordereau :" if bs_type != "BSFF PACKAGINGS" else "Statut du contenant:"
    if metric_type == "quantity":
        legend_title = "Statut :"
        y_title = "Quantité (en tonnes)"

    min_x = None
    max_x = None
    for config in plot_configs:
        if metric_type == "counts" and "column_counts" not in config:
            continue

        if metric_type == "quantity" and "column_quantity" not in config:
            continue

        column_to_use = config["column_counts"] if metric_type == "counts" else config["column_quantity"]
        data = bs_weekly_data

        if len(data) == 0:
            continue

        # Filter out data from previous year:
        current_year = data.select("semaine").max().item().year
        data = data.filter(pl.col("semaine").dt.year() == current_year)
        data_without_nulls = data.drop_nulls(column_to_use)

        data = data.to_dict(as_series=False)

        min_at = data["semaine"][0]
        if min_x is None or min_at < min_x:
            min_x = min_at

        max_at = data["semaine"][-1]
        if max_x is None or max_at > max_x:
            max_x = max_at

        name = config[f"{metric_type}_line_config"]["name"]
        suffix = config[f"{metric_type}_line_config"]["suffix"]

        # Creates a list of text to only show value on last point of the line
        texts = []
        last_value = None

        if len(data_without_nulls) > 0:
            last_value = data_without_nulls[-1, column_to_use]
        texts = [""] * (len(data_without_nulls) - 1) if len(data_without_nulls) > 1 else []
        texts += [format_number(last_value)]

        if metric_type == "counts":
            to_add_str = bs_type

            if bs_type == "BSFF PACKAGINGS":  # Handle the case of BSFF that shows packagings for the processing counts
                to_add_str = "contenants"

            suffix = f"{to_add_str} {suffix}"

        hover_texts = [
            f"Semaine du {semaine:%d/%m} au {semaine + timedelta(days=6):%d/%m}<br><b>{format_number(value, 2)}</b> {suffix}"
            for semaine, value in zip(data["semaine"], data[column_to_use])
        ]

        scatter_list.append(
            go.Scatter(
                x=data["semaine"],
                y=data[column_to_use],
                mode="lines+text",
                name=name,
                text=texts,
                textfont_size=15,
                textfont_color=config["color"],
                line_color=config["color"],
                textposition="middle right",
                hovertext=hover_texts,
                hoverinfo="text",
                line_shape="spline",
                line_smoothing=0.3,
                line_width=3,
                visible=config.get("visible", True),
            )
        )

    fig = go.Figure(scatter_list)

    fig.update_layout(
        paper_bgcolor="#fff",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=45, r=90, l=5),
        legend=dict(
            orientation="h",
            y=1.15,
            x=-0.06,
            font_size=13,
            itemwidth=40,
            bgcolor="rgba(0,0,0,0)",
            title=legend_title,
        ),
        uirevision=True,
    )

    delta = max_x - min_x

    # handle ticks to start at first day of the first complete week of the year
    breaks = []
    for i in range(1, min_x.day):
        breaks.append(datetime(current_year, 1, i))

    fig.update_xaxes(
        range=[min_x - delta * 0.05, max_x + delta * 0.1],
        rangebreaks=[dict(values=breaks)],
        gridcolor=gridcolor,
    )
    fig.update_yaxes(side="right", title=y_title, gridcolor=gridcolor)

    return fig


def create_weekly_quantity_processed_figure(
    quantity_recovered: pl.Series,
    quantity_destroyed: pl.Series,
    date_interval: tuple[datetime, datetime] | None = None,
) -> go.Figure:
    """Creates the figure showing the weekly waste quantity processed by type of process (destroyed or recovered).

    Parameters
    ----------
    quantity_recovered: Series
        Series containing the quantity of recovered waste aggregated by week.
    quantity_destroyed: Series
        Series containing the quantity of destroyed waste aggregated by week.

    Returns
    -------
    Plotly Figure Object
        Figure object ready to be plotted.
    """

    data_conf = [
        {
            "data": quantity_recovered,
            "name": "Déchets valorisés",
            "text": "Semaine du {0:%d/%m} au {1:%d/%m}<br><b>{2}</b> tonnes de déchets valorisées",
            "color": "#66673D",
        },
        {
            "data": quantity_destroyed,
            "name": "Déchets éliminés",
            "text": "Semaine du {0:%d/%m} au {1:%d/%m}<br><b>{2}</b> tonnes de déchets éliminées",
            "color": "#5E2A2B",
        },
    ]

    min_x, max_x = None, None
    traces = []
    for conf in data_conf:
        data = conf["data"]

        # Filter out data from previous year:
        current_year = data.select("semaine").max().item().year

        date_filter = pl.col("semaine").dt.year() == current_year
        if date_interval is not None:
            date_filter = pl.col("semaine").is_between(*date_interval, closed="left")

        data = data.filter(date_filter)
        data = data.sort("semaine")

        data = data.to_dict(as_series=False)

        min_at = data["semaine"][0]
        if min_x is None or min_at < min_x:
            min_x = min_at

        max_at = data["semaine"][-1]
        if max_x is None or max_at > max_x:
            max_x = max_at

        hover_texts = [
            conf["text"].format(
                processed_at,
                processed_at + timedelta(days=6),
                format_number(quantity),
            )
            for processed_at, quantity in zip(data["semaine"][:-1], data["quantite_traitee"][:-1])
        ]

        # Handle case when last data point is last week of the year
        last_point_date = data["semaine"][-1]
        last_point_value = data["quantite_traitee"][-1]
        if (last_point_date + timedelta(days=6)).year != current_year:
            last_point = datetime(current_year, 12, 31)
            hover_texts.append(
                f"Période du {last_point_date:%d/%m} au {last_point:%d/%m}<br><b>{format_number(last_point_value)}</b> tonnes de {conf['name'].lower()}."
            )
        else:
            hover_texts.append(
                f"Semaine du {last_point_date:%d/%m} au {last_point_date + timedelta(days=6):%d/%m}<br><b>{format_number(last_point_value)}</b> {conf['name'].lower()}"
            )

        traces.append(
            go.Bar(
                x=data["semaine"],
                y=data["quantite_traitee"],
                name=conf["name"],
                hovertext=hover_texts,
                hoverinfo="text",
                texttemplate="%{y:.2s} tonnes",
                marker_color=conf["color"],
                width=1000 * 3600 * 24 * 6,
            )
        )

    fig = go.Figure(data=traces)

    max_value = sum([conf["data"]["quantite_traitee"].max() or 0 for conf in data_conf])

    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="Semaine de traitement",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1,
            xanchor="left",
            x=0,
            title="Type de traitement :",
            bgcolor="rgba(0,0,0,0)",
        ),
        margin=dict(t=30, r=70, l=20),
        barmode="stack",
        yaxis_title="Quantité (en tonnes)",
        yaxis_range=[0, max_value * 1.1],
        modebar_bgcolor="rgba(0,0,0,0)",
        modebar_color="rgba(146, 146, 146, 0.7)",
        modebar_activecolor="rgba(146, 146, 146, 0.7)",
    )
    fig.update_yaxes(side="right")

    # handle ticks to start at first day of the first complete week of the year
    breaks = []
    for i in range(1, min_x.day):
        breaks.append(datetime(current_year, 1, i))

    fig.update_xaxes(
        range=[min_x - timedelta(days=7), max_x + timedelta(days=7)],
        rangebreaks=[dict(values=breaks)],
        gridcolor=gridcolor,
    )
    fig.update_yaxes(gridcolor=gridcolor)
    return fig


def create_quantity_processed_sunburst_figure(
    weekly_waste_processed_data_df: pl.DataFrame,
    waste_codes_data: pl.DataFrame,
    date_interval: tuple[datetime, datetime],
) -> go.Figure:
    """Creates the figure showing the weekly waste quantity processed by type of processing operation (destroyed or recovered).

    Parameters
    ----------
    weekly_waste_processed_data_df: DataFrame
       DataFrame with weekly quantity of processed waste by processing operation code.
    waste_codes_data: DataFrame
        DataFrame containing the description for each processing operation code.

    Returns
    -------
    Plotly Figure Object
        Sunburst Figure object ready to be plotted.
    """
    processing_operation_codes_descriptions = {e["code"]: e["description"] for e in waste_codes_data.to_dicts()}

    agg_data = (
        weekly_waste_processed_data_df.filter(
            pl.col("semaine").is_between(*date_interval, closed="left") & (pl.col("code_operation") != "")
        )
        .group_by(["code_operation"])
        .agg(pl.col("type_operation").max(), pl.col("quantite_traitee").sum())
    )
    total_data = agg_data.group_by("type_operation").agg(pl.col("quantite_traitee").sum()).sort("type_operation")

    agg_data_recycled = agg_data.filter(pl.col("type_operation") == "Déchet valorisé").sort("quantite_traitee")
    agg_data_eliminated = agg_data.filter(pl.col("type_operation") == "Déchet éliminé").sort("quantite_traitee")

    agg_data_recycled_other = agg_data_recycled.filter(
        (pl.col("quantite_traitee") / pl.col("quantite_traitee").sum()) <= 0.12
    )
    agg_data_eliminated_other = agg_data_eliminated.filter(
        (pl.col("quantite_traitee") / pl.col("quantite_traitee").sum()) <= 0.21
    )

    agg_data_recycled_other_quantity = agg_data_recycled_other["quantite_traitee"].sum()
    agg_data_eliminated_other_quantity = agg_data_eliminated_other["quantite_traitee"].sum()

    other_processing_operations_codes = (
        pl.concat(
            [
                agg_data_recycled_other.select("code_operation"),
                agg_data_eliminated_other.select("code_operation"),
            ]
        )
        .unique()
        .to_series()
    )
    agg_data_without_other = agg_data.filter(
        pl.col("code_operation").is_in(other_processing_operations_codes).not_()
    ).sort("quantite_traitee", descending=True)

    agg_data_without_other = agg_data_without_other.with_columns(
        pl.col("type_operation")
        .map_elements(lambda x: "rgb(102, 103, 61, 0.7)" if x == "Déchet valorisé" else "rgb(94, 42, 43, 0.7)")
        .alias("colors")
    )

    total_data = total_data.to_dict(as_series=False)
    agg_data_without_other = agg_data_without_other.to_dict(as_series=False)
    ids = (
        total_data["type_operation"]
        + agg_data_without_other["code_operation"]
        + ["Autres opérations de valorisation", "Autres opérations d'élimination'"]
    )

    labels = total_data["type_operation"] + agg_data_without_other["code_operation"] + ["Autre"] * 2
    parents = ["", ""] + agg_data_without_other["type_operation"] + ["Déchet valorisé", "Déchet éliminé"]
    values = (
        total_data["quantite_traitee"]
        + agg_data_without_other["quantite_traitee"]
        + [agg_data_recycled_other_quantity, agg_data_eliminated_other_quantity]
    )
    colors = (
        ["rgb(102, 103, 61, 1)", "rgb(94, 42, 43, 1)"]
        + agg_data_without_other["colors"]
        + ["rgb(102, 103, 61, 0.7)", "rgb(94, 42, 43, 0.7)"]
    )

    hover_text_template = "{code} : {description}<br><b>{quantity}t</b> traitées"
    hover_texts = (
        [
            f"<b>{format_number(e)}t</b> {index.split(' ')[1]}es"
            if index != "Autre"
            else f"<b>{format_number(e)}t</b>"
            for index, e in zip(total_data["type_operation"], total_data["quantite_traitee"])
        ]
        + [
            hover_text_template.format(
                code=processing_operation,
                description=processing_operation_codes_descriptions.get(
                    processing_operation, "Autre opération de traitement"
                ),
                quantity=format_number(quantity),
            )
            for processing_operation, quantity in zip(
                agg_data_without_other["code_operation"],
                agg_data_without_other["quantite_traitee"],
            )
        ]
        + [
            f"Autres opérations de traitement<br><b>{format_number(e)}t</b> traitées"
            for e in [
                agg_data_recycled_other_quantity,
                agg_data_eliminated_other_quantity,
            ]
        ]
    )

    fig = go.Figure(
        go.Sunburst(
            ids=ids,
            labels=labels,
            parents=parents,
            values=values,
            marker_colors=colors,
            marker_line_color="rgba(238, 238, 238, 1)",
            marker_line_width=2,
            branchvalues="total",
            texttemplate="%{label} - <b>%{percentRoot}</b>",
            hovertext=hover_texts,
            hoverinfo="text",
            sort=False,
            insidetextorientation="horizontal",
            insidetextfont_size=15,
        )
    )
    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        modebar_bgcolor="rgba(0,0,0,0)",
        modebar_color="rgba(146, 146, 146, 0.7)",
        modebar_activecolor="rgba(146, 146, 146, 0.7)",
    )

    return fig


def create_treemap_companies_figure(data_with_naf: pl.DataFrame, year: int, use_quantity: bool = False) -> go.Figure:
    """Creates the figure showing the number of companies by NAF category.

    Parameters
    ----------
    data_with_naf: DataFrame
        DataFrame containing data, including NAF categories to aggregate.
    use_quantity: boolean
        IF true, aggregation is done on column `quantity`. Default False.

    Returns
    -------
    Plotly Figure Object
        Figure object ready to be plotted.
    """

    colors = pl.DataFrame(
        [
            [
                "Activités de services administratifs et de soutien",
                "rgba(97, 49, 107, 1)",
            ],
            [
                "Arts, spectacles et activités récréatives",
                "rgba(112, 111, 211, 1)",
            ],
            [
                "Activités financières et d'assurance",
                "rgba(247, 241, 227, 1)",
            ],
            [
                "Hébergement et restauration",
                "rgba(52, 172, 224, 1)",
            ],
            [
                "Santé humaine et action sociale",
                "rgba(51, 217, 178, 1)",
            ],
            [
                "Enseignement",
                "rgba(44, 44, 84, 1)",
            ],
            [
                "Construction",
                "rgba(71, 71, 135, 1)",
            ],
            [
                "Transports et entreposage",
                "rgba(113, 87, 87, 1)",
            ],
            [
                "Autres activités de services",
                "rgba(255, 121, 63, 1)",
            ],
            [
                "Activités des ménages en tant qu'employeurs ; activités indifférenciées des ménages en tant que producteurs de biens et services pour usage propre",
                "rgba(33, 140, 116, 1)",
            ],
            [
                "Information et communication",
                "rgba(255, 82, 82, 1)",
            ],
            [
                "Industrie manufacturière",
                "rgba(34, 112, 147, 1)",
            ],
            [
                "Activités spécialisées, scientifiques et techniques",
                "rgba(209, 204, 192, 1)",
            ],
            [
                "Administration publique",
                "rgba(255, 177, 66, 1)",
            ],
            [
                "Production et distribution d'eau ; assainissement, gestion des déchets et dépollution",
                "rgba(255, 218, 121, 1)",
            ],
            [
                "Commerce ; réparation d'automobiles et de motocycles",
                "rgba(179, 57, 57, 1)",
            ],
            [
                "Activités immobilières",
                "rgba(100, 98, 93, 1)",
            ],
            [
                "Industries extractives",
                "rgba(204, 142, 53, 1)",
            ],
            [
                "Production et distribution d'électricité, de gaz, de vapeur et d'air conditionné",
                "rgba(204, 174, 98, 1)",
            ],
            [
                "Activités extra-territoriales",
                "rgba(205, 97, 51, 1)",
            ],
            [
                "Agriculture, sylviculture et pêche",
                "rgba(77, 52, 42, 1)",
            ],
            [
                "NAF inconnu",
                "rgba(183, 21, 64, 1)",
            ],
        ],
        schema=["libelle_section", "color"],
    )

    df = data_with_naf.filter(pl.col("annee") == year)

    df = df.fill_null("NAF inconnu")

    # Init values

    stat_col = "nombre_etablissements"
    value_expr = pl.col(stat_col).sum().alias("value")
    value_suffix = pl.lit("</b>")
    hover_expr_str = "</b> établissements inscrits dans la {label} NAF "
    hover_expr_lit_nulls = pl.lit("</b> établissements inscrits ayant un code NAF inconnu ")
    hover_expr_lit_end = pl.lit("%</b> du total des établissements inscrits.<extra></extra>")
    unit = ""
    if use_quantity:
        stat_col = "quantite_produite"
        value_expr = pl.col(stat_col).sum().alias("value")
        value_suffix = pl.lit("t</b>")
        hover_expr_str = " tonnes</b> produites par des établissements inscrits dans la {label} NAF "
        hover_expr_lit_nulls = pl.lit(" tonnes</b> produites par des établissements ayant un code NAF inconnu ")
        hover_expr_lit_end = pl.lit("%</b> de la quantité totale produite.<extra></extra>")
        unit = "t"

    total = df.select(stat_col).sum().item()

    labels = [f"Tous les établissements - <b>{total / 1000:.2f}k{unit}</b>"]
    hover_texts = [f"Tous les établissements - <b>{total / 1000:.2f}k{unit}</b><extra></extra>"]

    categories = ["sous_classe", "classe", "groupe", "division", "section"]

    # build dfs at each granularity
    dfs = []
    for i, cat in enumerate(categories):
        temp_df = df.drop_nulls(f"libelle_{cat}")

        agg_exprs = [
            value_expr,
            pl.col(f"libelle_{cat}").max(),
        ]

        id_sep = "#"

        col_names_to_agg = []
        if i < (len(categories) - 1):
            # Create the expression to get the value of higher pivot dimensions
            # (e.g for "code_sous_classe" it will take the max of "code_classe" and upper hierarchies)
            for tmp_cat in reversed(categories[i + 1 :]):
                tmp_col_name = f"libelle_{tmp_cat}"
                agg_exprs.append(pl.col(tmp_col_name).max())
                col_names_to_agg.append(tmp_col_name)
        col_names_to_agg.append(f"libelle_{cat}")

        temp_df = temp_df.group_by(f"code_{cat}", maintain_order=True).agg(agg_exprs)

        id_expr = pl.concat_str(
            [pl.lit("Tous les établissements")] + [pl.col(e) for e in col_names_to_agg], separator=id_sep
        )
        temp_df = temp_df.with_columns(ids=id_expr)

        temp_colors = colors
        temp_df = temp_df.join(temp_colors, on="libelle_section", how="left")

        parent_exp = (
            pl.col("ids")
            .str.split(id_sep)
            .list.reverse()
            .list.slice(1)
            .list.reverse()
            .list.join(id_sep)
            .alias("parents")
        )

        labels_expr = pl.concat_str(
            [
                pl.col(f"libelle_{cat}").map_elements(lambda x: break_long_line(x, 14)),
                pl.lit(" - <b>"),
                pl.col("value").map_elements(lambda x: f"{x / 1000:.0f}k" if x > 1000 else format_number(x, 1)),
                value_suffix,
            ]
        ).alias("labels")

        hover_expr_prefix = pl.lit(hover_expr_str.format(label=cat.replace("_", " ")))
        hover_expr_code = pl.col(f"code_{cat}")
        hover_expr_label = pl.format(" - <i>{}</i>", pl.col(f"libelle_{cat}"))
        if cat == "section":
            when_expr = pl.when(pl.col("code_section") == "NAF inconnu")
            hover_expr_prefix = when_expr.then(hover_expr_lit_nulls).otherwise(hover_expr_prefix)
            hover_expr_code = when_expr.then(pl.lit("")).otherwise(hover_expr_code)
            hover_expr_label = when_expr.then(pl.lit("")).otherwise(hover_expr_label)

        hover_expr = pl.concat_str(
            [
                pl.lit("<b>"),
                pl.col("value").map_elements(format_number),
                hover_expr_prefix,
                hover_expr_code,
                hover_expr_label,
                pl.lit("<br>soit <b>"),
                (100 * pl.col("value") / total).round(2).cast(pl.Utf8),
                hover_expr_lit_end,
            ]
        ).alias("hover_texts")

        dfs.append(
            temp_df.with_columns([labels_expr, hover_expr, parent_exp]).select(
                [
                    pl.col("ids"),
                    pl.col("labels"),
                    pl.col("parents"),
                    pl.col("value"),
                    pl.col("hover_texts"),
                    pl.col("color"),
                ]
            )
        )

    # Build plotly necessaries lists
    ids = ["Tous les établissements"]
    parents = [""]
    values = [total]
    colors = ["rgba(238, 238, 238, 0)"]
    for df in reversed(dfs):
        json = df.to_dict(as_series=False)
        ids.extend(json["ids"])
        labels.extend(json["labels"])
        parents.extend(json["parents"])
        values.extend(json["value"])
        hover_texts.extend(json["hover_texts"])
        colors.extend(json["color"])

    fig = go.Figure(
        go.Treemap(
            ids=ids,
            labels=labels,
            values=values,
            parents=parents,
            hovertemplate=hover_texts,
            marker_colors=colors,
            branchvalues="total",
            pathbar_thickness=35,
            textposition="middle center",
            tiling_packing="squarify",
            insidetextfont_size=300,
            pathbar_textfont_size=50,
            tiling_pad=7,
            maxdepth=2,
            marker_line_width=0,
            marker_depthfade="reversed",
            marker_pad={"t": 80, "r": 20, "b": 20, "l": 20},
        )
    )
    fig.update_layout(
        margin={"l": 15, "r": 15, "t": 35, "b": 25},
        height=800,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        modebar_bgcolor="rgba(0,0,0,0)",
        modebar_color="rgba(146, 146, 146, 0.7)",
        modebar_activecolor="rgba(146, 146, 146, 0.7)",
    )
    return fig
