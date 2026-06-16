from dataclasses import dataclass, field
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QTableWidget, QTableWidgetItem


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
    user_profile_controller: Any
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
    widget.setShowGrid(False)
    widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    widget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
    widget.setWordWrap(False)
    widget.setCornerButtonEnabled(False)
    widget.setProperty("role", "data-table")
    widget.horizontalHeader().setHighlightSections(False)
    widget.horizontalHeader().setMinimumSectionSize(72)
    widget.horizontalHeader().setStretchLastSection(False)
    widget.verticalHeader().setDefaultSectionSize(36)
    _apply_column_resize_modes(widget)
    return widget


def fill_table(widget, rows):
    widget.setRowCount(len(rows))
    headers = [_normalized_header(widget.horizontalHeaderItem(index).text()) for index in range(widget.columnCount())]
    for row_index, values in enumerate(rows):
        for column_index, value in enumerate(values):
            item = QTableWidgetItem(str(value))
            if headers[column_index] in CENTERED_HEADERS:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            elif headers[column_index] in RIGHT_ALIGNED_HEADERS:
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            widget.setItem(row_index, column_index, item)
    _apply_column_resize_modes(widget)


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


COMPACT_HEADERS = {
    "id",
    "pos",
    "min",
    "tipo",
    "status",
    "rodada",
    "valor",
    "capitao",
    "pontuacao",
    "jogadores",
    "placar",
}

CENTERED_HEADERS = {
    "id",
    "pos",
    "min",
    "status",
    "rodada",
    "capitao",
    "jogadores",
    "placar",
}

RIGHT_ALIGNED_HEADERS = {
    "valor",
    "patrimonio apos",
    "pontuacao",
}


def _normalized_header(label):
    return str(label or "").strip().casefold()


def _apply_column_resize_modes(widget):
    header = widget.horizontalHeader()
    for index in range(widget.columnCount()):
        item = widget.horizontalHeaderItem(index)
        header_name = _normalized_header(item.text() if item else "")
        if header_name in COMPACT_HEADERS:
            mode = QHeaderView.ResizeMode.ResizeToContents
        else:
            mode = QHeaderView.ResizeMode.Stretch
        header.setSectionResizeMode(index, mode)
