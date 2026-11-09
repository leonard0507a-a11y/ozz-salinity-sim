"""Streamlit-приложение: интерактивная симуляция защиты кабеля."""
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st

from src.ozz_sim.model import Params, relay_current, dead_zone

st.set_page_config(page_title="OZZ Salinity Sim", layout="wide")
st.title("Защита кабеля плавучей платформы от утечки в воду")
st.caption("Модель по рис. 2.5–2.6 диссертации. Это расчёт, а не измерения.")

# --- Ползунки ---
col1, col2, col3 = st.columns(3)
with col1:
    rho = st.slider("ρ воды, Ом·м", 5.0, 500.0, 15.0, step=1.0)
    r_fault = st.slider("Переходное сопротивление, Ом", 0.0, 500.0, 0.0, step=10.0)
with col2:
    l_d = st.slider("Положение электрода l_д, м", 0.0, 700.0, 7.0, step=1.0)
    x_fault = st.slider("Место утечки x, м", 0.0, 700.0, 74.0, step=1.0)
with col3:
    i_set_ma = st.slider("Ток срабатывания реле, мА", 0.05, 1.0, 0.24, step=0.01)

p = Params(rho=rho, r_fault=r_fault, I_set=i_set_ma * 1e-3)

# --- Расчёт в точке ---
i_now = relay_current(x_fault, l_d, p)
st.metric("Ток реле в точке утечки", f"{i_now * 1e3:.3f} мА",
          delta="сработает" if i_now >= p.I_set else "не сработает")

dz_start, dz_len = dead_zone(l_d, p)
st.write(f"Зона нечувствительности: начало **{dz_start:.0f} м**, длина **{dz_len:.0f} м**")

# --- График тока вдоль кабеля ---
xs = np.linspace(0, p.l_cable, 400)
i_curve = np.array([relay_current(x, l_d, p) for x in xs]) * 1e3

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(xs, i_curve, label="ток реле, мА")
ax.axhline(p.I_set * 1e3, color="red", ls="--", label="ток срабатывания")
ax.axvline(x_fault, color="green", ls=":", label="место утечки")
ax.set_xlabel("Расстояние вдоль кабеля x, м")
ax.set_ylabel("Ток реле, мА")
ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig)

# --- Зависимость от солёности ---
rhos = np.linspace(5, 500, 200)
i_rho = np.array([relay_current(x_fault, l_d, Params(rho=r, r_fault=r_fault,
                                                      I_set=p.I_set)) for r in rhos]) * 1e3
fig2, ax2 = plt.subplots(figsize=(10, 3.5))
ax2.plot(rhos, i_rho)
ax2.axhline(p.I_set * 1e3, color="red", ls="--")
ax2.set_xlabel("ρ воды, Ом·м")
ax2.set_ylabel("Ток реле, мА")
ax2.grid(True, alpha=0.3)
st.pyplot(fig2)
