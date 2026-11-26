from datetime import datetime
from pathlib import Path

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty
from kivymd.app import MDApp


class SupervisorioApp(MDApp):
    active_env = StringProperty("SIMULADOR LOCAL")
    is_connected = BooleanProperty(False)
    comm_status_text = StringProperty("DESCONECTADO — DADOS DESATUALIZADOS")
    last_update_str = StringProperty("--:--:--")

    def build(self):
        self.title = "Supervisório ENE118 - Ventilação e Refrigeração"
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Slategray"

        kv_path = Path(__file__).parent / "kv" / "main_layout.kv"
        return Builder.load_file(str(kv_path))

    def on_start(self):
        # Atualiza o relógio da barra superior a cada 1 segundo
        Clock.schedule_interval(self._update_clock, 1.0)

    def _update_clock(self, _dt):
        self.last_update_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def switch_screen(self, screen_name: str):
        self.root.ids.screen_manager.current = screen_name