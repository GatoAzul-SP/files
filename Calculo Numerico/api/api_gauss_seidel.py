import numpy as np
from gauss_seidel import GaussSeidel

from pydantic import BaseModel
from fastapi import APIRouter, HTTPException

class SistemaEC(BaseModel):
    coeficientes: list[list[float]]
    terms_indep: list[float]

router = APIRouter(prefix="/gauss-seidel")

@router.post("/")
def gauss_seidel(sistema: SistemaEC):
    sistema = sistema.dict()
    try:
        coeficientes = np.array(sistema["coeficientes"])
        terms_indep = np.array(sistema["terms_indep"])
        resolvedor = GaussSeidel(coeficientes, terms_indep)
        solucion = resolvedor.resolver().ravel().tolist()
    except (ValueError, TypeError) as e:
        raise HTTPException(422, detail=[{"msg": e.args[0]}])

    return {"solucion": solucion}
