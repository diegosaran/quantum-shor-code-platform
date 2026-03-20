from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import SimulationRequest, SimulationResponse
from app.circuits.shor_code import run_shor_simulation, get_circuit_diagram

router = APIRouter(prefix="/quantum", tags=["quantum"])

@router.get("/health")
async def health_check():
    return {"status": "Quantum backend is operational"}

@router.post("/simulate", response_model=SimulationResponse)
async def simulate_shor_code(request: SimulationRequest):
    try:
        counts, circuit_size = run_shor_simulation(
            error_type=request.error.type,
            error_qubit=request.error.qubit,
            shots=request.shots
        )

        logical_counts = {}
        for key, value in counts.items():
            logical_state = key[0]
            logical_counts[logical_state] = logical_counts.get(logical_state, 0) + value

        logical_outcome = max(logical_counts, key=logical_counts.get)

        return SimulationResponse(
            counts=counts,
            logical_state=logical_outcome,
            circuit_size=circuit_size,
            message="Simulation completed successfully."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")

@router.get("/circuit")
async def get_circuit(
    error_type: str = Query("none", regex="^(none|x|z|y)$"),
    error_qubit: int = Query(0, ge=0, le=8)
):
    """
    Returns a base64 image of the circuit.
    """
    try:
        img_base64 = get_circuit_diagram(error_type, error_qubit)
        return {"circuit_image": img_base64}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating circuit: {str(e)}")