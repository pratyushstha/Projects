"""
GUI Interface for RLC Circuit Simulator
Provides interactive interface for circuit parameter input and visualization
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np

from circuit_simulator import create_circuit, SeriesRLCCircuit
from circuit_analysis import CircuitAnalyzer
from plotting_utils import CircuitPlotter

class RLCSimulatorGUI:
    """Main GUI class for RLC Circuit Simulator"""
    
    def __init__(self, root):
        self.root = root
        self.current_circuit = None
        self.plotter = CircuitPlotter()
        self.current_figure = None
        
        # Initialize GUI components
        self.setup_main_interface()
        self.setup_default_values()
        
    def setup_main_interface(self):
        """Setup the main GUI interface"""
        # Create main frames
        self.control_frame = ttk.Frame(self.root)
        self.control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        self.plot_frame = ttk.Frame(self.root)
        self.plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Setup control panel
        self.setup_control_panel()
        
        # Setup plot area
        self.setup_plot_area()
        
    def setup_control_panel(self):
        """Setup the control panel with parameter inputs"""
        # Title
        title_label = ttk.Label(self.control_frame, text="RLC Circuit Simulator", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Circuit Type Selection
        circuit_frame = ttk.LabelFrame(self.control_frame, text="Circuit Configuration", padding=10)
        circuit_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.circuit_type = tk.StringVar(value="series")
        ttk.Radiobutton(circuit_frame, text="Series RLC", variable=self.circuit_type, 
                       value="series", command=self.on_parameter_change).pack(anchor=tk.W)
        ttk.Radiobutton(circuit_frame, text="Parallel RLC", variable=self.circuit_type, 
                       value="parallel", command=self.on_parameter_change).pack(anchor=tk.W)
        
        # Circuit Parameters
        params_frame = ttk.LabelFrame(self.control_frame, text="Circuit Parameters", padding=10)
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Resistance
        ttk.Label(params_frame, text="Resistance (R):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.R_var = tk.StringVar(value="10.0")
        self.R_entry = ttk.Entry(params_frame, textvariable=self.R_var, width=15)
        self.R_entry.grid(row=0, column=1, padx=(5, 0), pady=2)
        self.R_entry.bind('<KeyRelease>', self.on_parameter_change)
        ttk.Label(params_frame, text="Ω").grid(row=0, column=2, sticky=tk.W, padx=(5, 0))
        
        # Inductance
        ttk.Label(params_frame, text="Inductance (L):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.L_var = tk.StringVar(value="0.001")
        self.L_entry = ttk.Entry(params_frame, textvariable=self.L_var, width=15)
        self.L_entry.grid(row=1, column=1, padx=(5, 0), pady=2)
        self.L_entry.bind('<KeyRelease>', self.on_parameter_change)
        ttk.Label(params_frame, text="H").grid(row=1, column=2, sticky=tk.W, padx=(5, 0))
        
        # Capacitance
        ttk.Label(params_frame, text="Capacitance (C):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.C_var = tk.StringVar(value="0.0001")
        self.C_entry = ttk.Entry(params_frame, textvariable=self.C_var, width=15)
        self.C_entry.grid(row=2, column=1, padx=(5, 0), pady=2)
        self.C_entry.bind('<KeyRelease>', self.on_parameter_change)
        ttk.Label(params_frame, text="F").grid(row=2, column=2, sticky=tk.W, padx=(5, 0))
        
        # Input Signal Configuration
        signal_frame = ttk.LabelFrame(self.control_frame, text="Input Signal", padding=10)
        signal_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.input_type = tk.StringVar(value="step")
        ttk.Radiobutton(signal_frame, text="Step Input (DC)", variable=self.input_type, 
                       value="step", command=self.on_parameter_change).pack(anchor=tk.W)
        ttk.Radiobutton(signal_frame, text="Sinusoidal Input (AC)", variable=self.input_type, 
                       value="sinusoidal", command=self.on_parameter_change).pack(anchor=tk.W)
        
        # Sinusoidal parameters (initially disabled)
        self.sine_frame = ttk.Frame(signal_frame)
        self.sine_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(self.sine_frame, text="Frequency:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.freq_var = tk.StringVar(value="50.0")
        self.freq_entry = ttk.Entry(self.sine_frame, textvariable=self.freq_var, width=10)
        self.freq_entry.grid(row=0, column=1, padx=(5, 0), pady=2)
        self.freq_entry.bind('<KeyRelease>', self.on_parameter_change)
        ttk.Label(self.sine_frame, text="Hz").grid(row=0, column=2, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(self.sine_frame, text="Amplitude:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.amp_var = tk.StringVar(value="1.0")
        self.amp_entry = ttk.Entry(self.sine_frame, textvariable=self.amp_var, width=10)
        self.amp_entry.grid(row=1, column=1, padx=(5, 0), pady=2)
        self.amp_entry.bind('<KeyRelease>', self.on_parameter_change)
        ttk.Label(self.sine_frame, text="V").grid(row=1, column=2, sticky=tk.W, padx=(5, 0))
        
        # Simulation Parameters
        sim_frame = ttk.LabelFrame(self.control_frame, text="Simulation Settings", padding=10)
        sim_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(sim_frame, text="Duration:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.duration_var = tk.StringVar(value="5.0")
        self.duration_entry = ttk.Entry(sim_frame, textvariable=self.duration_var, width=15)
        self.duration_entry.grid(row=0, column=1, padx=(5, 0), pady=2)
        self.duration_entry.bind('<KeyRelease>', self.on_parameter_change)
        ttk.Label(sim_frame, text="s").grid(row=0, column=2, sticky=tk.W, padx=(5, 0))
        
        ttk.Label(sim_frame, text="Time Points:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.points_var = tk.StringVar(value="1000")
        self.points_entry = ttk.Entry(sim_frame, textvariable=self.points_var, width=15)
        self.points_entry.grid(row=1, column=1, padx=(5, 0), pady=2)
        self.points_entry.bind('<KeyRelease>', self.on_parameter_change)
        
        # Control Buttons
        button_frame = ttk.Frame(self.control_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Simulate", command=self.simulate_circuit).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Frequency Response", command=self.show_frequency_response).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Compare Damping", command=self.compare_damping).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Save Plot", command=self.save_plot).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Reset", command=self.reset_parameters).pack(fill=tk.X, pady=2)
        
        # Analysis Display
        self.analysis_frame = ttk.LabelFrame(self.control_frame, text="Circuit Analysis", padding=10)
        self.analysis_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create scrollable text widget for analysis
        self.analysis_text = tk.Text(self.analysis_frame, height=15, width=40, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(self.analysis_frame, orient=tk.VERTICAL, command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=scrollbar.set)
        
        self.analysis_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Update sine frame state
        self.update_sine_frame_state()
        
    def setup_plot_area(self):
        """Setup the matplotlib plot area"""
        # Create initial empty plot
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.ax.set_title("RLC Circuit Simulator - Select parameters and click Simulate")
        self.ax.grid(True, alpha=0.3)
        
        # Embed plot in tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        toolbar.update()
        
    def setup_default_values(self):
        """Setup default circuit values and perform initial simulation"""
        self.on_parameter_change()
        
    def update_sine_frame_state(self):
        """Enable/disable sinusoidal parameters based on input type"""
        state = tk.NORMAL if self.input_type.get() == "sinusoidal" else tk.DISABLED
        
        for widget in self.sine_frame.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.configure(state=state)
                
    def on_parameter_change(self, event=None):
        """Called when any parameter changes"""
        self.update_sine_frame_state()
        self.update_circuit_analysis()
        
    def get_circuit_parameters(self):
        """Get and validate circuit parameters from GUI"""
        try:
            R = float(self.R_var.get())
            L = float(self.L_var.get())
            C = float(self.C_var.get())
            
            if R <= 0 or L <= 0 or C <= 0:
                raise ValueError("All parameters must be positive")
                
            return R, L, C
            
        except ValueError as e:
            messagebox.showerror("Invalid Parameters", f"Error in circuit parameters: {e}")
            return None
            
    def get_simulation_parameters(self):
        """Get and validate simulation parameters"""
        try:
            duration = float(self.duration_var.get())
            points = int(self.points_var.get())
            
            if duration <= 0 or points <= 0:
                raise ValueError("Duration and points must be positive")
                
            return duration, points
            
        except ValueError as e:
            messagebox.showerror("Invalid Parameters", f"Error in simulation parameters: {e}")
            return None
            
    def get_signal_parameters(self):
        """Get signal parameters for sinusoidal input"""
        try:
            frequency = float(self.freq_var.get())
            amplitude = float(self.amp_var.get())
            
            if frequency <= 0 or amplitude <= 0:
                raise ValueError("Frequency and amplitude must be positive")
                
            return frequency, amplitude
            
        except ValueError as e:
            messagebox.showerror("Invalid Parameters", f"Error in signal parameters: {e}")
            return None
            
    def create_current_circuit(self):
        """Create circuit instance with current parameters"""
        params = self.get_circuit_parameters()
        if params is None:
            return None
            
        R, L, C = params
        circuit_type = self.circuit_type.get()
        
        try:
            return create_circuit(circuit_type, R, L, C)
        except Exception as e:
            messagebox.showerror("Circuit Error", f"Error creating circuit: {e}")
            return None
            
    def update_circuit_analysis(self):
        """Update the circuit analysis display"""
        circuit = self.create_current_circuit()
        if circuit is None:
            return
            
        self.current_circuit = circuit
        
        try:
            # Get analysis
            analysis = CircuitAnalyzer.calculate_time_constants(circuit)
            insights = CircuitAnalyzer.get_educational_insights(circuit)
            
            # Clear and update analysis text
            self.analysis_text.delete(1.0, tk.END)
            
            # Add circuit parameters
            params = self.get_circuit_parameters()
            R, L, C = params
            
            analysis_text = f"""CIRCUIT PARAMETERS:
