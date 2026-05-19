from PySide6.QtCore import QDate, QEvent, QSize, Qt, QTimer
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QAbstractSpinBox,
    QCalendarWidget,
    QComboBox,
    QDateEdit,
    QFrame,
    QGridLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QScrollArea,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from sofafut.controllers.main_controller import FixtureRow, MainController
from sofafut.infrastructure.settings import PROJECT_ROOT
from sofafut.views.match_details_window import MatchDetailsWidget


TEAM_ICON_FILES = {
    "Athletico": "atlparanaense.png",
    "Atlético Mineiro": "atlmineiro.png",
    "Bahia": "bahia.png",
    "Botafogo": "botafogo.png",
    "Chapecoense": "chapecoense.png",
    "Corinthians": "corinthians.png",
    "Coritiba": "coritiba.png",
    "Cruzeiro": "cruzeiro.png",
    "Flamengo": "flamengo.png",
    "Fluminense": "fluminense.png",
    "Grêmio": "gremio.png",
    "Internacional": "internacional.png",
    "Mirassol": "mirassol.png",
    "Palmeiras": "palmeiras.png",
    "Red Bull Bragantino": "rbbragantino.png",
    "Remo": "remo.png",
    "Santos": "santos.png",
    "São Paulo": "saopaulo.png",
    "Vasco da Gama": "vasco.png",
    "Vitória": "vitoria.png",
}


class TodayDateEdit(QDateEdit):
    MONTH_NAMES = (
        "",
        "janeiro",
        "fevereiro",
        "marco",
        "abril",
        "maio",
        "junho",
        "julho",
        "agosto",
        "setembro",
        "outubro",
        "novembro",
        "dezembro",
    )

    def __init__(self) -> None:
        super().__init__()
        self.setReadOnly(True)
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.calendar_popup = QCalendarWidget(self)
        self.calendar_popup.setWindowFlag(Qt.WindowType.Popup, True)
        self.calendar_popup.setGridVisible(False)
        self.calendar_popup.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar_popup.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.ShortDayNames)
        self.calendar_popup.setFixedSize(270, 210)
        self.calendar_popup.clicked.connect(self._select_calendar_date)
        self.lineEdit().installEventFilter(self)
        self.lineEdit().setCursor(Qt.CursorShape.PointingHandCursor)

    def textFromDateTime(self, date_time) -> str:
        date = date_time.date()
        if date == QDate.currentDate():
            return "Hoje"
        return f"{date.day()} de {self.MONTH_NAMES[date.month()]}"

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._show_calendar_popup()
            event.accept()
            return
        super().mousePressEvent(event)

    def eventFilter(self, watched, event) -> bool:
        if watched is self.lineEdit() and event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
                self._show_calendar_popup()
                return True
        return super().eventFilter(watched, event)

    def _show_calendar_popup(self) -> None:
        self.calendar_popup.setMinimumDate(self.minimumDate())
        self.calendar_popup.setMaximumDate(self.maximumDate())
        self.calendar_popup.setSelectedDate(self.date())
        self.calendar_popup.move(self.mapToGlobal(self.rect().bottomLeft()))
        self.calendar_popup.show()
        self.calendar_popup.raise_()

    def _select_calendar_date(self, date: QDate) -> None:
        self.setDate(date)
        self.calendar_popup.hide()

