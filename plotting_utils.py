"""
Plotting Utilities for RLC Circuit Visualization
Provides comprehensive plotting functions for circuit analysis
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np
from circuit_analysis import CircuitAnalyzer

class CircuitPlotter:
    """Utility class for creating educational plots of RLC circuit responses"""
    
    def __init__(self):
        # Set up matplotlib style for educational plots
        plt.style.use('default')
        self.setup_plot_style()
    
    def setup_plot_style(self):
        """Configure matplotlib for clear, educational plots"""
        plt.rcParams.update({
            'font.size': 10,
            'axes.titlesize': 12,
            'axes.labelsize': 11,
            'legend.fontsize': 9,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'figure.titlesize': 14,
            'lines.linewidth': 2,
            'grid.alpha': 0.3,
            'axes.grid': True
        })
    
    def plot_time_response(self, t, voltage, current, circuit, input_type="Step"):
        """
        Create comprehensive time-domain response plots
        
        Args:
            t (array): Time array
            voltage (array): Voltage response
            current (array): Current response  
            circuit (RLCCircuit): Circuit instance
            input_type (str): Type of input signal
        """
        # Create figure with subplots
        fig = plt.figure(figsize=(14, 10))
        fig.suptitle(f'{type(circuit).__name__.replace("RLCCircuit", " RLC Circuit")} - {input_type} Response', 
                    fontsize=16, fontweight='bold')
        
        # Create grid layout
        gs = fig.add_gridspec(3, 2, height_ratios=[2, 2, 1], width_ratios=[3, 1], 
                             hspace=0.3, wspace=0.3)
        
        # Plot voltage response
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.plot(t, voltage, 'b-', linewidth=2.5, label='Voltage Response')
        ax1.set_xlabel('Time (seconds)')
        ax1.set_ylabel('Voltage (V)')
        ax1.set_title('Voltage vs Time', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # Add envelope for underdamped response
        if circuit.get_damping_factor() < 1:
            analysis = CircuitAnalyzer.calculate_time_constants(circuit)
            if 'envelope_time_constant' in analysis:
                tau = analysis['envelope_time_constant']
                envelope = np.exp(-t / tau)
                peak_voltage = np.max(np.abs(voltage))
                ax1.plot(t, peak_voltage * envelope, 'r--', alpha=0.7, label='Envelope')
                ax1.plot(t, -peak_voltage * envelope, 'r--', alpha=0.7)
                ax1.legend()
        
        # Plot current response
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.plot(t, current, 'r-', linewidth=2.5, label='Current Response')
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('Current (A)')
        ax2.set_title('Current vs Time', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        # Phase plot (Voltage vs Current)
        ax3 = fig.add_subplot(gs[0, 1])
        ax3.plot(voltage, current, 'g-', linewidth=2, alpha=0.8)
        ax3.set_xlabel('Voltage (V)')
        ax3.set_ylabel('Current (A)')
        ax3.set_title('Phase Plot\n(V vs I)', fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # Add arrow to show direction
        if len(voltage) > 10:
            mid_idx = len(voltage) // 2
            ax3.annotate('', xy=(voltage[mid_idx+1], current[mid_idx+1]), 
                        xytext=(voltage[mid_idx], current[mid_idx]),
                        arrowprops=dict(arrowstyle='->', color='red', lw=2))
        
        # Circuit parameters and analysis
        ax4 = fig.add_subplot(gs[1, 1])
        ax4.axis('off')
        
        # Create parameter text
        param_text = f"""Circuit Parameters:
R = {circuit.R:.3f} Ω
L = {circuit.L:.6f} H
C = {circuit.C:.6f} F