R = {R:.6f} Ω
L = {L:.6f} H  
C = {C:.6f} F

DERIVED PARAMETERS:
Natural Frequency: {analysis['natural_frequency_hz']:.3f} Hz
Resonance ω₀: {analysis['natural_frequency_rad']:.3f} rad/s
Damping Factor ζ: {analysis['damping_factor']:.4f}
Quality Factor Q: {analysis['q_factor']:.3f}
Damping Type: {analysis['damping_type']}

"""
            
            # Add damping-specific information
            if analysis['damping_factor'] < 1:
                analysis_text += f"""UNDERDAMPED RESPONSE:
Damped Frequency: {analysis.get('damped_frequency_hz', 0):.3f} Hz
Oscillation Period: {analysis.get('period_damped', 0):.4f} s
Envelope τ: {analysis.get('envelope_time_constant', 0):.4f} s

"""
            elif analysis['damping_factor'] > 1:
                analysis_text += f"""OVERDAMPED RESPONSE:
Fast Time Constant: {analysis.get('time_constant_1', 0):.4f} s
Slow Time Constant: {analysis.get('time_constant_2', 0):.4f} s

"""
            else:
                analysis_text += f"""CRITICALLY DAMPED:
Time Constant: {analysis.get('time_constant', 0):.4f} s

