# Hydrogen Atom Perturbation Simulator V3 - SC CAT Edition ⚛️🐈‍⬛

A comprehensive, interactive Python GUI application built with PyQt5 and Matplotlib to visualize and calculate the energy level splittings of the Hydrogen atom under various quantum mechanical perturbations. 

This tool is designed for physics students, researchers, and educators to intuitively explore how external fields and relativistic corrections affect atomic energy levels.

![Simulator Screenshot](schrödingers_siths_data_plot.png) 
*(Note: Add a screenshot of the app running here and name it `screenshot.png` in your repo)*

## ✨ Features

- **Interactive GUI:** Easy-to-use control panel to select the Principal Quantum Number ($n$).
- **Dynamic Hamiltonian Terms:** Toggle specific physical phenomena on/off to see their isolated or combined effects on the energy levels:
  - **Fine Structure ($H_{fs}$):** Relativistic momentum correction + Spin-Orbit coupling.
  - **Lamb Shift ($H_{Lamb}$):** Quantum Electrodynamics (QED) vacuum fluctuation corrections.
  - **Zeeman Effect ($H_{Zeeman}$):** Energy splitting under an external magnetic field ($B_z$).
  - **Stark Effect ($H_{Stark}$):** Energy splitting under an external electric field ($E_z$).
- **Real-time Plotting:** Dynamic visualization of energy shifts ($\Delta E$) in $\mu$eV as terms are sequentially applied.
- **Spectrum Analyzer:** Automatically calculates and lists allowed optical dipole transitions based on quantum selection rules ($\Delta l = \pm 1$, $\Delta m_j = 0, \pm 1$).
- **Export Capabilities:** Save your calculated energy states as a `.csv` file and export the generated high-resolution plot as a `.png` for research logs or presentations.

## 🧰 Prerequisites

To run this simulator, you need Python 3.x installed on your machine along with a few external libraries. 

The required libraries are:
- `numpy` (For numerical operations)
- `matplotlib` (For plotting the energy levels)
- `PyQt5` (For the Graphical User Interface)

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/hydrogen-perturbation-simulator.git](https://github.com/yourusername/hydrogen-perturbation-simulator.git)
   cd hydrogen-perturbation-simulator

2. **Create a virtual enviroment (Optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate #on Linux
   venv\Scripts\activate #on Windows
3. **Install the required dependencies**
   ```bash
   pip install numpy matplotlib PyQt5

**Usage**
Run the main script from your terminal:
```bash 
python H_perturbation.py