Analysis:
f₀ = {circuit.f_0:.3f} Hz
ζ = {circuit.get_damping_factor():.4f}
Q = {circuit.get_q_factor():.3f}
Type: {circuit.get_damping_type()}"""
        
        ax4.text(0.05, 0.95, param_text, transform=ax4.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='monospace',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
        
        # Educational insights
        ax5 = fig.add_subplot(gs[2, :])
        ax5.axis('off')
        
        insights = CircuitAnalyzer.get_educational_insights(circuit)
        insight_text = "Key Insights:\n" + "\n".join(insights[:4])  # Show first 4 insights
        
        ax5.text(0.02, 0.9, insight_text, transform=ax5.transAxes, fontsize=9,
                verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8))
        
        plt.tight_layout()
        return fig
    
    def plot_frequency_response(self, circuit):
        """
        Plot frequency response (Bode plot) of the circuit
        
        Args:
            circuit (RLCCircuit): Circuit instance
        """
        # Create frequency range
        f_0 = circuit.f_0
        f_min = f_0 / 1000
        f_max = f_0 * 1000
        frequencies = np.logspace(np.log10(f_min), np.log10(f_max), 1000)
        
        # Get frequency response
        freq_response = CircuitAnalyzer.analyze_frequency_response(circuit, frequencies)
        
        # Create Bode plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        fig.suptitle(f'{type(circuit).__name__.replace("RLCCircuit", " RLC Circuit")} - Frequency Response', 
                    fontsize=14, fontweight='bold')
        
        # Magnitude plot
        ax1.semilogx(frequencies, freq_response['magnitude_db'], 'b-', linewidth=2.5)
        ax1.set_ylabel('Magnitude (dB)')
        ax1.set_title('Magnitude Response')
        ax1.grid(True, alpha=0.3)
        ax1.axvline(f_0, color='red', linestyle='--', alpha=0.7, label=f'f₀ = {f_0:.3f} Hz')
        ax1.legend()
        
        # Phase plot
        ax2.semilogx(frequencies, freq_response['phase_deg'], 'r-', linewidth=2.5)
        ax2.set_xlabel('Frequency (Hz)')
        ax2.set_ylabel('Phase (degrees)')
        ax2.set_title('Phase Response')
        ax2.grid(True, alpha=0.3)
        ax2.axvline(f_0, color='red', linestyle='--', alpha=0.7, label=f'f₀ = {f_0:.3f} Hz')
        ax2.legend()
        
        plt.tight_layout()
        return fig
    
    def plot_comparison(self, circuits_data, input_type="Step"):
        """
        Plot comparison of multiple circuit responses
        
        Args:
            circuits_data (list): List of tuples (circuit, t, voltage, current, label)
            input_type (str): Type of input signal
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        fig.suptitle(f'Circuit Response Comparison - {input_type} Input', 
                    fontsize=14, fontweight='bold')
        
        colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown']
        
        for i, (circuit, t, voltage, current, label) in enumerate(circuits_data):
            color = colors[i % len(colors)]
            
            # Plot voltage
            ax1.plot(t, voltage, color=color, linewidth=2, label=f'{label} (ζ={circuit.get_damping_factor():.3f})')
            
            # Plot current
            ax2.plot(t, current, color=color, linewidth=2, label=f'{label}')
        
        ax1.set_ylabel('Voltage (V)')
        ax1.set_title('Voltage Response Comparison')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        ax2.set_xlabel('Time (seconds)')
        ax2.set_ylabel('Current (A)')
        ax2.set_title('Current Response Comparison')
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        
        plt.tight_layout()
        return fig
    
    def plot_damping_comparison(self, L, C, R_values):
        """
        Create educational plot showing effect of different damping factors
        
        Args:
            L (float): Inductance value
            C (float): Capacitance value
            R_values (list): List of resistance values to compare
        """
        from circuit_simulator import SeriesRLCCircuit
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Effect of Damping Factor on RLC Circuit Response', fontsize=16, fontweight='bold')
        
        colors = ['blue', 'red', 'green', 'orange', 'purple']
        damping_types = []
        
        for i, R in enumerate(R_values):
            circuit = SeriesRLCCircuit(R, L, C)
            t, voltage, current = circuit.simulate_step_response(duration=3.0)
            
            color = colors[i % len(colors)]
            zeta = circuit.get_damping_factor()
            damping_type = circuit.get_damping_type()
            
            label = f'R={R}Ω, ζ={zeta:.3f} ({damping_type})'
            damping_types.append((R, zeta, damping_type))
            
            # Voltage response
            axes[0,0].plot(t, voltage, color=color, linewidth=2, label=label)
            
            # Current response
            axes[0,1].plot(t, current, color=color, linewidth=2, label=label)
            
            # Phase plot
            axes[1,0].plot(voltage, current, color=color, linewidth=2, label=label)
        
        # Configure plots
        axes[0,0].set_title('Voltage Response')
        axes[0,0].set_ylabel('Voltage (V)')
        axes[0,0].grid(True, alpha=0.3)
        axes[0,0].legend()
        
        axes[0,1].set_title('Current Response')
        axes[0,1].set_ylabel('Current (A)')
        axes[0,1].grid(True, alpha=0.3)
        axes[0,1].legend()
        
        axes[1,0].set_title('Phase Plot (V vs I)')
        axes[1,0].set_xlabel('Voltage (V)')
        axes[1,0].set_ylabel('Current (A)')
        axes[1,0].grid(True, alpha=0.3)
        axes[1,0].legend()
        
        # Summary table
        axes[1,1].axis('off')
        table_data = []
        for R, zeta, damping_type in damping_types:
            table_data.append([f'{R:.1f}', f'{zeta:.3f}', damping_type])
        
        table = axes[1,1].table(cellText=table_data,
                               colLabels=['R (Ω)', 'ζ', 'Damping Type'],
                               cellLoc='center',
                               loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        axes[1,1].set_title('Damping Summary', fontweight='bold')
        
        plt.tight_layout()
        return fig
