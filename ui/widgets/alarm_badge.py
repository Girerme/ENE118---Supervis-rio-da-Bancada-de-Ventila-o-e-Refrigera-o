from kivy.graphics import Color, Line, Rectangle, Triangle
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.label import Label


class AlarmBadge(Label):
    """Indicador de alarme redundante (ISA-101): cor + forma + número da prioridade.
    priority: 0 = sem alarme, 1 = alta (vermelho/quadrado),
              2 = média (amarelo/triângulo), 3 = baixa (laranja/triângulo invertido).
    """

    priority = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(26), dp(26))
        self.bold = True
        self.font_size = "12sp"
        self.halign = "center"
        self.valign = "middle"
        self.bind(pos=self._redraw, size=self._redraw, priority=self._redraw)
        self._redraw()

    def _redraw(self, *_args):
        self.canvas.before.clear()
        p = int(self.priority)

        if p <= 0:
            self.text = ""
            self.opacity = 0
            return

        self.opacity = 1
        self.text = str(p)
        x, y = self.pos
        w, h = self.size

        with self.canvas.before:
            if p == 1:
                # Prioridade 1: Quadrado vermelho
                self.color = (1, 1, 1, 1)
                Color(0.85, 0.12, 0.12, 1)
                Rectangle(pos=(x, y), size=(w, h))
                Color(0.1, 0.1, 0.1, 1)
                Line(rectangle=(x, y, w, h), width=1.2)
            elif p == 2:
                # Prioridade 2: Triângulo amarelo
                self.color = (0.1, 0.1, 0.1, 1)
                pts = [x, y, x + w, y, x + w / 2, y + h]
                Color(0.98, 0.85, 0.12, 1)
                Triangle(points=pts)
                Color(0.1, 0.1, 0.1, 1)
                Line(points=pts + [x, y], width=1.2)
            else:
                # Prioridade 3: Triângulo invertido laranja
                self.color = (0.1, 0.1, 0.1, 1)
                pts = [x, y + h, x + w, y + h, x + w / 2, y]
                Color(0.95, 0.55, 0.12, 1)
                Triangle(points=pts)
                Color(0.1, 0.1, 0.1, 1)
                Line(points=pts + [x, y + h], width=1.2)