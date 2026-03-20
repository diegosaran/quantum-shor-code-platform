"""
========================================================
Shor Code Quantum Error Correction Demonstration
========================================================

Author: Diego Saran

ABSTRACT
--------
This script demonstrates the full workflow of the Shor
9-qubit quantum error correcting code.

The experiment performs:
1. Logical qubit encoding
2. Artificial error injection
3. Syndrome measurement
4. Error correction
5. Logical state recovery
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from typing import Dict, Tuple
import matplotlib.pyplot as plt
import io
import base64

def create_shor_circuit(error_type: str = "none", error_qubit: int = 0) -> Tuple[QuantumCircuit, int]:
    """
    Creates the Shor code circuit with optional error injection.

    Args:
        error_type: Type of error ("x", "z", "y", "none")
        error_qubit: Index of the qubit (0-8) where the error is injected

    Returns:
        The full Qiskit circuit and the number of operations
    """
    # Registers
    data = QuantumRegister(9, "data")
    anc = QuantumRegister(8, "anc")
    syn_phase = ClassicalRegister(2, "syn_phase")
    syn_bit = ClassicalRegister(6, "syn_bit")
    out = ClassicalRegister(1, "out")

    qc = QuantumCircuit(data, anc, syn_bit, syn_phase, out)

    # --- 1. INITIALIZATION (Logical state |1⟩) ---
    qc.x(data[0])

    # --- 2. SHOR ENCODING ---
    # Phase encoding across blocks
    qc.cx(data[0], data[3])
    qc.cx(data[0], data[6])
    qc.h(data[0])
    qc.h(data[3])
    qc.h(data[6])
    qc.barrier()

    # Bit encoding within blocks
    for i in [0, 3, 6]:
        qc.cx(data[i], data[i+1])
        qc.cx(data[i], data[i+2])
    qc.barrier()

    # --- 3. ERROR INJECTION ---
    if error_type != "none" and 0 <= error_qubit < 9:
        if error_type == "x":
            qc.x(data[error_qubit])
        elif error_type == "z":
            qc.z(data[error_qubit])
        elif error_type == "y":
            qc.y(data[error_qubit])
        qc.barrier()

    # --- 4. PHASE SYNDROME ---
    # Stabilizer X0 X1 X2 X3 X4 X5
    for q in [0,1,2,3,4,5]:
        qc.h(data[q])
    for q in [0,1,2,3,4,5]:
        qc.cx(data[q], anc[0])
    for q in [0,1,2,3,4,5]:
        qc.h(data[q])
    qc.barrier()

    # Stabilizer X3 X4 X5 X6 X7 X8
    for q in [3,4,5,6,7,8]:
        qc.h(data[q])
    for q in [3,4,5,6,7,8]:
        qc.cx(data[q], anc[1])
    for q in [3,4,5,6,7,8]:
        qc.h(data[q])

    qc.measure(anc[0], syn_phase[0])
    qc.measure(anc[1], syn_phase[1])
    qc.barrier()

    # --- 5. PHASE CORRECTION ---
    with qc.if_test((syn_phase[0], 1)):
        with qc.if_test((syn_phase[1], 0)):
            qc.z(data[0])  # error in block 0

    with qc.if_test((syn_phase[0], 0)):
        with qc.if_test((syn_phase[1], 1)):
            qc.z(data[6])  # error in block 2

    with qc.if_test((syn_phase[0], 1)):
        with qc.if_test((syn_phase[1], 1)):
            qc.z(data[3])  # error in block 1
    qc.barrier()

    # --- 6. BIT-FLIP SYNDROME ---
    # Block 0
    qc.cx(data[0], anc[2])
    qc.cx(data[1], anc[2])
    qc.cx(data[1], anc[3])
    qc.cx(data[2], anc[3])

    # Block 1
    qc.cx(data[3], anc[4])
    qc.cx(data[4], anc[4])
    qc.cx(data[4], anc[5])
    qc.cx(data[5], anc[5])

    # Block 2
    qc.cx(data[6], anc[6])
    qc.cx(data[7], anc[6])
    qc.cx(data[7], anc[7])
    qc.cx(data[8], anc[7])
    qc.barrier()

    # Measure bit syndromes
    qc.measure(anc[2], syn_bit[0])
    qc.measure(anc[3], syn_bit[1])
    qc.measure(anc[4], syn_bit[2])
    qc.measure(anc[5], syn_bit[3])
    qc.measure(anc[6], syn_bit[4])
    qc.measure(anc[7], syn_bit[5])
    qc.barrier()

    # --- 7. BIT-FLIP CORRECTION ---
    # Qubit 0
    with qc.if_test((syn_bit[0],1)):
        with qc.if_test((syn_bit[1],0)):
            qc.x(data[0])

    # Qubit 1
    with qc.if_test((syn_bit[0],1)):
        with qc.if_test((syn_bit[1],1)):
            qc.x(data[1])

    # Qubit 2
    with qc.if_test((syn_bit[0],0)):
        with qc.if_test((syn_bit[1],1)):
            qc.x(data[2])

    # Qubit 3
    with qc.if_test((syn_bit[2],1)):
        with qc.if_test((syn_bit[3],0)):
            qc.x(data[3])

    # Qubit 4
    with qc.if_test((syn_bit[2],1)):
        with qc.if_test((syn_bit[3],1)):
            qc.x(data[4])

    # Qubit 5
    with qc.if_test((syn_bit[2],0)):
        with qc.if_test((syn_bit[3],1)):
            qc.x(data[5])

    # Qubit 6
    with qc.if_test((syn_bit[4],1)):
        with qc.if_test((syn_bit[5],0)):
            qc.x(data[6])

    # Qubit 7
    with qc.if_test((syn_bit[4],1)):
        with qc.if_test((syn_bit[5],1)):
            qc.x(data[7])

    # Qubit 8
    with qc.if_test((syn_bit[4],0)):
        with qc.if_test((syn_bit[5],1)):
            qc.x(data[8])
    qc.barrier()

    # --- 8. DECODING ---
    # Bit decoding
    for i in [0,3,6]:
        qc.cx(data[i], data[i+1])
        qc.cx(data[i], data[i+2])

    # Phase decoding
    qc.h(data[0])
    qc.h(data[3])
    qc.h(data[6])
    qc.cx(data[0], data[3])
    qc.cx(data[0], data[6])

    # --- 9. FINAL MEASUREMENT ---
    qc.measure(data[0], out)

    return qc, qc.size()

def run_shor_simulation(error_type: str = "none", error_qubit: int = 0, shots: int = 1024) -> Dict[str, int]:
    """
    Creates and runs the Shor code circuit.

    Args:
        error_type: Type of error
        error_qubit: Qubit where the error is injected
        shots: Number of executions

    Returns:
        Dictionary with result counts
    """
    circuit, size = create_shor_circuit(error_type, error_qubit)
    
    # Configure simulator
    simulator = AerSimulator()
    
    # Run simulation
    job = simulator.run(circuit, shots=shots)
    result = job.result()
    counts = result.get_counts(circuit)
    
    return counts, size

def get_circuit_diagram(error_type: str = "none", error_qubit: int = 0) -> str:
    """
    Generates a base64 image of the circuit for frontend display.
    """
    circuit, _ = create_shor_circuit(error_type, error_qubit)
    
    # Draw circuit
    fig = circuit.draw('mpl', style='iqp', fold=-1)
    
    # Convert to base64
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    
    return img_base64