from dataclasses import dataclass, field
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem


@dataclass
class PySideViewContext:
    username: str
    auth_controller: Any
    player_catalog_controller: Any
    player_comparison_controller: Any
    favorite_controller: Any
    round_controller: Any
    lineup_controller: Any
    ranking_controller: Any
    market_controller: Any
    jogadores_catalogo: list = field(default_factory=list)
    jogadores_disponiveis: list = field(default_factory=list)
    jogadores_mercado: list = field(default_factory=list)
    jogadores_escalados: list = field(default_factory=list)
    jogadores_favoritos: list = field(default_factory=list)
    clubes_favoritos: list = field(default_factory=list)
    capitao: Any = None
    sort_directions: dict = field(default_factory=dict)


def table(headers):
    widget = QTableWidget(0, len(headers))
    widget.setHorizontalHeaderLabels(headers)
    widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
    widget.verticalHeader().setVisible(False)
    widget.setAlternatingRowColors(True)
    return widget


def fill_table(widget, rows):
    widget.setRowCount(len(rows))
    for row_index, values in enumerate(rows):
        for column_index, value in enumerate(values):
            item = QTableWidgetItem(str(value))
            if column_index in {0, 3, 4}:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            widget.setItem(row_index, column_index, item)
    widget.resizeColumnsToContents()


def fill_players_table(widget, jogadores):
    fill_table(
        widget,
        [
            [
                jogador.api_id or "",
                jogador.nome or "",
                jogador.nome_time or "",
                jogador.posicao or "",
                f"{float(jogador.valor_mercado or 0):.2f}",
            ]
            for jogador in jogadores
        ],
    )


def selected_rows(widget):
    return sorted({item.row() for item in widget.selectedItems()})


def next_sort_direction(context, key):
    reverse = not context.sort_directions.get(key, False)
    context.sort_directions[key] = reverse
    return reverse


def sortable_value(value):
    if value is None:
        return (1, "")

    if isinstance(value, (int, float)):
        return (0, value)

    try:
        return (0, float(value))
    except (TypeError, ValueError):
        return (0, str(value).casefold())
