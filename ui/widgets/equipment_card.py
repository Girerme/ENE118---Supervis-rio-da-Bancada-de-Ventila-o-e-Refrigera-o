from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label

from ui.widgets.alarm_badge import AlarmBadge


class EquipmentCard(BoxLayout):
    """Bloco 2D neutro para equipamentos (ISA-101).
    Ligado = preenchimento claro; Parado = preenchimento escuro.
    """

    title = StringProperty("Equipamento")
    subtitle = StringProperty("")
    is_running = BooleanProperty(False)
    is_stale = BooleanProperty(False)
    alarm_priority = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = dp(8)
        self.spacing = dp(4)
        self.size_hint_y = None
        self.height = dp(88)

        # Cabeçalho: nome + badge de alarme
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(26))
        self._lbl_title = Label(
            text=self.title,
            bold=True,
            font_size="13sp",
            halign="left",
            valign="middle",
        )
        self._lbl_title.bind(size=self._lbl_title.setter("text_size"))
        self._badge = AlarmBadge(priority=self.alarm_priority)
        header.add_widget(self._lbl_title)
        header.add_widget(self._badge)

        # Estado textual explícito (LIGADO / PARADO / DESATUALIZADO)
        self._lbl_status = Label(
            text="PARADO",
            bold=True,
            font_size="14sp",
            halign="left",
            valign="middle",
        )
        self._lbl_status.bind(size=self._lbl_status.setter("text_size"))

        # Subtítulo opcional (ex.: modo de partida ou comando solicitado)
        self._lbl_sub = Label(
            text=self.subtitle,
            font_size="11sp",
            halign="left",
            valign="middle",
        )
        self._lbl_sub.bind(size=self._lbl_sub.setter("text_size"))

        self.add_widget(header)
        self.add_widget(self._lbl_status)
        self.add_widget(self._lbl_sub)

        self.bind(
            pos=self._update_visual,
            size=self._update_visual,
            title=self._update_visual,
            subtitle=self._update_visual,
            is_running=self._update_visual,
            is_stale=self._update_visual,
            alarm_priority=self._update_visual,
        )
        self._update_visual()

    def _update_visual(self, *_args):
        self._lbl_title.text = self.title
        self._lbl_sub.text = self.subtitle
        self._badge.priority = self.alarm_priority

        if self.is_stale:
            bg = (0.72, 0.72, 0.72, 1)
            fg = (0.35, 0.35, 0.35, 1)
            border = (0.85, 0.65, 0.10, 1)
            self._lbl_status.text = "DESATUALIZADO"
        elif self.is_running:
            # Brilho claro = em operação
            bg = (0.96, 0.96, 0.96, 1)
            fg = (0.10, 0.12, 0.18, 1)
            border = (0.25, 0.25, 0.25, 1)
            self._lbl_status.text = "LIGADO"
        else:
            # Brilho escuro = parado (estado normal)
            bg = (0.45, 0.47, 0.50, 1)
            fg = (0.95, 0.95, 0.95, 1)
            border = (0.25, 0.25, 0.25, 1)
            self._lbl_status.text = "PARADO"

        if self.alarm_priority == 1:
            border = (0.85, 0.12, 0.12, 1)
        elif self.alarm_priority == 2:
            border = (0.95, 0.75, 0.10, 1)

        self._lbl_title.color = fg
        self._lbl_status.color = fg
        self._lbl_sub.color = fg

        self.canvas.before.clear()
        with self.canvas.before:
            Color(*bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[4])
            Color(*border)
            Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 4), width=1.4)