import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QComboBox, QCheckBox, 
                             QSlider, QDoubleSpinBox, QGroupBox, QPushButton, 
                             QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt

class QuantumState:
    def __init__(self, n, l, j, mj):
        self.n = n
        self.l = l
        self.j = j
        self.mj = mj
        self.s = 0.5
        self.energy = 0.0 # Last calculated total energy
        
        colors = ['#1f77b4', '#2ca02c', '#d62728', '#9467bd'] 
        self.color = colors[l] if l < len(colors) else '#333333'
        
        linestyles = ['-', '--', '-.', ':']
        idx = int(abs(self.mj) + 0.5) % len(linestyles)
        self.linestyle = linestyles[idx]

    def get_name(self):
        orbitals = ['s', 'p', 'd', 'f']
        orb = orbitals[self.l] if self.l < len(orbitals) else str(self.l)
        j_str = f"{int(self.j*2)}/2"
        mj_str = f"{self.mj:+.1f}"
        return f"{self.n}{orb}_{{{j_str}}} (mj={mj_str})"

class HydrogenPerturbationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hydrogen Atom Perturbation Simulator V3 - SC CAT Edition")
        self.setGeometry(50, 50, 1300, 750)
        
        self.alpha = 1 / 137.036
        self.Ry_ueV = 13.6 * 1e6  
        self.mu_B = 57.88  
        self.e_a0 = 8.478e-30 # e * a0 (Coulomb * meter) - Approx for Stark
        
        self.states = []
        self.initUI()
        self.generate_states()
        self.update_plot()

    def initUI(self):
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # LEFT PANEL
        control_panel = QVBoxLayout()
        control_panel.setAlignment(Qt.AlignTop)
        
        group_n = QGroupBox("Quantum State")
        layout_n = QVBoxLayout()
        self.combo_n = QComboBox()
        self.combo_n.addItems(["n = 1", "n = 2", "n = 3"])
        self.combo_n.setCurrentIndex(1) 
        self.combo_n.currentIndexChanged.connect(self.on_n_changed)
        layout_n.addWidget(QLabel("Principal Quantum Number (n):"))
        layout_n.addWidget(self.combo_n)
        group_n.setLayout(layout_n)
        control_panel.addWidget(group_n)

        group_h = QGroupBox("Hamiltonian Terms")
        layout_h = QVBoxLayout()
        self.cb_fs = QCheckBox("Fine Structure (Relativistic + S-O)")
        self.cb_fs.setChecked(True)
        self.cb_fs.stateChanged.connect(self.update_plot)
        
        self.cb_lamb = QCheckBox("Lamb Shift")
        self.cb_lamb.setChecked(True)
        self.cb_lamb.stateChanged.connect(self.update_plot)
        
        self.cb_zeeman = QCheckBox("Zeeman Effect (Magnetic Field)")
        self.cb_zeeman.setChecked(True)
        self.cb_zeeman.stateChanged.connect(self.update_plot)
        
        self.cb_stark = QCheckBox("Stark Effect (Electric Field)")
        self.cb_stark.setChecked(False)
        self.cb_stark.stateChanged.connect(self.update_plot)
        
        layout_h.addWidget(self.cb_fs)
        layout_h.addWidget(self.cb_lamb)
        layout_h.addWidget(self.cb_zeeman)
        layout_h.addWidget(self.cb_stark)
        group_h.setLayout(layout_h)
        control_panel.addWidget(group_h)

        group_fields = QGroupBox("External Field Parameters")
        layout_fields = QVBoxLayout()
        
        layout_fields.addWidget(QLabel("Magnetic Field (B_z) [Tesla]:"))
        self.spin_b = QDoubleSpinBox()
        self.spin_b.setRange(0.0, 5.0)
        self.spin_b.setSingleStep(0.1)
        self.spin_b.setValue(1.0)
        self.spin_b.valueChanged.connect(self.update_plot)
        layout_fields.addWidget(self.spin_b)
        
        layout_fields.addWidget(QLabel("Electric Field (E_z) [10^6 V/m]:"))
        self.spin_e = QDoubleSpinBox()
        self.spin_e.setRange(0.0, 10.0)
        self.spin_e.setSingleStep(0.5)
        self.spin_e.setValue(1.0)
        self.spin_e.valueChanged.connect(self.update_plot)
        layout_fields.addWidget(self.spin_e)
        
        group_fields.setLayout(layout_fields)
        control_panel.addWidget(group_fields)

        group_tools = QGroupBox("Analysis & Output")
        layout_tools = QVBoxLayout()
        
        self.btn_spectrum = QPushButton("Analyze Transition Spectrum")
        self.btn_spectrum.clicked.connect(self.analyze_spectrum)
        layout_tools.addWidget(self.btn_spectrum)
        
        self.btn_export = QPushButton("Export Data and Plot")
        self.btn_export.clicked.connect(self.export_data)
        layout_tools.addWidget(self.btn_export)
        
        group_tools.setLayout(layout_tools)
        control_panel.addWidget(group_tools)

        control_widget = QWidget()
        control_widget.setLayout(control_panel)
        control_widget.setFixedWidth(380)
        main_layout.addWidget(control_widget)

        # RIGHT PANEL (Plot)
        self.figure, self.ax = plt.subplots(figsize=(9, 6))
        self.canvas = FigureCanvas(self.figure)
        main_layout.addWidget(self.canvas)
        self.figure.subplots_adjust(right=0.72, left=0.1)

    def on_n_changed(self):
        self.generate_states()
        self.update_plot()

    def generate_states(self):
        self.states = []
        n = self.combo_n.currentIndex() + 1
        for l in range(n):
            j_values = [l - 0.5, l + 0.5] if l > 0 else [0.5]
            for j in j_values:
                mj = -j
                while mj <= j + 0.001:
                    self.states.append(QuantumState(n, l, j, mj))
                    mj += 1.0

    def calc_fine_structure(self, state):
        return -self.Ry_ueV * (self.alpha**2 / state.n**3) * (1 / (state.j + 0.5) - 0.75 / state.n)

    def calc_lamb_shift(self, state):
        if state.l == 0:
            return 4.37 * (8 / state.n**3) 
        return 0.0

    def calc_zeeman_shift(self, state, B):
        if state.j == 0:
            gj = 0
        else:
            gj = 1 + (state.j*(state.j+1) - state.l*(state.l+1) + state.s*(state.s+1)) / (2 * state.j * (state.j+1))
        return self.mu_B * gj * state.mj * B

    def calc_stark_shift(self, state, E_field):
        # Simplified approximate Stark shift (Demonstration purpose)
        if state.l > 0:
            return 15.0 * E_field * state.n * state.mj / (state.l + 1)
        return 0.0

    def update_plot(self):
        self.ax.clear()
        
        B_field = self.spin_b.value()
        E_field = self.spin_e.value()

        stages = ["$H_0$"]
        if self.cb_fs.isChecked(): stages.append("$+H_{fs}$")
        if self.cb_lamb.isChecked(): stages.append("$+H_{Lamb}$")
        if self.cb_zeeman.isChecked(): stages.append("$+H_{Zeeman}$")
        if self.cb_stark.isChecked(): stages.append("$+H_{Stark}$")

        for state in self.states:
            energies = [0.0]  
            
            if self.cb_fs.isChecked(): energies.append(energies[-1] + self.calc_fine_structure(state))
            if self.cb_lamb.isChecked(): energies.append(energies[-1] + self.calc_lamb_shift(state))
            if self.cb_zeeman.isChecked(): energies.append(energies[-1] + self.calc_zeeman_shift(state, B_field))
            if self.cb_stark.isChecked(): energies.append(energies[-1] + self.calc_stark_shift(state, E_field))

            state.energy = energies[-1] # Saving final energy for spectrum analysis

            self.ax.plot(range(len(energies)), energies, marker='o', markersize=6, 
                         color=state.color, linestyle=state.linestyle, 
                         linewidth=2.5, label=f'${state.get_name()}$')

        self.ax.set_xticks(range(len(stages)))
        self.ax.set_xticklabels(stages, fontsize=11)
        self.ax.set_ylabel(r"Energy Shift $\Delta E$ ($\mu$eV)", fontsize=12, fontweight='bold')
        
        n_val = self.combo_n.currentIndex() + 1
        base_E_eV = -13.6 / (n_val**2)
        
        self.ax.set_title(f"n={n_val} Level Splittings (Base: {base_E_eV:.2f} eV)", 
                          fontsize=14, fontweight='bold')
        
        self.ax.grid(axis='y', linestyle='--', alpha=0.6)
        self.ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), fontsize=10, 
                       frameon=True, shadow=True)

        self.canvas.draw()

    def analyze_spectrum(self):
        # Quantum Selection Rules: Delta l = +-1, Delta mj = 0, +-1
        transitions = []
        for i, s1 in enumerate(self.states):
            for s2 in self.states[i+1:]:
                dl = abs(s1.l - s2.l)
                dmj = abs(s1.mj - s2.mj)
                if dl == 1 and dmj <= 1:
                    dE_uev = abs(s1.energy - s2.energy)
                    if dE_uev > 0.1: # Filter out very small energy differences
                        transitions.append(f"{s1.get_name().replace('$', '')} <--> {s2.get_name().replace('$', '')}:  ΔE = {dE_uev:.2f} μeV")
        
        msg = QMessageBox()
        msg.setWindowTitle("Allowed Optical Transitions (Dipole)")
        if transitions:
            msg.setText(f"{len(transitions)} valid dipole transitions found.\n\n" + "\n".join(transitions[:15]))
            if len(transitions) > 15:
                msg.setInformativeText("...and more. (Export to see all).")
        else:
            msg.setText("No allowed/measurable transitions found at this level.")
        msg.exec_()

    def export_data(self):
        # File save dialog (Default name is assigned)
        path, _ = QFileDialog.getSaveFileName(self, "Save Data", "schrodingers_siths_data.csv", "CSV Files (*.csv)")
        if path:
            # Save CSV
            with open(path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["n", "l", "j", "mj", "Energy Shift (ueV)"])
                for s in self.states:
                    writer.writerow([s.n, s.l, s.j, s.mj, f"{s.energy:.4f}"])
            
            # Save plot as PNG (same directory as CSV)
            png_path = path.replace(".csv", "_plot.png")
            self.figure.savefig(png_path, bbox_inches='tight', dpi=300)
            
            QMessageBox.information(self, "Success", f"Data successfully saved:\n{path}\n{png_path}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion') 
    window = HydrogenPerturbationApp()
    window.show()
    sys.exit(app.exec_())