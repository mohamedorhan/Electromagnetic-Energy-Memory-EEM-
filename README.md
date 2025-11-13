# Electromagnetic Energy Memory (EEM)

**Electromagnetic Energy Memory (EEM)** is a mathematical and computational framework that demonstrates how energy can be stored as **long-lived electromagnetic memory states** inside purely resonant LC networks—without any chemical reactions.

This repository contains:

- Full Python simulation of the EEM model  
- High-resolution numerical experiments  
- Publication-ready figures  
- The official research paper  

---

## 📄 Official Research Paper

**DOI:** https://doi.org/10.5281/zenodo.17597289  
**Author:** Mohamed Orhan Zeinel  
**ORCID:** https://orcid.org/0009-0008-1139-8102  

PDF is included in the repository.

---

## 🔬 Scientific Overview

### What is EEM?
EEM proposes that energy can be stored not as chemical potential (like batteries), but as **stable spatial patterns** in a network of coupled LC resonators.

A memory state is a localized energy distribution that:

1. Remains confined to a small region of the network  
2. Persists for long times despite electrical losses  

This creates a new class of **non-chemical energy storage**.

---

## 📁 Repository Structure


├── eem_energy_memory.py        # Main simulation script
├── Electromagnetic_Energy_Memory__EEM_.pdf   # Full scientific paper
├── README.md                   # This file
└── Figures/                    # Simulation output figures (PNG)

---

## 🧠 Mathematical Model (Brief)

We consider a ring of \(N\) identical RLC cells with coupling capacitance \(C_c\).

Equations:

\[
\frac{dq_k}{dt} = i_k
\]

\[
L\frac{di_k}{dt}
= -Ri_k - \frac{1}{C}q_k - \frac{1}{C_c}(2q_k - q_{k-1} - q_{k+1})
\]

Energy per cell:

\[
E_k(t) = \frac{q_k^2}{2C} + \frac{L i_k^2}{2}
\]

Localized peaks in \(E_k\) correspond to **energy memory states**.

---

## ▶️ Running the Simulation

### Requirements

Python 3.9+
numpy
scipy
matplotlib
### Run
```bash
python eem_energy_memory.py

The script automatically generates:
	•	Total energy decay plot
	•	Space–time energy map
	•	Memory localization profile

All plots are saved in the Figures directory.

⸻

🧪 Configuration Example

from eem_energy_memory import EEMConfig, run_simulation

cfg = EEMConfig(
    N=16,
    L=1e-3,
    C=1e-6,
    Cc=1e-6,
    R=1e-3,
    t_final=0.05,
    samples=6000,
    initial_cells=(0,),
    initial_charge=4e-6,
)

t, q, i, E, E_tot = run_simulation(cfg)

📊 Output Examples
	•	*_total_energy.png – Total stored energy vs time
	•	*_energy_map.png – Heatmap of energy over space/time
	•	*_memory_profile.png – Localized memory state detector

⸻

📚 Citation

If you use this work, please cite:

Electromagnetic Energy Memory (EEM):
A Resonant and Network-Based Framework for Non-Chemical Energy Storage
Mohamed Orhan Zeinel, 2025.
DOI: 10.5281/zenodo.17597289

GitHub Repository (2025).
