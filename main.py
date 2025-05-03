from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from io import BytesIO

app = FastAPI()

# CORS para acesso externo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_excel(BytesIO(contents), engine='openpyxl')

    df.columns = ["Data", "Hora", "Consumo_kW", "Estado"]
    df = df.dropna(subset=["Data", "Hora", "Consumo_kW"])
    df["Datetime"] = pd.to_datetime(df["Data"].astype(str) + " " + df["Hora"].astype(str))
    df["Consumo_kW"] = pd.to_numeric(df["Consumo_kW"], errors="coerce")
    df = df.dropna(subset=["Consumo_kW"])

    df["Energia_15min_kWh"] = df["Consumo_kW"] / 4
    energia_diaria = df.groupby(df["Data"])["Energia_15min_kWh"].sum()
    energia_total = df["Energia_15min_kWh"].sum()
    media_diaria = energia_diaria.mean()
    consumo_max_dia = energia_diaria.max()
    pot_max_15min = df["Consumo_kW"].max()

    return {
        "energia_total_kWh": round(energia_total, 2),
        "media_diaria_kWh": round(media_diaria, 2),
        "consumo_maximo_dia_kWh": round(consumo_max_dia, 2),
        "potencia_maxima_kW": round(pot_max_15min, 2),
        "dias_medidos": energia_diaria.shape[0]
    }
