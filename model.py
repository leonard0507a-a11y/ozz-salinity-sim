"""Модель защиты кабеля плавучей платформы по способу
«напряжение между заземлённой нейтралью и электродом в озере».
"""
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Params:
    rho: float = 15.0            
    U: float = 230.0             
    l_cable: float = 700.0       
    r_relay: float = 6000.0      
    I_set: float = 0.24e-3       
    r_fault: float = 0.0         
    r_electrode: float = 1.0     
    k_geo: float = 1.0           

def _r_leak(x: float, p: Params) -> float:
    return p.k_geo * p.rho * max(x, 1e-6) / p.l_cable + p.r_electrode

def relay_current(x: float, l_d: float, p: Params) -> float:
    r_leak = _r_leak(abs(x - l_d), p) + p.r_fault
    return p.U / (r_leak + p.r_relay)

def dead_zone(l_d: float, p: Params, x_max: float | None = None, step: float = 1.0) -> tuple[float, float]:
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

def robust_electrode_position(rho_range: tuple[float, float], p: Params, n: int = 20) -> float:
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
