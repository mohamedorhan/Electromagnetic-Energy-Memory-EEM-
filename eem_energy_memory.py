#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Electromagnetic Energy Memory (EEM) — LC Ring Simulator
-------------------------------------------------------

Final, publication–ready Python reference implementation.

Features:
- LC ring model with resistive loss and capacitive coupling
- High-precision ODE integration (solve_ivp)
- Per-cell and total energy tracking
- Automatic energy localization (memory state) detection
- Publication-grade plots:
    * total energy vs time
    * space–time energy map
    * energy localization profile

Dependencies:
  numpy, scipy, matplotlib

Author: Mohamed Orhan Zeinel
"""

from dataclasses import dataclass
from typing import Tuple, Optional

import numpy as np
from scipy.integrate import solve_ivp
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt


# ============================================================
# 1. Configuration
# ============================================================

@dataclass
class EEMConfig:
    """Configuration for the Electromagnetic Energy Memory (EEM) LC-ring simulation.

    All values are in SI units.
    """
    # Network structure
    N: int = 16                 # number of LC cells in the ring

    # Component values
    L: float = 1e-3             # inductance per cell [H]
    C: float = 1e-6             # capacitance per cell [F]
    Cc: float = 1e-6            # coupling capacitance between neighbours [F]
    R: float = 1e-3             # series resistance per cell [Ohm]

    # Time integration
    t_final: float = 5e-2       # final simulation time [s]
    samples: int = 6000         # number of time samples
    rtol: float = 1e-9          # relative tolerance for ODE solver
    atol: float = 1e-12         # absolute tolerance for ODE solver

    # Initial conditions
    initial_cells: Tuple[int, ...] = (0,)  # indices of cells with injected charge
    initial_charge: float = 4e-6           # charge injected in selected cells [C]
    initial_current: float = 0.0           # initial current in each cell [A]

    # Random seed (optional)
    random_seed: Optional[int] = None      # set to an int for reproducibility


# ============================================================
# 2. Core dynamics
# ============================================================

def lc_ring_rhs(t: float, y: np.ndarray, cfg: EEMConfig) -> np.ndarray:
    """Right-hand side of the LC-ring ODE system.

    State vector y = [q_0, ..., q_{N-1}, i_0, ..., i_{N-1}],
    where q_k is charge on capacitor of cell k, and i_k is the current.
    """
    N = cfg.N
    q = y[:N]
    i = y[N:]

    # Periodic neighbours (ring topology)
    q_left = np.roll(q, 1)
    q_right = np.roll(q, -1)

    # dq/dt = i
    dqdt = i

    # Coupling term via capacitors Cc
    coupling = (2.0 * q - q_left - q_right) / cfg.Cc

    # di/dt from KVL in each loop
    didt = (-cfg.R * i - q / cfg.C - coupling) / cfg.L

    return np.concatenate([dqdt, didt])


# ============================================================
# 3. Energy
# ============================================================

def compute_energy(q: np.ndarray, i: np.ndarray, cfg: EEMConfig):
    """Compute per-cell and total electromagnetic energy.

    E_cap = q^2 / (2C)
    E_ind = L * i^2 / 2
    """
    e_cap = q * q / (2.0 * cfg.C)
    e_ind = 0.5 * cfg.L * i * i
    e_cell = e_cap + e_ind
    e_total = float(np.sum(e_cell))
    return e_cell, e_total


# ============================================================
# 4. Simulation driver
# ============================================================

def run_simulation(cfg: EEMConfig):
    """Run the EEM LC-ring simulation.

    Returns:
        t:            time array, shape (T,)
        q_hist:       charges, shape (T, N)
        i_hist:       currents, shape (T, N)
        E_cells_hist: per-cell energy, shape (T, N)
        E_total_hist: total energy, shape (T,)
    """
    if cfg.random_seed is not None:
        np.random.seed(cfg.random_seed)

    N = cfg.N

    # Initial charges and currents
    q0 = np.zeros(N, dtype=float)
    for idx in cfg.initial_cells:
        q0[idx % N] = cfg.initial_charge

    i0 = np.full(N, cfg.initial_current, dtype=float)

    y0 = np.concatenate([q0, i0])

    t_eval = np.linspace(0.0, cfg.t_final, cfg.samples)

    sol = solve_ivp(
        fun=lambda t, y: lc_ring_rhs(t, y, cfg),
        t_span=(0.0, cfg.t_final),
        y0=y0,
        t_eval=t_eval,
        method="RK45",
        rtol=cfg.rtol,
        atol=cfg.atol,
    )

    if not sol.success:
        raise RuntimeError(f"Time integration failed: {sol.message}")

    t = sol.t
    Y = sol.y.T  # shape (T, 2N)

    q_hist = Y[:, :N]
    i_hist = Y[:, N:]

    E_cells_hist = np.zeros_like(q_hist)
    E_total_hist = np.zeros_like(t)

    for k in range(len(t)):
        e_cell, e_tot = compute_energy(q_hist[k], i_hist[k], cfg)
        E_cells_hist[k] = e_cell
        E_total_hist[k] = e_tot

    return t, q_hist, i_hist, E_cells_hist, E_total_hist


# ============================================================
# 5. Memory state detection
# ============================================================

def detect_memory_state(E_cells_hist: np.ndarray, smooth_sigma: float = 1.0):
    """Detect the dominant energy localization cell (memory state).

    We average the per-cell energy over time, smooth the spatial profile,
    and select the index of the maximum as the memory cell.
    """
    spatial_avg = np.mean(E_cells_hist, axis=0)
    smooth_profile = gaussian_filter1d(spatial_avg, sigma=smooth_sigma)
    memory_idx = int(np.argmax(smooth_profile))
    return memory_idx, smooth_profile


# ============================================================
# 6. Plotting
# ============================================================

def plot_results(
    t: np.ndarray,
    E_cells_hist: np.ndarray,
    E_total_hist: np.ndarray,
    cfg: EEMConfig,
    memory_idx: int,
    smooth_profile: np.ndarray,
    show: bool = True,
    save_prefix: Optional[str] = None,
) -> None:
    """Generate publication-ready plots.

    1. Total energy vs time.
    2. Space–time map of per-cell energy.
    3. Spatial energy localization profile.

    If save_prefix is given, each figure is saved as PNG:
      f"{save_prefix}_total_energy.png", etc.
    """
    N = cfg.N

    # --- Total energy ---
    fig1, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(t, E_total_hist, linewidth=1.2)
    ax1.set_title("Total Energy Decay — Electromagnetic Energy Memory (EEM)")
    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel("Energy [J]")
    ax1.grid(True)
    fig1.tight_layout()

    if save_prefix is not None:
        fig1.savefig(f"{save_prefix}_total_energy.png", dpi=300)

    # --- Space–time map of per-cell energy ---
    fig2, ax2 = plt.subplots(figsize=(9, 5))
    im = ax2.imshow(
        E_cells_hist.T,
        aspect="auto",
        origin="lower",
        extent=[t[0], t[-1], 0, N],
        cmap="viridis",
    )
    cbar = fig2.colorbar(im, ax=ax2)
    cbar.set_label("Energy per cell [J]")
    ax2.set_title("High-Resolution Energy Map — EEM LC Ring")
    ax2.set_xlabel("Time [s]")
    ax2.set_ylabel("Cell index")
    fig2.tight_layout()

    if save_prefix is not None:
        fig2.savefig(f"{save_prefix}_energy_map.png", dpi=300)

    # --- Spatial localization profile ---
    fig3, ax3 = plt.subplots(figsize=(8, 4))
    cell_indices = np.arange(N)
    ax3.plot(cell_indices, smooth_profile, linewidth=2.0, label="Average energy profile")
    ax3.axvline(memory_idx, linestyle="--", color="red", label=f"Memory cell = {memory_idx}")
    ax3.set_title("Energy Localization Profile (Memory State Detector)")
    ax3.set_xlabel("Cell index")
    ax3.set_ylabel("Average energy")
    ax3.grid(True)
    ax3.legend()
    fig3.tight_layout()

    if save_prefix is not None:
        fig3.savefig(f"{save_prefix}_memory_profile.png", dpi=300)

    if show:
        plt.show()
    else:
        plt.close("all")


# ============================================================
# 7. Summary
# ============================================================

def summarize_results(t: np.ndarray, E_total_hist: np.ndarray, memory_idx: int) -> None:
    """Print a short summary of the simulation outcome."""
    E_initial = E_total_hist[0]
    E_final = E_total_hist[-1]
    decay_ratio = E_final / E_initial if E_initial != 0 else np.nan

    print("=== Electromagnetic Energy Memory (EEM) — Summary ===")
    print(f"Simulation time: {t[0]:.3e} s → {t[-1]:.3e} s")
    print(f"Initial total energy: {E_initial:.3e} J")
    print(f"Final total energy:   {E_final:.3e} J")
    print(f"Energy decay ratio (final / initial): {decay_ratio:.3f}")
    print(f"Dominant memory cell index: {memory_idx}")


# ============================================================
# 8. Main
# ============================================================

def main() -> None:
    """Entry point: run a default EEM simulation and plot the results."""
    cfg = EEMConfig()  # edit parameters here if you want

    t, q_hist, i_hist, E_cells_hist, E_total_hist = run_simulation(cfg)
    memory_idx, smooth_profile = detect_memory_state(E_cells_hist, smooth_sigma=1.0)
    summarize_results(t, E_total_hist, memory_idx)

    # show=True to see plots, save_prefix to save PNG files
    plot_results(
        t,
        E_cells_hist,
        E_total_hist,
        cfg,
        memory_idx,
        smooth_profile,
        show=True,
        save_prefix=None,
    )


if __name__ == "__main__":
    main()