"""
            
            # Add settling times
            if 'settling_time_2_percent' in analysis:
                analysis_text += f"""SETTLING TIMES:
2% Settling: {analysis['settling_time_2_percent']:.4f} s
5% Settling: {analysis['settling_time_5_percent']:.4f} s

"""
            
            # Add educational insights
            analysis_text += "EDUCATIONAL INSIGHTS:\n"
            for insight in insights:
                analysis_text += f"• {insight}\n"
                
            self.analysis_text.insert(1.0, analysis_text)
            
        except Exception as e:
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(1.0, f"Error in analysis: {e}")
            
    def simulate_circuit(self):
        """Perform circuit simulation and update plot"""
        circuit = self.create_current_circuit()
        if circuit is None:
            return
            
        sim_params = self.get_simulation_parameters()
        if sim_params is None:
            return
            
        duration, points = sim_params
        
        try:
            # Perform simulation based on input type
            if self.input_type.get() == "step":
                t, voltage, current = circuit.simulate_step_response(duration, points)
                input_label = "Step"
            else:
                signal_params = self.get_signal_parameters()
                if signal_params is None:
                    return
                    
                frequency, amplitude = signal_params
                t, voltage, current = circuit.simulate_sinusoidal_response(
                    frequency, amplitude, duration, points)
                input_label = f"Sinusoidal ({frequency} Hz)"
                
            # Clear previous plot and create new one
            plt.close(self.fig)
            self.fig = self.plotter.plot_time_response(t, voltage, current, circuit, input_label)
            
            # Update canvas
            self.canvas.figure = self.fig
            self.canvas.draw()
            
            # Store current figure for saving
            self.current_figure = self.fig
            
        except Exception as e:
            messagebox.showerror("Simulation Error", f"Error in simulation: {e}")
            
    def show_frequency_response(self):
        """Show frequency response plot"""
        circuit = self.create_current_circuit()
        if circuit is None:
            return
            
        try:
            # Clear previous plot and create frequency response
            plt.close(self.fig)
            self.fig = self.plotter.plot_frequency_response(circuit)
            
            # Update canvas
            self.canvas.figure = self.fig
            self.canvas.draw()
            
            # Store current figure for saving
            self.current_figure = self.fig
            
        except Exception as e:
            messagebox.showerror("Frequency Response Error", f"Error creating frequency response: {e}")
            
    def compare_damping(self):
        """Show damping comparison plot"""
        params = self.get_circuit_parameters()
        if params is None:
            return
            
        R, L, C = params
        
        try:
            # Create range of R values to show different damping
            R_values = [R/10, R/3, R, R*3, R*10]
            
            # Clear previous plot and create comparison
            plt.close(self.fig)
            self.fig = self.plotter.plot_damping_comparison(L, C, R_values)
            
            # Update canvas
            self.canvas.figure = self.fig
            self.canvas.draw()
            
            # Store current figure for saving
            self.current_figure = self.fig
            
        except Exception as e:
            messagebox.showerror("Damping Comparison Error", f"Error creating damping comparison: {e}")
            
    def save_plot(self):
        """Save current plot to file"""
        if self.current_figure is None:
            messagebox.showwarning("No Plot", "No plot to save. Please run a simulation first.")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"), ("SVG files", "*.svg")],
            title="Save Plot"
        )
        
        if filename:
            try:
                self.current_figure.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Plot saved to {filename}")
            except Exception as e:
                messagebox.showerror("Save Error", f"Error saving plot: {e}")
                
    def reset_parameters(self):
        """Reset all parameters to default values"""
        self.R_var.set("10.0")
        self.L_var.set("0.001")
        self.C_var.set("0.0001")
        self.freq_var.set("50.0")
        self.amp_var.set("1.0")
        self.duration_var.set("5.0")
        self.points_var.set("1000")
        self.circuit_type.set("series")
        self.input_type.set("step")
        
        self.on_parameter_change()
        
        # Reset plot
        plt.close(self.fig)
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.ax.set_title("RLC Circuit Simulator - Select parameters and click Simulate")
        self.ax.grid(True, alpha=0.3)
        
        self.canvas.figure = self.fig
        self.canvas.draw()
