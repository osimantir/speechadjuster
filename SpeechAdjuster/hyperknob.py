''' Based on the Knob class from Kivy Garden
    to incorporate start and end angular limits
'''

import math

from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, BooleanProperty, ListProperty

Builder.load_string('''

<HyperKnob>
    size_hint: None, None
    pos_hint: {'center_x': .5, 'center_y': .5}

    canvas.before:
        Color:
            rgba: self.markeroff_color
        Ellipse:
            pos: self.pos
            size: self.size[0], self.size[1]
            angle_start: self.minangle + 360
            angle_end: self.maxangle + 360
        Color:
            rgba: self.marker_color
        Ellipse:
            pos: self.pos
            size: self.size[0], self.size[1]
            angle_start: self.minangle
            angle_end: self._angle if self._angle > self.minangle else self.minangle
        Color:
            rgba: 0.6, 0.6, 0.6, 1
        Ellipse:
            pos: self.pos[0] + (self.size[0] * (1 - self.track_proportion))/2, self.pos[1] + (self.size[1] * (1 - self.track_proportion)) / 2
            size: self.size[0] * self.track_proportion, self.size[1] * self.track_proportion
        PushMatrix
        Rotate:
            angle: 360 - self._angle
            origin: self.center
    canvas:
        PopMatrix

''')


class HyperKnob(Widget):

    knob_radius = NumericProperty(.5)
    track_proportion = NumericProperty(.9)
    line_start = NumericProperty(.8)
    line_end = NumericProperty(1)
    show_knob = BooleanProperty(False)
    minangle = NumericProperty(0)
    maxangle = NumericProperty(360)
    minvalue = NumericProperty(0)
    maxvalue = NumericProperty(100)
    markeroff_color = ListProperty([.2, .2, .2, 1])
    marker_color = ListProperty([.4, .4, .4, 1])
    value = NumericProperty(0)
    disabled = BooleanProperty(False)
    _angle = NumericProperty(0)
    _angle_step = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(value = self._value)
        mindim = min(self.width, self.height)
        self.size = mindim * self.knob_radius, mindim * self.knob_radius
        fac = (self.value - self.minvalue) / (self.maxvalue - self.minvalue)
        self._angle = fac * (self.maxangle - self.minangle) + self.minangle

    def _value(self, instance, value):
        if self.disabled:
            return
        fac = 0 if value <= self.minvalue else (value - self.minvalue) / (self.maxvalue - self.minvalue)
        self._angle = fac * (self.maxangle - self.minangle) + self.minangle

    def on_touch_move(self, touch):
        if self.disabled or not self.collide_point(*touch.pos):
            return

        posx, posy = touch.pos
        cx, cy = self.center
        rx, ry = posx - cx, posy - cy

        if ry >= 0:
            quadrant = 1 if rx >= 0 else 4
        else:
            quadrant = 3 if rx <= 0 else 2

        try:
            angle = math.atan(rx / ry) * (180./math.pi)
            if quadrant == 2 or quadrant == 3:
                angle = 180 + angle
            elif quadrant == 4:
                angle = 360 + angle
        except:
            angle = 90 if quadrant <= 2 else 270

        # don't update if angle is not in the allowed range
        if self.minangle >= 0:
            if angle < self.minangle:
                self.value = self.minvalue
                return
            elif angle > self.maxangle:
                self.value = self.maxvalue
                return
        elif angle < 180:
            if angle > self.maxangle:
                self.value = self.maxvalue
                return
        else:
            a = angle - 360
            if a < self.minangle:
                self.value = self.minvalue
                return

        self._angle_step = 360 / (self.maxvalue - self.minvalue)
        self._angle = self._angle_step
        while self._angle < angle:
            self._angle = self._angle + self._angle_step

        if (self.minangle <= 0) and (self.maxangle >= 0):
            if angle > 180:
                angle -= 360

        relativeValue = (angle - self.minangle) / (self.maxangle - self.minangle)
        self.value = (relativeValue * (self.maxvalue - self.minvalue)) + self.minvalue
