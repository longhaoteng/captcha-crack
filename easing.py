#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'mr.long'

import math


class Easing(object):
    """
    Easing functions
    """

    PI = math.pi
    c1 = 1.70158
    c2 = c1 * 1.525
    c3 = c1 + 1
    c4 = (2 * PI) / 3
    c5 = (2 * PI) / 4.5


def ease_out_sine(x):
    return math.sin(x * Easing.PI / 2)


def ease_out_cubic(x):
    return 1 - pow(1 - x, 3)


def ease_out_quint(x):
    return 1 - pow(1 - x, 5)


def ease_out_circ(x):
    return math.sqrt(1 - pow(x - 1, 2))


def ease_out_quad(x):
    return 1 - (1 - x) * (1 - x)


def ease_out_quart(x):
    return 1 - pow(1 - x, 4)


def ease_out_expo(x):
    if x == 1:
        return 1
    else:
        return 1 - pow(2, -10 * x)


def ease_out_back(x):
    return 1 + Easing.c3 * pow(x - 1, 3) + Easing.c1 * pow(x - 1, 2)


def ease_out_bounce(x):
    n1 = 7.5625
    d1 = 2.75
    if x < 1 / d1:
        return n1 * x * x
    elif x < 2 / d1:
        x -= 1.5 / d1
        return n1 * x * x + 0.75
    elif x < 2.5 / d1:
        x -= 2.25 / d1
        return n1 * x * x + 0.9375
    else:
        x -= 2.625 / d1
        return n1 * x * x + 0.984375
