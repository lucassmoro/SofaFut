import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


class SofaFutGui:
    def __init__(
        self,
        auth_controller,
        player_catalog_controller,
        round_controller,
        lineup_controller,
        ranking_controller,
    ):
        self.auth_controller = auth_controller
        self.player_catalog_controller = player_catalog_controller
        self.round_controller = round_controller
        self.lineup_controller = lineup_controller
        self.ranking_controller = ranking_controller
        self.username = None
        self.jogadores_catalogo = []
        self.jogadores_disponiveis = []
        self.jogadores_escalados = []
        self.jogadores_fantasy = []

        self.root = tk.Tk()
        self.root.title("SofaFut")
        self.root.geometry("1180x760")
        self.root.minsize(980, 640)
        self._configurar_estilo()
        self._montar_layout()

    def run(self):
        self.root.mainloop()

    def _configurar_estilo(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame", background="#f7f4ef")
        style.configure("TLabel", background="#f7f4ef", foreground="#260d33")
        style.configure("Title.TLabel", foreground="#003f69", font=("Arial", 22, "bold"))
        style.configure("Subtitle.TLabel", foreground="#106b87", font=("Arial", 10))
        style.configure("TButton", padding=(10, 6), font=("Arial", 10, "bold"))
        style.configure("Accent.TButton", background="#003f69", foreground="#ffffff")
        style.configure("Treeview", rowheight=28)
        style.configure("Treeview.Heading", background="#003f69", foreground="#ffffff", font=("Arial", 10, "bold"))

    def _montar_layout(self):
        self.root.configure(background="#f7f4ef")
        self.container = ttk.Frame(self.root, padding=18)
        self.container.pack(fill=tk.BOTH, expand=True)
        self._montar_tela_login()

    def _limpar_container(self):
        for child in self.container.winfo_children():
            child.destroy()

    def _montar_tela_login(self):
        self._limpar_container()
        wrapper = ttk.Frame(self.container)
        wrapper.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        ttk.Label(wrapper, text="SofaFut", style="Title.TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 8))
        ttk.Label(
            wrapper,
            text="Entre ou cadastre-se para montar sua escalação.",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, columnspan=2, pady=(0, 24))

        ttk.Label(wrapper, text="Usuário").grid(row=2, column=0, sticky=tk.W, padx=6, pady=6)
        self.username_entry = ttk.Entry(wrapper, width=34)
        self.username_entry.grid(row=2, column=1, padx=6, pady=6)

        ttk.Label(wrapper, text="Senha").grid(row=3, column=0, sticky=tk.W, padx=6, pady=6)
        self.password_entry = ttk.Entry(wrapper, width=34, show="*")
        self.password_entry.grid(row=3, column=1, padx=6, pady=6)

        buttons = ttk.Frame(wrapper)
        buttons.grid(row=4, column=0, columnspan=2, pady=(18, 0))
        ttk.Button(buttons, text="Entrar", command=self._login).pack(side=tk.LEFT, padx=6)
        ttk.Button(buttons, text="Cadastrar", command=self._cadastrar).pack(side=tk.LEFT, padx=6)

        self.status_label = ttk.Label(wrapper, text="", style="Subtitle.TLabel")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=(16, 0))

    def _login(self):
        username = self.username_entry.get().strip()
        senha = self.password_entry.get().strip()
        if not username or not senha:
            self._mostrar_erro("Preencha usuário e senha.")
            return

        mensagem = self.auth_controller.login(username, senha)
        if mensagem != "Usuario logado":
            self.status_label.configure(text=mensagem)
            return

        self.username = username
        self._montar_tela_principal()

    def _cadastrar(self):
        username = self.username_entry.get().strip()
        senha = self.password_entry.get().strip()
        if not username or not senha:
            self._mostrar_erro("Preencha usuário e senha.")
            return

        mensagem = self.auth_controller.cadastrar(username=username, senha=senha)
        self.status_label.configure(text=mensagem)

    def _montar_tela_principal(self):
        self._limpar_container()
        header = ttk.Frame(self.container)
        header.pack(fill=tk.X, pady=(0, 12))
        ttk.Label(header, text="SofaFut", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(header, text=f"Usuário: {self.username}", style="Subtitle.TLabel").pack(side=tk.RIGHT)

        self.tabs = ttk.Notebook(self.container)
        self.tabs.pack(fill=tk.BOTH, expand=True)
        self._montar_aba_rodada()
        self._montar_aba_escalacao()
        self._montar_aba_ranking()

        self._carregar_catalogo()
        self._atualizar_ranking()

    def _montar_aba_rodada(self):
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="Rodada")

        filters = ttk.Frame(tab)
        filters.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(filters, text="Temporada").pack(side=tk.LEFT, padx=(0, 6))
        self.temporada_var = tk.StringVar(value="2024")
        temporada_combo = ttk.Combobox(
            filters,
            textvariable=self.temporada_var,
            values=[str(item) for item in self.round_controller.listar_temporadas_disponiveis()],
            width=8,
            state="readonly",
        )
        temporada_combo.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(filters, text="Rodada").pack(side=tk.LEFT, padx=(0, 6))
        self.rodada_var = tk.StringVar(value="1")
        rodada_combo = ttk.Combobox(
            filters,
            textvariable=self.rodada_var,
            values=[str(item) for item in self.round_controller.listar_rodadas_disponiveis()],
            width=8,
            state="readonly",
        )
        rodada_combo.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(filters, text="Máx. partidas").pack(side=tk.LEFT, padx=(0, 6))
        self.max_partidas_var = tk.StringVar(value="10")
        ttk.Entry(filters, textvariable=self.max_partidas_var, width=6).pack(side=tk.LEFT, padx=(0, 14))

        ttk.Button(filters, text="Carregar Rodada", command=self._carregar_rodada).pack(side=tk.LEFT)
        ttk.Button(filters, text="Usar Cache", command=self._listar_jogadores_cache).pack(side=tk.LEFT, padx=8)

        columns = ("api_id", "nome", "time", "posicao", "minutos", "partida")
        self.available_tree = ttk.Treeview(tab, columns=columns, show="headings", selectmode="extended")
        for column, label, width in (
            ("api_id", "ID", 72),
            ("nome", "Jogador", 190),
            ("time", "Time", 150),
            ("posicao", "Pos", 60),
            ("minutos", "Min", 60),
            ("partida", "Partida", 250),
        ):
            self.available_tree.heading(column, text=label)
            self.available_tree.column(column, width=width, anchor=tk.W)
        self.available_tree.pack(fill=tk.BOTH, expand=True)

        footer = ttk.Frame(tab)
        footer.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(footer, text="Adicionar Selecionados à Escalação", command=self._adicionar_selecionados).pack(side=tk.LEFT)
        self.round_status_label = ttk.Label(footer, text="", style="Subtitle.TLabel")
        self.round_status_label.pack(side=tk.LEFT, padx=12)

    def _montar_aba_escalacao(self):
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="Escalação")

        columns = ("api_id", "nome", "time", "posicao", "capitao")
        self.lineup_tree = ttk.Treeview(tab, columns=columns, show="headings", selectmode="browse")
        for column, label, width in (
            ("api_id", "ID", 72),
            ("nome", "Jogador", 220),
            ("time", "Time", 170),
            ("posicao", "Pos", 70),
            ("capitao", "Capitão", 90),
        ):
            self.lineup_tree.heading(column, text=label)
            self.lineup_tree.column(column, width=width, anchor=tk.W)
        self.lineup_tree.pack(fill=tk.BOTH, expand=True)

        footer = ttk.Frame(tab)
        footer.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(footer, text="Definir Capitão", command=self._definir_capitao).pack(side=tk.LEFT)
        ttk.Button(footer, text="Remover", command=self._remover_escalado).pack(side=tk.LEFT, padx=8)
        ttk.Button(footer, text="Calcular Pontuação", command=self._calcular_pontuacao).pack(side=tk.LEFT, padx=8)
        self.lineup_status_label = ttk.Label(footer, text="0/11 jogadores", style="Subtitle.TLabel")
        self.lineup_status_label.pack(side=tk.LEFT, padx=12)

        self.score_text = tk.Text(tab, height=8, wrap=tk.WORD)
        self.score_text.pack(fill=tk.X, pady=(10, 0))

    def _montar_aba_ranking(self):
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="Ranking")
        ttk.Button(tab, text="Atualizar Ranking", command=self._atualizar_ranking).pack(anchor=tk.W, pady=(0, 8))
        self.ranking_text = tk.Text(tab, wrap=tk.WORD)
        self.ranking_text.pack(fill=tk.BOTH, expand=True)

    def _carregar_catalogo(self):
        temporada = int(self.temporada_var.get())
        jogadores = self.player_catalog_controller.carregar_jogadores_temporada(temporada=temporada)
        self.jogadores_catalogo = jogadores
        self.round_status_label.configure(text=f"Catálogo carregado: {len(jogadores)} jogadores")

    def _carregar_rodada(self):
        try:
            temporada = int(self.temporada_var.get())
            rodada = int(self.rodada_var.get())
            max_partidas = self._max_partidas()
            dados = self.round_controller.baixar_dados_rodada(
                temporada=temporada,
                numero_rodada=rodada,
                max_partidas=max_partidas,
            )
            total = len(dados.get("partidas_api", {}).get("response", []))
            cacheadas = len(dados.get("partidas", []))
            self._listar_jogadores_cache()
            self.round_status_label.configure(text=f"Rodada {rodada}: {cacheadas}/{total} partidas com estatísticas")
        except Exception as exc:
            self._mostrar_erro(str(exc))

    def _listar_jogadores_cache(self):
        try:
            temporada = int(self.temporada_var.get())
            rodada = int(self.rodada_var.get())
            self.jogadores_disponiveis = self.round_controller.listar_jogadores_disponiveis(
                temporada=temporada,
                numero_rodada=rodada,
            )
            self._preencher_disponiveis()
            self.round_status_label.configure(text=f"{len(self.jogadores_disponiveis)} atuações disponíveis")
        except Exception as exc:
            self._mostrar_erro(str(exc))

    def _preencher_disponiveis(self):
        self.available_tree.delete(*self.available_tree.get_children())
        for index, jogador in enumerate(self.jogadores_disponiveis):
            self.available_tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    jogador.get("api_id") or "",
                    jogador.get("nome") or "",
                    jogador.get("time") or "",
                    jogador.get("posicao") or "",
                    jogador.get("minutos") or 0,
                    jogador.get("partida") or "",
                ),
            )

    def _adicionar_selecionados(self):
        selecionados = [
            self.jogadores_disponiveis[int(item_id)]
            for item_id in self.available_tree.selection()
        ]
        players = self.lineup_controller.selecionar_players_do_catalogo(selecionados)
        existentes = {player.api_id for player in self.jogadores_escalados}

        for player in players:
            if len(self.jogadores_escalados) >= 11:
                break
            if player.api_id in existentes:
                continue
            self.jogadores_escalados.append(player)
            existentes.add(player.api_id)

        if len(players) < len(selecionados):
            self._mostrar_erro("Alguns jogadores selecionados não existem no catálogo fixo.")

        self._preencher_escalacao()
        self.tabs.select(1)

    def _preencher_escalacao(self):
        self.lineup_tree.delete(*self.lineup_tree.get_children())
        capitao = self.jogadores_escalados[0] if self.jogadores_escalados else None

        for index, jogador in enumerate(self.jogadores_escalados):
            self.lineup_tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    jogador.api_id or "",
                    jogador.nome or "",
                    jogador.nome_time or "",
                    jogador.posicao or "",
                    "Sim" if jogador is capitao else "",
                ),
            )

        self.lineup_status_label.configure(text=f"{len(self.jogadores_escalados)}/11 jogadores")

    def _definir_capitao(self):
        selection = self.lineup_tree.selection()
        if not selection:
            return
        index = int(selection[0])
        jogador = self.jogadores_escalados.pop(index)
        self.jogadores_escalados.insert(0, jogador)
        self._preencher_escalacao()

    def _remover_escalado(self):
        selection = self.lineup_tree.selection()
        if not selection:
            return
        self.jogadores_escalados.pop(int(selection[0]))
        self._preencher_escalacao()

    def _calcular_pontuacao(self):
        try:
            if len(self.jogadores_escalados) != 11:
                raise RuntimeError("A escalação precisa ter 11 jogadores.")

            temporada = int(self.temporada_var.get())
            rodada = int(self.rodada_var.get())
            jogadores_fantasy = self.lineup_controller.criar_escalacao_fantasy(
                self.jogadores_escalados,
                capitao=self.jogadores_escalados[0],
            )
            rodada_model = self.round_controller.montar_rodada_por_cache(
                temporada=temporada,
                numero_rodada=rodada,
                jogadores_escalados=self.jogadores_escalados,
            )
            self.round_controller.adicionar_rodada(rodada_model)
            pontuacao_total = self.lineup_controller.executar_rodada(
                username=self.username,
                numero_rodada=rodada,
                jogadores_fantasy=jogadores_fantasy,
            )
            escalacao = self.lineup_controller.buscar_escalacao(rodada)
            jogadores_calculados = escalacao.jogadores if escalacao is not None else jogadores_fantasy
            self.jogadores_fantasy = jogadores_calculados
            self._mostrar_pontuacao(rodada, pontuacao_total, jogadores_calculados)
            self._atualizar_ranking()
        except Exception as exc:
            self._mostrar_erro(str(exc))

    def _mostrar_pontuacao(self, rodada, pontuacao_total, jogadores_fantasy):
        self.score_text.delete("1.0", tk.END)
        self.score_text.insert(tk.END, f"Rodada {rodada}: {pontuacao_total} pontos\n\n")
        for jogador_fantasy in jogadores_fantasy:
            capitao = " (capitão)" if jogador_fantasy.capitao else ""
            self.score_text.insert(
                tk.END,
                f"{jogador_fantasy.jogador.nome}{capitao}: {jogador_fantasy.pontuacao} pontos\n",
            )

    def _atualizar_ranking(self):
        if not hasattr(self, "ranking_text"):
            return
        self.ranking_text.delete("1.0", tk.END)
        self.ranking_text.insert(tk.END, self.ranking_controller.formatar_ranking_usuarios())

    def _max_partidas(self):
        valor = self.max_partidas_var.get().strip()
        if not valor:
            return None
        return int(valor)

    def _mostrar_erro(self, mensagem):
        messagebox.showerror("SofaFut", mensagem)
