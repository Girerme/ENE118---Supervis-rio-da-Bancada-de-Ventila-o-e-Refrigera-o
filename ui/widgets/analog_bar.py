from kivy.graphics import Color, Line, Rectangle, Triangle
from kivy.metrics import dp
from kivy.properties import BooleanProperty, NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from ui.widgets.alarm_badge import AlarmBadge


class _AnalogGaugeCanvas(Widget):
    """Barra vertical com faixa normal (azul claro), zonas de alarme e ponteiro."""

    value = NumericProperty(0.0)
    min_val = NumericProperty(0.0)
    max_val = NumericProperty(100.0)
    normal_low = NumericProperty(20.0)
    normal_high = NumericProperty(80.0)
    alarm_low = NumericProperty(10.0)
    alarm_high = NumericProperty(90.0)
    is_stale = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            pos=self._redraw,
            size=self._redraw,
            value=self._redraw,
            min_val=self._redraw,
            max_val=self._redraw,
            normal_low=self._redraw,
            normal_high=self._redraw,
            alarm_low=self._redraw,
            alarm_high=self._redraw,
            is_stale=self._redraw,
        )

    def _val_to_y(self, val: float) -> float:
        span = max(self.max_val - self.min_val, 1e-6)
        ratio = max(0.0, min(1.0, (val - self.min_val) / span))
        return self.y + ratio * self.height

    def _redraw(self, *_args):
        self.canvas.clear()
        if self.width <= 0 or self.height <= 0:
            return

        bar_w = dp(16)
        bar_x = self.center_x - bar_w / 2 + dp(5)

        y_min = self.y
        y_max = self.top
        y_al_lo = self._val_to_y(self.alarm_low)
        y_al_hi = self._val_to_y(self.alarm_high)
        y_nm_lo = self._val_to_y(self.normal_low)
        y_nm_hi = self._val_to_y(self.normal_high)
        y_val = self._val_to_y(self.value)

        in_low_alarm = self.value <= self.alarm_low
        in_high_alarm = self.value >= self.alarm_high

        with self.canvas:
            # Fundo neutro da barra
            Color(0.92, 0.92, 0.92, 1)
            Rectangle(pos=(bar_x, y_min), size=(bar_w, self.height))

            # Zona de alarme inferior
            Color(*(0.95, 0.80, 0.12, 1) if (in_low_alarm and not self.is_stale) else (0.58, 0.58, 0.58, 1))
            Rectangle(pos=(bar_x, y_min), size=(bar_w, max(0, y_al_lo - y_min)))

            # Zona de alarme superior
            Color(*(0.95, 0.80, 0.12, 1) if (in_high_alarm and not self.is_stale) else (0.58, 0.58, 0.58, 1))
            Rectangle(pos=(bar_x, y_al_hi), size=(bar_w, max(0, y_max - y_al_hi)))

            # Faixa desejável de operação (azul claro ISA-101)
            Color(0.75, 0.88, 0.92, 1)
            Rectangle(pos=(bar_x, y_nm_lo), size=(bar_w, max(0, y_nm_hi - y_nm_lo)))

            # Contorno da barra
            Color(0.20, 0.20, 0.20, 1)
            Line(rectangle=(bar_x, y_min, bar_w, self.height), width=1.1)

            # Ponteiro triangular indicando o valor atual
            ptr_size = dp(9)
            Color(*(0.55, 0.55, 0.55, 1) if self.is_stale else (0.18, 0.20, 0.24, 1))
            Triangle(
                points=[
                    bar_x - ptr_size,
                    y_val + ptr_size * 0.6,
                    bar_x - ptr_size,
                    y_val - ptr_size * 0.6,
                    bar_x,
                    y_val,
                ]
            )


class AnalogBar(BoxLayout):
    """Indicador analógico completo: título, badge de alarme, barra vertical e valor + unidade."""

    label_text = StringProperty("Variável")
    unit = StringProperty("")
    value = NumericProperty(0.0)
    min_val = NumericProperty(0.0)
    max_val = NumericProperty(100.0)
    normal_low = NumericProperty(20.0)
    normal_high = NumericProperty(80.0)
    alarm_low = NumericProperty(10.0)
    alarm_high = NumericProperty(90.0)
    is_stale = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_x = None
        self.width = dp(96)
        self.padding = dp(4)
        self.spacing = dp(4)

        self._lbl_name = Label(
            text=self.label_text,
            font_size="11sp",
            bold=True,
            color=(0.15, 0.15, 0.15, 1),
            size_hint_y=None,
            height=dp(30),
            halign="center",
            valign="middle",
        )
        self._lbl_name.bind(size=self._lbl_name.setter("text_size"))

        # Container para centralizar o badge de alarme
        badge_box = BoxLayout(size_hint_y=None, height=dp(26))
        badge_box.add_widget(Widget())
        self._badge = AlarmBadge(priority=0)
        badge_box.add_widget(self._badge)
        badge_box.add_widget(Widget())

        self._gauge = _AnalogGaugeCanvas()

        self._lbl_val = Label(
            text=f"{self.value:.1f} {self.unit}",
            font_size="12sp",
            bold=True,
            color=(0.05, 0.15, 0.45, 1),
            size_hint_y=None,
            height=dp(24),
            halign="center",
            valign="middle",
        )

        self.add_widget(self._lbl_name)
        self.add_widget(badge_box)
        self.add_widget(self._gauge)
        self.add_widget(self._lbl_val)

        self.bind(
            label_text=self._sync,
            unit=self._sync,
            value=self._sync,
            min_val=self._sync,
            max_val=self._sync,
            normal_low=self._sync,
            normal_high=self._sync,
            alarm_low=self._sync,
            alarm_high=self._sync,
            is_stale=self._sync,
        )
        self._sync()

    def _sync(self, *_args):
        self._lbl_name.text = self.label_text
        self._gauge.value = self.value
        self._gauge.min_val = self.min_val
        self._gauge.max_val = self.max_val
        self._gauge.normal_low = self.normal_low
        self._gauge.normal_high = self.normal_high
        self._gauge.alarm_low = self.alarm_low
        self._gauge.alarm_high = self.alarm_high
        self._gauge.is_stale = self.is_stale

        if self.is_stale:
            self._lbl_val.text = "---"
            self._lbl_val.color = (0.45, 0.45, 0.45, 1)
            self._badge.priority = 0
        else:
            self._lbl_val.text = f"{self.value:.1f} {self.unit}".strip()
            self._lbl_val.color = (0.05, 0.15, 0.45, 1)
            if self.value <= self.alarm_low or self.value >= self.alarm_high:
                self._badge.priority = 2
            else:
                self._badge.priority = 0