class MainWindow(QMainWindow):
    def __init__(
        self,
        username: str,
        controller: MainController | None = None,
    ) -> None:
        super().__init__()
        self.username = username
        self.controller = controller or MainController(username)
        self.team_buttons: dict[str, QPushButton] = {}
        self.nav_buttons: dict[str, QPushButton] = {}
        self.favorite_save_timer = QTimer(self)
        self.favorite_save_timer.setSingleShot(True)
        self.favorite_save_timer.setInterval(500)
        self.favorite_save_timer.timeout.connect(self._save_favorites)

        self.setWindowTitle("SofaFut - Principal")
        self.setMinimumSize(1000, 720)
        self._build_ui()
        self._load_seasons()
        self._refresh_favorites_table()

    def _build_ui(self) -> None:
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(12)

        layout.addLayout(self._build_top_bar())

        self.pages = QStackedWidget()
        self.pages.addWidget(self._build_games_tab())
        self.pages.addWidget(self._build_profile_tab())
        self.pages.addWidget(self._build_favorites_tab())
        layout.addWidget(self.pages, 1)
        layout.addLayout(self._build_bottom_nav())

        self.setCentralWidget(root)
        self._select_page(0)
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: #f7f4ef;
            }
            QPushButton[role="navButton"] {
                background: #b3aca4;
                color: #260d33;
                border: 0;
                border-radius: 18px;
                min-width: 104px;
                min-height: 36px;
                padding: 0 18px;
                font-weight: 700;
            }
            QPushButton[role="navButton"]:checked {
                background: #003f69;
                color: #ffffff;
            }
            QPushButton#profileButton {
                background: #003f69;
                border: 0;
                border-radius: 20px;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
                padding: 0;
            }
            QPushButton#profileButton:hover {
                background: #106b87;
            }
            QLabel[role="title"] {
                color: #003f69;
                font-size: 26px;
                font-weight: 800;
            }
            QLabel[role="subtitle"] {
                color: #106b87;
                font-size: 14px;
            }
            QComboBox {
                background: #ffffff;
                border: 1px solid #b3aca4;
                border-radius: 8px;
                color: #260d33;
                font-weight: 700;
                padding: 8px 12px;
                min-width: 132px;
                min-height: 24px;
            }
            QComboBox[role="seasonCombo"] {
                background: #f9fbfb;
                border: 1px solid #157a8c;
                color: #003f69;
                min-width: 118px;
                padding-left: 14px;
                padding-right: 30px;
            }
            QComboBox[role="seasonCombo"]:hover {
                background: #eef7f8;
                border-color: #106b87;
            }
            QComboBox[role="seasonCombo"]:focus {
                border: 2px solid #106b87;
            }
            QComboBox[role="seasonCombo"] QAbstractItemView {
                background: #ffffff;
                border: 1px solid #157a8c;
                color: #260d33;
                selection-background-color: #157a8c;
                selection-color: #ffffff;
                outline: 0;
            }
            QDateEdit {
                background: #ffffff;
                border: 1px solid #b3aca4;
                border-radius: 8px;
                color: #260d33;
                font-weight: 700;
                padding: 8px 12px;
                min-width: 112px;
                min-height: 24px;
            }
            QComboBox:hover, QDateEdit:hover {
                border-color: #157a8c;
            }
            QComboBox:focus, QDateEdit:focus {
                border: 2px solid #157a8c;
            }
            QComboBox::drop-down {
                background: transparent;
                border: 0;
                width: 0;
            }
            QComboBox::down-arrow {
                image: none;
                border: 0;
                width: 0;
                height: 0;
            }
            QDateEdit::drop-down {
                subcontrol-origin: border;
                subcontrol-position: center right;
                background: transparent;
                border: 0;
                width: 0;
            }
            QDateEdit::down-arrow {
                image: none;
                border: 0;
                width: 0;
                height: 0;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background: #003f69;
                color: #ffffff;
                min-height: 28px;
            }
            QCalendarWidget QToolButton {
                background: transparent;
                color: #ffffff;
                border: 0;
                border-radius: 4px;
                font-weight: 800;
                padding: 2px 6px;
            }
            QCalendarWidget QToolButton:hover {
                background: #106b87;
            }
            QCalendarWidget QMenu {
                background: #ffffff;
                color: #260d33;
                border: 1px solid #b3aca4;
            }
            QCalendarWidget QSpinBox {
                background: #ffffff;
                color: #260d33;
                border: 1px solid #b3aca4;
                border-radius: 4px;
                min-height: 20px;
                selection-background-color: #157a8c;
                selection-color: #ffffff;
            }
            QCalendarWidget QAbstractItemView {
                background: #ffffff;
                color: #260d33;
                font-size: 12px;
                selection-background-color: #157a8c;
                selection-color: #ffffff;
                outline: 0;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: #b3aca4;
            }
            QTableWidget {
                background: #ffffff;
                border: 1px solid #d5cec6;
                gridline-color: #e5ded7;
                selection-background-color: #157a8c;
                selection-color: #ffffff;
                min-height: 360px;
            }
            QHeaderView::section {
                background: #003f69;
                color: #ffffff;
                padding: 8px;
                border: 0;
                font-weight: 700;
            }
            QPushButton {
                background: #003f69;
                border: 0;
                border-radius: 6px;
                color: #ffffff;
                font-weight: 700;
                padding: 9px 16px;
            }
            QPushButton:hover {
                background: #106b87;
            }
            QPushButton[role="stepButton"] {
                background: #ffffff;
                border: 1px solid #b3aca4;
                border-radius: 8px;
                color: #003f69;
                font-size: 18px;
                font-weight: 900;
                min-width: 34px;
                max-width: 34px;
                min-height: 34px;
                max-height: 34px;
                padding: 0;
            }
            QPushButton[role="stepButton"]:hover {
                background: #e8f3f4;
                border-color: #157a8c;
            }
            QPushButton[role="todayButton"] {
                background: #157a8c;
                border: 0;
                border-radius: 8px;
                color: #ffffff;
                font-weight: 800;
                min-height: 34px;
                padding: 0 14px;
            }
            QPushButton[role="todayButton"]:hover {
                background: #106b87;
            }
            QLabel[role="filterLabel"] {
                color: #260d33;
                font-size: 13px;
                font-weight: 800;
            }
            QFrame[role="panel"] {
                background: #ffffff;
                border: 1px solid #d5cec6;
                border-radius: 8px;
            }
            QFrame[role="teamCard"] {
                background: #fbfaf7;
                border: 1px solid #d5cec6;
                border-radius: 10px;
            }
            QLabel[role="teamName"] {
                color: #260d33;
                font-size: 13px;
                font-weight: 800;
            }
            QPushButton[role="followButton"] {
                background: #ffffff;
                border: 1px solid #157a8c;
                border-radius: 8px;
                color: #157a8c;
                font-weight: 800;
                min-height: 30px;
                padding: 0 12px;
            }
            QPushButton[role="followButton"]:checked {
                background: #157a8c;
                color: #ffffff;
            }
            QPushButton[role="followButton"]:hover {
                background: #e8f3f4;
            }
            QPushButton[role="followButton"]:checked:hover {
                background: #106b87;
            }
            QFrame[role="topBar"], QFrame[role="bottomBar"] {
                background: transparent;
                border: 0;
            }
            """
        )

    def _build_top_bar(self) -> QHBoxLayout:
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(4, 0, 4, 0)

        app_title = QLabel("SofaFut")
        app_title.setProperty("role", "title")
        top_bar.addWidget(app_title)
        top_bar.addStretch(1)

        profile_button = QPushButton()
        profile_button.setObjectName("profileButton")
        profile_button.setToolTip("Perfil")
        profile_button.setIcon(self._avatar_icon())
        profile_button.setIconSize(QSize(26, 26))
        profile_button.clicked.connect(lambda: self._select_page(1))
        top_bar.addWidget(profile_button, 0, Qt.AlignmentFlag.AlignRight)
        return top_bar

    def _build_bottom_nav(self) -> QHBoxLayout:
        nav = QHBoxLayout()
        nav.setContentsMargins(0, 8, 0, 0)
        nav.addStretch(1)

        for index, label in ((0, "Jogos"), (2, "Favoritos")):
            button = QPushButton(label)
            button.setCheckable(True)
            button.setProperty("role", "navButton")
            button.clicked.connect(lambda checked=False, page=index: self._select_page(page))
            self.nav_buttons[label] = button
            nav.addWidget(button)

        nav.addStretch(1)
        return nav

    def _avatar_icon(self) -> QIcon:
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#f7f4ef"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(11, 6, 10, 10)
        painter.drawEllipse(6, 18, 20, 13)
        painter.end()
        return QIcon(pixmap)

    def _select_page(self, index: int) -> None:
        self.pages.setCurrentIndex(index)
        for label, button in self.nav_buttons.items():
            button_page = 0 if label == "Jogos" else 2
            button.setChecked(button_page == index)

    def _build_games_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(18)

        title = QLabel("Jogos do Brasileirao")
        title.setProperty("role", "title")
        subtitle = QLabel("Use os filtros para trocar temporada e dia. Quando houver jogos hoje, esse dia abre por padrao.")
        subtitle.setProperty("role", "subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        filters = QHBoxLayout()
        filters.addWidget(self._filter_label("Temporada"))
        filters.addWidget(self._step_button("‹", lambda: self._step_combo(self.season_combo, -1)))
        self.season_combo = QComboBox()
        self.season_combo.setEditable(False)
        self.season_combo.setProperty("role", "seasonCombo")
        self.season_combo.currentTextChanged.connect(self._on_season_changed)
        filters.addWidget(self.season_combo)
        filters.addWidget(self._step_button("›", lambda: self._step_combo(self.season_combo, 1)))
        filters.addSpacing(14)
        filters.addWidget(self._filter_label("Data"))
        filters.addWidget(self._step_button("‹", lambda: self._step_date(self.date_edit, -1)))
        self.date_edit = TodayDateEdit()
        self._setup_date_edit(self.date_edit, self._on_game_date_changed)
        filters.addWidget(self.date_edit)
        filters.addWidget(self._step_button("›", lambda: self._step_date(self.date_edit, 1)))
        filters.addWidget(self._today_button(lambda: self._set_today(self.date_edit)))
        filters.addStretch()
        layout.addLayout(filters)

        self.games_table = self._build_table("games")
        self.games_content_stack = QStackedWidget()
        self.games_content_stack.addWidget(self.games_table)
        layout.addWidget(self.games_content_stack, 1)
        return tab

    def _build_profile_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(18)

        title = QLabel(f"Perfil de {self.username}")
        title.setProperty("role", "title")
        subtitle = QLabel("Marque seus times favoritos para filtrar a aba Favoritos.")
        subtitle.setProperty("role", "subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        panel = QFrame()
        panel.setProperty("role", "panel")
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(18, 18, 18, 18)
        panel_layout.setSpacing(12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        teams_widget = QWidget()
        teams_layout = QGridLayout(teams_widget)
        teams_layout.setContentsMargins(4, 4, 4, 4)
        teams_layout.setHorizontalSpacing(16)
        teams_layout.setVerticalSpacing(16)

        for index, (team, is_favorite) in enumerate(self.controller.teams_with_favorite_state()):
            teams_layout.addWidget(self._build_team_card(team, is_favorite), index // 5, index % 5)
        scroll.setWidget(teams_widget)

        panel_layout.addWidget(scroll, 1)
        layout.addWidget(panel, 1)
        return tab

    def _build_team_card(self, team: str, is_favorite: bool) -> QFrame:
        card = QFrame()
        card.setProperty("role", "teamCard")
        card.setFixedSize(150, 178)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(96, 76)
        icon_label.setPixmap(self._team_pixmap(team))

        name_label = QLabel(team)
        name_label.setProperty("role", "teamName")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setFixedHeight(36)

        follow_button = QPushButton()
        follow_button.setCheckable(True)
        follow_button.setProperty("role", "followButton")
        follow_button.setChecked(is_favorite)
        self._update_follow_button_text(follow_button)
        follow_button.toggled.connect(lambda checked, button=follow_button: self._update_follow_button_text(button))
        follow_button.toggled.connect(lambda _checked: self.favorite_save_timer.start())
        self.team_buttons[team] = follow_button

        layout.addWidget(icon_label, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        layout.addWidget(follow_button)
        return card

    def _team_pixmap(self, team: str) -> QPixmap:
        filename = TEAM_ICON_FILES.get(team)
        if not filename:
            return QPixmap()
        pixmap = QPixmap(str(PROJECT_ROOT / "data" / "images" / "time_icones" / "seriea" / filename))
        return pixmap.scaled(
            76,
            76,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

    def _team_icon(self, team: str) -> QIcon:
        pixmap = self._team_pixmap(team)
        return QIcon(pixmap) if not pixmap.isNull() else QIcon()

    def _update_follow_button_text(self, button: QPushButton) -> None:
        button.setText("Seguindo" if button.isChecked() else "Seguir")

    def _build_favorites_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(4, 8, 4, 8)
        layout.setSpacing(18)

        title = QLabel("Jogos dos favoritos")
        title.setProperty("role", "title")
        self.favorites_subtitle = QLabel("")
        self.favorites_subtitle.setProperty("role", "subtitle")
        layout.addWidget(title)
        layout.addWidget(self.favorites_subtitle)

        filters = QHBoxLayout()
        filters.addWidget(self._filter_label("Temporada"))
        filters.addWidget(self._step_button("‹", lambda: self._step_combo(self.favorite_season_combo, -1)))
        self.favorite_season_combo = QComboBox()
        self.favorite_season_combo.setEditable(False)
        self.favorite_season_combo.setProperty("role", "seasonCombo")
        self.favorite_season_combo.currentTextChanged.connect(self._on_favorite_season_changed)
        filters.addWidget(self.favorite_season_combo)
        filters.addWidget(self._step_button("›", lambda: self._step_combo(self.favorite_season_combo, 1)))
        filters.addSpacing(14)
        filters.addWidget(self._filter_label("Data"))
        filters.addWidget(self._step_button("‹", lambda: self._step_date(self.favorite_date_edit, -1)))
        self.favorite_date_edit = TodayDateEdit()
        self._setup_date_edit(self.favorite_date_edit, self._refresh_favorites_table)
        filters.addWidget(self.favorite_date_edit)
        filters.addWidget(self._step_button("›", lambda: self._step_date(self.favorite_date_edit, 1)))
        filters.addWidget(self._today_button(lambda: self._set_today(self.favorite_date_edit)))
        filters.addStretch()
        layout.addLayout(filters)

        self.favorites_table = self._build_table("favorites")
        self.favorites_content_stack = QStackedWidget()
        self.favorites_content_stack.addWidget(self.favorites_table)
        layout.addWidget(self.favorites_content_stack, 1)
        return tab

    def _build_table(self, source: str) -> QTableWidget:
        table = QTableWidget(0, 7)
        table.setHorizontalHeaderLabels(["Data", "Temporada", "Rodada", "Mandante", "Placar", "Visitante", "Estadio"])
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(34)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setMinimumSectionSize(90)
        table.cellDoubleClicked.connect(
            lambda row, _column, current_table=table, table_source=source: self._show_match_details(
                current_table,
                row,
                table_source,
            )
        )
        return table

    def _filter_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setProperty("role", "filterLabel")
        return label

    def _step_button(self, text: str, callback) -> QPushButton:
        button = QPushButton(text)
        button.setProperty("role", "stepButton")
        button.clicked.connect(callback)
        return button

    def _today_button(self, callback) -> QPushButton:
        button = QPushButton("Hoje")
        button.setProperty("role", "todayButton")
        button.clicked.connect(callback)
        return button

    def _setup_date_edit(self, date_edit: QDateEdit, callback) -> None:
        date_edit.setCalendarPopup(True)
        date_edit.setDisplayFormat("dd/MM/yyyy")
        date_edit.dateChanged.connect(callback)

    def _load_seasons(self) -> None:
        seasons = self.controller.seasons()
        self.season_combo.blockSignals(True)
        self.favorite_season_combo.blockSignals(True)
        self.season_combo.clear()
        self.favorite_season_combo.clear()
        self.season_combo.addItems(seasons)
        self.favorite_season_combo.addItems(seasons)
        default_index = self.season_combo.findText(self.controller.default_season())
        self.season_combo.setCurrentIndex(default_index if default_index >= 0 else 0)
        self.favorite_season_combo.setCurrentIndex(default_index if default_index >= 0 else 0)
        self.season_combo.blockSignals(False)
        self.favorite_season_combo.blockSignals(False)
        self._on_season_changed(self.season_combo.currentText())
        self._on_favorite_season_changed(self.favorite_season_combo.currentText())

    def _on_season_changed(self, season_text: str) -> None:
        if not season_text:
            return
        self._load_dates(self.date_edit, season_text)
        self._refresh_games_table()

    def _on_favorite_season_changed(self, season_text: str) -> None:
        if not season_text:
            return
        self._load_dates(self.favorite_date_edit, season_text)
        self._refresh_favorites_table()

    def _load_dates(self, date_edit: QDateEdit, season_text: str) -> None:
        dates = [day for day, _label in self.controller.date_options(season_text)]
        default_day = self.controller.default_date(season_text)
        selected_day = default_day or (dates[0] if dates else "")
        date_edit.blockSignals(True)
        if dates:
            date_edit.setMinimumDate(QDate.fromString(dates[0], "yyyy-MM-dd"))
            date_edit.setMaximumDate(QDate.fromString(dates[-1], "yyyy-MM-dd"))
        if selected_day:
            date_edit.setDate(QDate.fromString(selected_day, "yyyy-MM-dd"))
        date_edit.blockSignals(False)

    def _on_game_date_changed(self) -> None:
        self._refresh_games_table()

    def _refresh_games_table(self) -> None:
        if not self.season_combo.currentText():
            return
        rows = self.controller.game_rows_by_date(
            self.season_combo.currentText(),
            self._date_edit_value(self.date_edit),
        )
        self._fill_table(self.games_table, rows)
        self._show_table("games")

    def _refresh_favorites_table(self) -> None:
        if not hasattr(self, "favorite_date_edit"):
            return
        view_data = self.controller.favorites_view_data(
            self.favorite_season_combo.currentText(),
            self._date_edit_value(self.favorite_date_edit),
        )
        self._fill_table(self.favorites_table, view_data.rows)
        self.favorites_subtitle.setText(view_data.subtitle)
        self._show_table("favorites")

    def _fill_table(self, table: QTableWidget, rows: list[FixtureRow]) -> None:
        table.setRowCount(len(rows))
        table.setIconSize(QSize(24, 24))
        for row, fixture in enumerate(rows):
            values = [
                fixture.date,
                fixture.season,
                fixture.round_name,
                fixture.home_team,
                fixture.score,
                fixture.away_team,
                fixture.venue,
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column == 0:
                    item.setData(Qt.ItemDataRole.UserRole, fixture.fixture_id)
                if column == 3:
                    item.setIcon(self._team_icon(fixture.home_team))
                elif column == 5:
                    item.setIcon(self._team_icon(fixture.away_team))
                if column in {1, 4}:
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, column, item)

    def _show_match_details(self, table: QTableWidget, row: int, source: str) -> None:
        id_item = table.item(row, 0)
        if id_item is None:
            return
        fixture_id = id_item.data(Qt.ItemDataRole.UserRole)
        if not fixture_id:
            return
        try:
            details = self.controller.match_details(str(fixture_id))
        except ValueError:
            return
        stack = self._content_stack(source)
        self._remove_details_widget(stack)
        details_widget = MatchDetailsWidget(
            details,
            on_back=lambda current_source=source: self._show_table(current_source),
            parent=self,
        )
        stack.addWidget(details_widget)
        stack.setCurrentWidget(details_widget)

    def _show_table(self, source: str) -> None:
        if source == "games" and hasattr(self, "games_content_stack"):
            self.games_content_stack.setCurrentIndex(0)
        elif source == "favorites" and hasattr(self, "favorites_content_stack"):
            self.favorites_content_stack.setCurrentIndex(0)

    def _content_stack(self, source: str) -> QStackedWidget:
        return self.games_content_stack if source == "games" else self.favorites_content_stack

    def _remove_details_widget(self, stack: QStackedWidget) -> None:
        while stack.count() > 1:
            widget = stack.widget(1)
            stack.removeWidget(widget)
            widget.deleteLater()

    def _save_favorites(self) -> None:
        selected_teams = {
            team for team, button in self.team_buttons.items() if button.isChecked()
        }
        view_data = self.controller.save_favorites(
            selected_teams,
            self.favorite_season_combo.currentText(),
            self._date_edit_value(self.favorite_date_edit),
        )
        self._fill_table(self.favorites_table, view_data.rows)
        self.favorites_subtitle.setText(view_data.subtitle)
        self._show_table("favorites")

    def _step_combo(self, combo: QComboBox, step: int) -> None:
        next_index = combo.currentIndex() + step
        if 0 <= next_index < combo.count():
            combo.setCurrentIndex(next_index)

    def _step_date(self, date_edit: QDateEdit, days: int) -> None:
        next_date = date_edit.date().addDays(days)
        if next_date < date_edit.minimumDate() or next_date > date_edit.maximumDate():
            return
        date_edit.setDate(next_date)

    def _set_today(self, date_edit: QDateEdit) -> None:
        today = QDate.currentDate()
        if today < date_edit.minimumDate():
            date_edit.setMinimumDate(today)
        if today > date_edit.maximumDate():
            date_edit.setMaximumDate(today)
        date_edit.setDate(today)

    def _date_edit_value(self, date_edit: QDateEdit) -> str:
        return date_edit.date().toString("yyyy-MM-dd")
