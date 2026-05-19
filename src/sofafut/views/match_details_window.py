from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from sofafut.services.match_details_service import MatchDetails, PlayerLineupRow, TeamLineup


class MatchDetailsWidget(QWidget):
    def __init__(
        self,
        details: MatchDetails,
        on_back: Callable[[], None] | None = None,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.details = details
        self.on_back = on_back
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        back_button = QPushButton("Voltar")
        back_button.setProperty("role", "backButton")
        back_button.clicked.connect(self._go_back)
        header.addWidget(back_button, 0, Qt.AlignmentFlag.AlignLeft)

        title = QLabel(self.details.title)
        title.setProperty("role", "title")
        title.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        header.addWidget(title, 1)
        layout.addLayout(header)

        tabs = QTabWidget()
        tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        tabs.addTab(self._build_lineups_tab(), "Escalacao")
        tabs.addTab(self._build_stats_tab(), "Estatisticas")
        layout.addWidget(tabs, 1)
        self.setStyleSheet(
            """
            QLabel[role="title"] {
                color: #003f69;
                font-size: 22px;
                font-weight: 800;
            }
            QLabel[role="teamTitle"] {
                color: #003f69;
                font-size: 16px;
                font-weight: 800;
            }
            QPushButton[role="backButton"] {
                background: #ffffff;
                border: 1px solid #157a8c;
                border-radius: 8px;
                color: #003f69;
                font-weight: 800;
                min-width: 92px;
                min-height: 34px;
                padding: 0 14px;
            }
            QPushButton[role="backButton"]:hover {
                background: #e8f3f4;
            }
            QFrame[role="detailsPanel"] {
                background: #ffffff;
                border: 1px solid #d5cec6;
                border-radius: 8px;
            }
            QTableWidget {
                background: #ffffff;
                border: 1px solid #d5cec6;
                gridline-color: #e5ded7;
                selection-background-color: #157a8c;
            }
            QHeaderView::section {
                background: #003f69;
                color: #ffffff;
                padding: 7px;
                border: 0;
                font-weight: 700;
            }
            QTableWidget::item {
                padding: 4px 7px;
            }
            QTabBar::tab {
                background: #b3aca4;
                color: #260d33;
                padding: 9px 16px;
                font-weight: 700;
            }
            QTabBar::tab:selected {
                background: #003f69;
                color: #ffffff;
            }
            """
        )

    def _go_back(self) -> None:
        if self.on_back is not None:
            self.on_back()

    def _build_lineups_tab(self) -> QWidget:
        tab = QWidget()
        layout = QHBoxLayout(tab)
        layout.setContentsMargins(0, 12, 0, 0)
        layout.setSpacing(14)
        layout.addWidget(self._lineup_panel(self.details.home_lineup))
        layout.addWidget(self._lineup_panel(self.details.away_lineup))
        return tab

    def _lineup_panel(self, lineup: TeamLineup) -> QFrame:
        panel = QFrame()
        panel.setProperty("role", "detailsPanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        title = QLabel(lineup.team_name)
        title.setProperty("role", "teamTitle")
        layout.addWidget(title)

        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels(["N", "Jogador", "Pos", "Tipo", "Nota"])
        self._setup_lineup_table(table)
        if lineup.players:
            table.setRowCount(len(lineup.players))
            for row, player in enumerate(lineup.players):
                self._fill_player_row(table, row, player)
        else:
            self._fill_empty_row(table, "Escalacao indisponivel para esta partida.", 5)
        layout.addWidget(table, 1)
        return panel

    def _fill_player_row(self, table: QTableWidget, row: int, player: PlayerLineupRow) -> None:
        values = [player.number, player.name, player.position, player.role, player.rating]
        for column, value in enumerate(values):
            item = QTableWidgetItem(value)
            if column in {0, 2, 3, 4}:
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, column, item)

    def _build_stats_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 12, 0, 0)
        panel = QFrame()
        panel.setProperty("role", "detailsPanel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(14, 14, 14, 14)
        table = QTableWidget(0, 3)
        table.setHorizontalHeaderLabels(
            [
                self.details.home_lineup.team_name,
                "Estatistica",
                self.details.away_lineup.team_name,
            ]
        )
        self._setup_stats_table(table)
        if self.details.stats:
            table.setRowCount(len(self.details.stats))
            for row, stat in enumerate(self.details.stats):
                if stat.is_group:
                    self._fill_group_row(table, row, stat.name, 3)
                    continue
                for column, value in enumerate([stat.home, stat.name, stat.away]):
                    item = QTableWidgetItem(value)
                    if column in {0, 1, 2}:
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    table.setItem(row, column, item)
        else:
            self._fill_empty_row(table, "Estatisticas indisponiveis para esta partida.", 3)
        panel_layout.addWidget(table)
        layout.addWidget(panel, 1)
        return tab

    def _setup_table(self, table: QTableWidget) -> None:
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(38)
        table.setWordWrap(False)
        table.setAlternatingRowColors(True)
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

    def _setup_lineup_table(self, table: QTableWidget) -> None:
        self._setup_table(table)
        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 44)
        table.setColumnWidth(2, 58)
        table.setColumnWidth(3, 92)
        table.setColumnWidth(4, 64)

    def _setup_stats_table(self, table: QTableWidget) -> None:
        self._setup_table(table)
        table.verticalHeader().setDefaultSectionSize(44)
        header = table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        table.setColumnWidth(0, 150)
        table.setColumnWidth(2, 150)

    def _fill_empty_row(self, table: QTableWidget, text: str, columns: int) -> None:
        table.setRowCount(1)
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(0, 0, item)
        table.setSpan(0, 0, 1, columns)

    def _fill_group_row(self, table: QTableWidget, row: int, text: str, columns: int) -> None:
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setBackground(QColor("#e8f3f4"))
        font = item.font()
        font.setBold(True)
        item.setFont(font)
        table.setItem(row, 0, item)
        table.setSpan(row, 0, 1, columns)
        table.setRowHeight(row, 34)
