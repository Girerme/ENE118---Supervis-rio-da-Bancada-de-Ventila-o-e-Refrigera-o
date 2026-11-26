from kivymd.uix.screen import MDScreen


class OverviewScreen(MDScreen):
    """Tela 1 (ISA-101 Nível 1-2): Visão geral da bancada de Ventilação e Refrigeração."""

    # Mapeamento: tag do CLP -> id do AnalogBar no .kv
    ANALOG_TAG_MAP = {
        "ve.temperatura": "bar_temp_saida",
        "ve.velocidade": "bar_vel_ar",
        "ve.vazao": "bar_vazao_ar",
        "ve.pit03": "bar_pit03",
        "ve.tit01": "bar_tit01",
        "ve.tit02": "bar_tit02",
        "ve.pit01": "bar_pit01",
        "ve.pit02": "bar_pit02",
        "ve.encoder": "bar_encoder",
        "ve.torque_axial1": "bar_torque",
    }

    def update_data(self, data: dict, is_stale: bool = False):
        """Atualiza todos os widgets da tela a partir do dicionário do DataManager."""
        # Atualiza barras analógicas
        for tag, widget_id in self.ANALOG_TAG_MAP.items():
            bar = self.ids.get(widget_id)
            if not bar:
                continue
            bar.is_stale = is_stale
            if not is_stale and tag in data:
                bar.value = float(data[tag])

        # Atualiza cards de equipamentos (já considerando lógica invertida tratada no DataManager)
        eq_map = {
            "eq_ventilador": ("ventilador_running", "ventilador_alarm"),
            "eq_compressor": ("compressor_running", "compressor_alarm"),
            "eq_condensador": ("condensador_running", "condensador_alarm"),
            "eq_aq1": ("aq1_running", "aq1_alarm"),
            "eq_aq2": ("aq2_running", "aq2_alarm"),
            "eq_umidificador": ("umi_running", "umi_alarm"),
        }
        for widget_id, (run_key, alm_key) in eq_map.items():
            card = self.ids.get(widget_id)
            if not card:
                continue
            card.is_stale = is_stale
            if not is_stale:
                card.is_running = bool(data.get(run_key, False))
                card.alarm_priority = int(data.get(alm_key, 0))

    # ==================== MOCKS PARA TESTE VISUAL ====================
    def load_mock_normal(self):
        self.update_data(
            {
                "ve.temperatura": 24.5,
                "ve.velocidade": 8.2,
                "ve.vazao": 920.0,
                "ve.pit03": 45.0,
                "ve.tit01": 14.0,
                "ve.tit02": 42.0,
                "ve.pit01": 75.0,
                "ve.pit02": 210.0,
                "ve.encoder": 1420.0,
                "ve.torque_axial1": 18.5,
                "ventilador_running": True,
                "compressor_running": True,
                "condensador_running": True,
                "aq1_running": False,
                "aq2_running": False,
                "umi_running": False,
            },
            is_stale=False,
        )

    def load_mock_alarm(self):
        self.update_data(
            {
                "ve.temperatura": 49.0,  # Acima do limite alto (45)
                "ve.velocidade": 8.0,
                "ve.vazao": 880.0,
                "ve.pit03": 42.0,
                "ve.tit01": 15.0,
                "ve.tit02": 72.0,  # Acima do limite alto (68)
                "ve.pit01": 75.0,
                "ve.pit02": 360.0,  # Acima do limite alto (340)
                "ve.encoder": 1420.0,
                "ve.torque_axial1": 19.0,
                "ventilador_running": True,
                "compressor_running": True,
                "compressor_alarm": 1,  # Prioridade 1 (vermelho)
                "condensador_running": False,
                "condensador_alarm": 2,  # Prioridade 2 (amarelo)
                "aq1_running": True,
                "aq2_running": False,
                "umi_running": False,
            },
            is_stale=False,
        )

    def load_mock_offline(self):
        self.update_data({}, is_stale=True)