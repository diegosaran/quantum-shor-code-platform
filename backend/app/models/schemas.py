from pydantic import BaseModel
from typing import Optional, Dict

class ErrorConfig(BaseModel):
    """Configuration of the error to be injected."""
    type: str  # "x", "z", "y", "none"
    qubit: Optional[int] = 0

class SimulationRequest(BaseModel):
    """POST request body for /simulate."""
    error: ErrorConfig
    shots: int = 1024

class SimulationResponse(BaseModel):
    """API response body."""
    counts: Dict[str, int]
    logical_state: str
    circuit_size: int
    message: str