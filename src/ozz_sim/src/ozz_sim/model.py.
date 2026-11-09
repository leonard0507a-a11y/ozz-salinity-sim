"""Модель защиты кабеля плавучей платформы по способу
«напряжение между заземлённой нейтралью и электродом в озере».

Воспроизводит расчётную схему рис. 2.5–2.6 диссертации.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Params:
    """Параметры схемы. Сопротивления в Ом, длины в м, токи в А."""
    rho: float = 15.0            # удельное сопротивление воды, Ом·м
    U: float = 230.0             # фазное напряжение, В
    l_cable: float = 700.0       # длина кабеля, м
    r_relay: float = 6000.0      # сопротивление обмотки реле, Ом
    I_set: float = 0.24e-3       # ток срабатывания реле, А
    r_fault: float = 0.0         # переходное сопротивление в месте утечки, Ом
    r_electrode: float = 1.0     # сопротивление электрода, Ом
    k_geo: float = 1.0           # геометрический коэффициент растекания


def _r_leak(x: float, p: Params) -> float:
    """Сопротивление пути утечки через воду от точки x до электрода."""
    # упрощённая модель: сопротивление пропорционально ρ и расстоянию
    return p.k_geo * p.rho * max(x, 1e-6) / p.l_cable + p.r_electrode


def relay_current(x: float, l_d: float, p: Params) -> float:
    """Ток через реле при утечке в точке x (м) и электроде в l_d (м).

    Возвращает ток в амперах.
    """
    r_leak = _r_leak(abs(x - l_d), p) + p.r_fault
    # делитель: напряжение U распределяется между путём утечки и реле
    i = p.U / (r_leak + p.r_relay)
    return i


def dead_zone(l_d: float, p: Params, x_max: float | None = None,
              step: float = 1.0) -> tuple[float, float]:
    """Зона, где ток реле меньше I_set (защита «слепая»).

    Возвращает (начало зоны, длина зоны) в метрах вдоль кабеля.
    """
    if x_max is None:
        x_max = p.l_cable
    start = None
    length = 0.0
    x = 0.0
    while x <= x_max:
        if relay_current(x, l_d, p) < p.I_set:
            if start is None:
                start = x
            length += step
        x += step
    if start is None:
        return (0.0, 0.0)
    return (start, length)


def robust_electrode_position(rho_range: tuple[float, float], p: Params,
                              n: int = 20) -> float:
    """Положение электрода, при котором зона нечувствительности
    минимальна на всём диапазоне ρ."""
    best_l = 0.0
    best_score = float("inf")
    lo, hi = rho_range
    for i in range(n + 1):
        l_d = lo + (hi - lo) * i / n
        score = 0.0
        for j in range(5):
            rho = lo + (hi - lo) * j / 4
            p2 = Params(**{**p.__dict__, "rho": rho})
            _, dz = dead_zone(l_d, p2)
            score += dz
        if score < best_score:
            best_score = score
            best_l = l_d
    return best_l
