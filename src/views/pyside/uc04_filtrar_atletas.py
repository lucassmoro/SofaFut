from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.views.pyside.shared import fill_players_table, table


class FilterPlayersScreen:
    CRITERIOS = {
        "Nome": "nome",
        "Clube": "clube",
        "Posicao": "posicao",
        "Valor": "valor",
    }

    def __init__(self, context, show_error):
        self.context = context
        self.show_error = show_error
        self.name_filter = None
        self.club_filter = None
        self.position_combo = None
        self.sort_combo = None
        self.direction_combo = None
        self.players_table = None
        self.status = None

    def build(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        filters = QHBoxLayout()
        self.name_filter = QLineEdit()
        self.name_filter.setPlaceholderText("nome")
        self.club_filter = QLineEdit()
        self.club_filter.setPlaceholderText("clube")
        self.position_combo = QComboBox()
        self.position_combo.addItem("Todas")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(list(self.CRITERIOS))
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["Decrescente", "Crescente"])
        apply_button = QPushButton("Filtrar")
        apply_button.clicked.connect(self.filtrar)

        filters.addWidget(QLabel("Nome"))
        filters.addWidget(self.name_filter)
        filters.addWidget(QLabel("Clube"))
        filters.addWidget(self.club_filter)
        filters.addWidget(QLabel("Posicao"))
        filters.addWidget(self.position_combo)
        filters.addWidget(QLabel("Ordenar"))
        filters.addWidget(self.sort_combo)
        filters.addWidget(self.direction_combo)
        filters.addWidget(apply_button)
        layout.addLayout(filters)

        self.players_table = table(["ID", "Jogador", "Time", "Pos", "Valor"])
        layout.addWidget(self.players_table, 1)
        self.status = QLabel("")
        layout.addWidget(self.status)
        return tab

    def atualizar_opcoes(self):
        jogadores = self._jogadores_catalogo()
        posicoes = sorted({jogador.posicao for jogador in jogadores if jogador.posicao})
        atual = self.position_combo.currentText() if self.position_combo else "Todas"
        self.position_combo.clear()
        self.position_combo.addItem("Todas")
        self.position_combo.addItems(posicoes)
        if atual in ["Todas", *posicoes]:
            self.position_combo.setCurrentText(atual)
        self.filtrar()

    def filtrar(self):
        jogadores = self._jogadores_ordenados()
        nome = self.name_filter.text().strip().casefold()
        clube = self.club_filter.text().strip().casefold()
        posicao = self.position_combo.currentText()

        if nome:
            jogadores = [j for j in jogadores if nome in (j.nome or "").casefold()]
        if clube:
            jogadores = [j for j in jogadores if clube in (j.nome_time or "").casefold()]
        if posicao != "Todas":
            jogadores = [j for j in jogadores if (j.posicao or "") == posicao]

        fill_players_table(self.players_table, jogadores)
        self.status.setText(f"{len(jogadores)} atletas encontrados")

    def _jogadores_ordenados(self):
        criterio = self.CRITERIOS[self.sort_combo.currentText()]
        reverse = self.direction_combo.currentText() == "Decrescente"
        try:
            return self.context.player_catalog_controller.listar_jogadores_ordenados(
                criterio,
                reverse=reverse,
            )
        except Exception:
            return sorted(
                self._jogadores_catalogo(),
                key=lambda jogador: (getattr(jogador, criterio, "") or ""),
                reverse=reverse,
            )

    def _jogadores_catalogo(self):
        if not self.context.jogadores_catalogo:
            self.context.jogadores_catalogo = self.context.player_catalog_controller.listar_jogadores()
        return self.context.jogadores_catalogo
