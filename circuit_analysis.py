"""
Circuit Analysis Utilities
Provides additional analysis functions for RLC circuits
"""

import numpy as np
import math

class CircuitAnalyzer:
    """Utility class for analyzing RLC circuit characteristics"""
    
    @staticmethod
    def calculate_resonance_frequency(L, C):
        """
        Calculate resonance frequency
        
        Args:
            L (float): Inductance in Henries
            C (float): Capacitance in Farads
            
        Returns:
            tuple: (omega_0 in rad/s, f_0 in Hz)
        """
        omega_0 = 1 / math.sqrt(L * C)
        f_0 = omega_0 / (2 * math.pi)
        return omega_0, f_0
    
    @staticmethod
    def calculate_time_constants(circuit):
        """
        Calculate important time constants for the circuit
        
        Args:
            circuit (RLCCircuit): Circuit instance
            
        Returns:
            dict: Dictionary with time constants and settling times
        """
        zeta = circuit.get_damping_factor()
        omega_0 = circuit.omega_0
        
        results = {
            'natural_frequency_rad': omega_0,
            'natural_frequency_hz': circuit.f_0,
            'damping_factor': zeta,
            'q_factor': circuit.get_q_factor(),
            'damping_type': circuit.get_damping_type()
        }
        
        if zeta < 1:  # Underdamped
            omega_d = omega_0 * math.sqrt(1 - zeta**2)
            results['damped_frequency_rad'] = omega_d
            results['damped_frequency_hz'] = omega_d / (2 * math.pi)
            results['envelope_time_constant'] = 1 / (zeta * omega_0)
            results['period_damped'] = 2 * math.pi / omega_d
            
        elif zeta > 1:  # Overdamped
            s1 = -omega_0 * (zeta + math.sqrt(zeta**2 - 1))
            s2 = -omega_0 * (zeta - math.sqrt(zeta**2 - 1))
            results['pole_1'] = s1
            results['pole_2'] = s2
            results['time_constant_1'] = -1 / s1
            results['time_constant_2'] = -1 / s2
            
        else:  # Critically damped
            results['repeated_pole'] = -omega_0
            results['time_constant'] = 1 / omega_0
        
        # Settling time (2% criterion)
        if zeta > 0:
            results['settling_time_2_percent'] = 4 / (zeta * omega_0)
            results['settling_time_5_percent'] = 3 / (zeta * omega_0)
        
        return results
    
    @staticmethod
    def analyze_frequency_response(circuit, frequencies):
        """
        Analyze frequency response of the circuit
        
        Args:
            circuit (RLCCircuit): Circuit instance
            frequencies (array): Frequency points in Hz
            
        Returns:
            dict: Magnitude and phase response data
        """
        tf = circuit.get_transfer_function()
        
        # Convert frequencies to rad/s
        omega = 2 * np.pi * np.array(frequencies)
        
        # Calculate frequency response
        w, h = tf.freqresp(omega)
        
        # Calculate magnitude in dB and phase in degrees
        magnitude_db = 20 * np.log10(np.abs(h))
        phase_deg = np.angle(h) * 180 / np.pi
        
        return {
            'frequencies_hz': frequencies,
            'frequencies_rad': omega,
            'magnitude_db': magnitude_db,
            'magnitude_linear': np.abs(h),
            'phase_deg': phase_deg,
            'phase_rad': np.angle(h)
        }
    
    @staticmethod
    def find_bandwidth(circuit, tolerance_db=-3):
        """
        Find the bandwidth of the circuit
        
        Args:
            circuit (RLCCircuit): Circuit instance
            tolerance_db (float): Tolerance for bandwidth calculation (default -3dB)
            
        Returns:
            dict: Bandwidth analysis results
        """
        # Create frequency range around resonance
        f_0 = circuit.f_0
        f_min = f_0 / 100
        f_max = f_0 * 100
        frequencies = np.logspace(np.log10(f_min), np.log10(f_max), 10000)
        
        # Get frequency response
        freq_response = CircuitAnalyzer.analyze_frequency_response(circuit, frequencies)
        
        # Find peak magnitude
        peak_magnitude_db = np.max(freq_response['magnitude_db'])
        target_magnitude_db = peak_magnitude_db + tolerance_db
        
        # Find frequencies where magnitude crosses target
        magnitude_db = freq_response['magnitude_db']
        crossing_indices = np.where(np.diff(np.signbit(magnitude_db - target_magnitude_db)))[0]
        
        bandwidth_data = {
            'peak_frequency_hz': frequencies[np.argmax(magnitude_db)],
            'peak_magnitude_db': peak_magnitude_db,
            'target_magnitude_db': target_magnitude_db
        }
        
        if len(crossing_indices) >= 2:
            f_lower = frequencies[crossing_indices[0]]
            f_upper = frequencies[crossing_indices[-1]]
            bandwidth_data.update({
                'lower_frequency_hz': f_lower,
                'upper_frequency_hz': f_upper,
                'bandwidth_hz': f_upper - f_lower,
                'q_factor_measured': bandwidth_data['peak_frequency_hz'] / (f_upper - f_lower)
            })
        
        return bandwidth_data
    
    @staticmethod
    def get_educational_insights(circuit):
        """
        Generate educational insights about the circuit behavior
        
        Args:
            circuit (RLCCircuit): Circuit instance
            
        Returns:
            list: List of educational insight strings
        """
        insights = []
        
        analysis = CircuitAnalyzer.calculate_time_constants(circuit)
        zeta = analysis['damping_factor']
        q_factor = analysis['q_factor']
        
        # Basic circuit information
        insights.append(f"Circuit Type: {type(circuit).__name__.replace('RLCCircuit', ' RLC Circuit')}")
        insights.append(f"Natural Frequency: {analysis['natural_frequency_hz']:.3f} Hz ({analysis['natural_frequency_rad']:.3f} rad/s)")
        insights.append(f"Damping Factor (ζ): {zeta:.4f}")
        insights.append(f"Quality Factor (Q): {q_factor:.3f}")
        insights.append(f"Damping Type: {analysis['damping_type']}")
        
        # Damping-specific insights
        if zeta < 1:
            insights.append("⚡ Underdamped: Circuit oscillates with decreasing amplitude")
            insights.append(f"   Damped Frequency: {analysis['damped_frequency_hz']:.3f} Hz")
            insights.append(f"   Oscillation Period: {analysis['period_damped']:.4f} seconds")
            insights.append(f"   Envelope Time Constant: {analysis['envelope_time_constant']:.4f} seconds")
            
            if q_factor > 10:
                insights.append("📈 High Q Factor: Sharp resonance, low energy loss")
            elif q_factor < 0.5:
                insights.append("📉 Low Q Factor: Broad resonance, high energy loss")
                
        elif zeta > 1:
            insights.append("🔄 Overdamped: No oscillation, slow return to equilibrium")
            insights.append(f"   Fast Time Constant: {analysis['time_constant_1']:.4f} seconds")
            insights.append(f"   Slow Time Constant: {analysis['time_constant_2']:.4f} seconds")
            insights.append("   Response is the sum of two exponential decays")
            
        else:
            insights.append("⚖️ Critically Damped: Fastest approach to equilibrium without overshoot")
            insights.append(f"   Time Constant: {analysis['time_constant']:.4f} seconds")
            insights.append("   Optimal balance between speed and stability")
        
        # Settling time information
        if 'settling_time_2_percent' in analysis:
            insights.append(f"⏱️ Settling Time (2%): {analysis['settling_time_2_percent']:.4f} seconds")
            insights.append(f"⏱️ Settling Time (5%): {analysis['settling_time_5_percent']:.4f} seconds")
        
        # Energy considerations
        from circuit_simulator import SeriesRLCCircuit
        if isinstance(circuit, SeriesRLCCircuit):
            insights.append("🔌 Series Configuration: Same current through all components")
            insights.append("   Voltage divides across R, L, and C")
            insights.append("   At resonance: X_L = X_C, minimum impedance")
        else:
            insights.append("🔗 Parallel Configuration: Same voltage across all components")
            insights.append("   Current divides through R, L, and C branches")
            insights.append("   At resonance: X_L = X_C, maximum impedance")
        
        return insights
