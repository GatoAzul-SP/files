from fastapi import FastAPI
import api_gauss_seidel
import api_montana_rusa
import api_analisis_datos

app = FastAPI(root_path="/api/v1")

app.include_router(api_conversion_bases.router)
app.include_router(api_gauss_seidel.router)
app.include_router(api_montana_rusa.router)
app.include_router(api_analisis_datos.router)
