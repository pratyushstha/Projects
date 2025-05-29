"""
RLC Circuit Simulator Core Classes
Implements series and parallel RLC circuit models with differential equation solving
"""

import numpy as np
import scipy.signal as signal
from abc import ABC, abstractmethod
import math

class RLCCircuit(ABC):
    """Abstract base class for RLC circuits"""
    
    def __init__(self, R, L, C):
        """
        Initialize circuit parameters
        
        Args:
            R (float): Resistance in Ohms
            L (float): Inductance in Henries  
            C (float): Capacitance in Farads
        """
        if R <= 0 or L <= 0 or C <= 0:
            raise ValueError("All circuit parameters (R, L, C) must be positive")
            
        self.R = R  # Resistance (Ohms)
        self.L = L  # Inductance (Henries)
        self.C = C  # Capacitance (Farads)
        
        # Calculate derived parameters
        self.omega_0 = 1 / math.sqrt(L * C)  # Natural frequency (rad/s)
        self.f_0 = self.omega_0 / (2 * math.pi)  # Natural frequency (Hz)
        
    @abstractmethod
    def get_transfer_function(self):
        """Get the transfer function for the specific circuit configuration"""
        pass
    
    @abstractmethod
    def get_damping_factor(self):
        """Calculate the damping factor for the circuit"""
        pass
    
    def get_q_factor(self):
        """Calculate the quality factor of the circuit"""
        return 1 / (2 * self.get_damping_factor())
    
    def get_damping_type(self):
        """Determine the damping type based on damping factor"""
        zeta = self.get_damping_factor()
        if zeta < 1:
            return "Underdamped"
        elif zeta == 1:
            return "Critically Damped"
        else:
            return "Overdamped"
    
    def simulate_step_response(self, duration=5.0, num_points=1000):
        """
        Simulate step response of the circuit
        
        Args:
            duration (float): Simulation duration in seconds
            num_points (int): Number of time points
            
        Returns:
            tuple: (time_array, voltage_response, current_response)
        """
        # Get transfer function
        tf = self.get_transfer_function()
        
        # Create time vector
        t = np.linspace(0, duration, num_points)
        
        # Calculate step response
        t_step, y_step = signal.step(tf, T=t)
        
        # Calculate current response (derivative of voltage for capacitor)
        current = self._calculate_current_response(t_step, y_step)
        
        return t_step, y_step, current
    
    def simulate_sinusoidal_response(self, frequency=1.0, amplitude=1.0, duration=5.0, num_points=1000):
        """
        Simulate sinusoidal input response
        
        Args:
            frequency (float): Input frequency in Hz
            amplitude (float): Input amplitude in Volts
            duration (float): Simulation duration in seconds
            num_points (int): Number of time points
            
        Returns:
            tuple: (time_array, voltage_response, current_response)
        """
        # Create time vector
        t = np.linspace(0, duration, num_points)
        
        # Create sinusoidal input
        omega = 2 * math.pi * frequency
        u = amplitude * np.sin(omega * t)
        
        # Get transfer function
        tf = self.get_transfer_function()
        
        # Calculate response using lsim
        t_sim, y_sim, _ = signal.lsim(tf, u, t)
        
        # Calculate current response
        current = self._calculate_current_response(t_sim, y_sim)
        
        return t_sim, y_sim, current
    
    @abstractmethod
    def _calculate_current_response(self, t, voltage):
        """Calculate current response based on voltage response"""
        pass

class SeriesRLCCircuit(RLCCircuit):
    """Series RLC Circuit Implementation"""
    
    def get_transfer_function(self):
        """
        Get transfer function for series RLC circuit
        Transfer function: H(s) = 1/(LCs² + RCs + 1)
        """
        # Coefficients for denominator polynomial: s² + (R/L)s + 1/(LC)
        denominator = [self.L * self.C, self.R * self.C, 1]
        numerator = [1]
        
        return signal.TransferFunction(numerator, denominator)
    
    def get_damping_factor(self):
        """Calculate damping factor for series RLC: ζ = R/(2√(L/C))"""
        return self.R / (2 * math.sqrt(self.L / self.C))
    
    def _calculate_current_response(self, t, voltage):
        """
        Calculate current in series RLC circuit
        For series: i = C * dv/dt
        """
        if len(voltage) < 2:
            return np.zeros_like(voltage)
        
        # Calculate derivative using finite differences
        dt = t[1] - t[0] if len(t) > 1 else 1
        current = np.gradient(voltage, dt) * self.C
        
        return current

class ParallelRLCCircuit(RLCCircuit):
    """Parallel RLC Circuit Implementation"""
    
    def get_transfer_function(self):
        """
        Get transfer function for parallel RLC circuit
        Transfer function: H(s) = RCs/(LCs² + RCs + 1)
        """
        # Coefficients for numerator: RCs
        numerator = [self.R * self.C, 0]
        # Coefficients for denominator: LCs² + RCs + 1
        denominator = [self.L * self.C, self.R * self.C, 1]
        
        return signal.TransferFunction(numerator, denominator)
    
    def get_damping_factor(self):
        """Calculate damping factor for parallel RLC: ζ = 1/(2R√(C/L))"""
        return 1 / (2 * self.R * math.sqrt(self.C / self.L))
    
    def _calculate_current_response(self, t, voltage):
        """
        Calculate current in parallel RLC circuit
        Total current is sum of currents through R, L, and C
        """
        if len(voltage) < 2:
            return np.zeros_like(voltage)
        
        dt = t[1] - t[0] if len(t) > 1 else 1
        
        # Current through resistor: i_R = V/R
        i_R = voltage / self.R
        
        # Current through capacitor: i_C = C * dV/dt
        dv_dt = np.gradient(voltage, dt)
        i_C = self.C * dv_dt
        
        # Current through inductor: i_L = (1/L) * ∫V dt
        # Approximate integral using cumulative sum
        i_L = np.cumsum(voltage) * dt / self.L
        
        # Total current
        total_current = i_R + i_C + i_L
        
        return total_current

def create_circuit(circuit_type, R, L, C):
    """
    Factory function to create RLC circuits
    
    Args:
        circuit_type (str): 'series' or 'parallel'
        R, L, C (float): Circuit parameters
        
    Returns:
        RLCCircuit: Appropriate circuit instance
    """
    if circuit_type.lower() == 'series':
        return SeriesRLCCircuit(R, L, C)
    elif circuit_type.lower() == 'parallel':
        return ParallelRLCCircuit(R, L, C)
    else:
        raise ValueError("Circuit type must be 'series' or 'parallel'")
