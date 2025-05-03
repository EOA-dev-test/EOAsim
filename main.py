from fastapi import FastAPI, File, UploadFile
import pandas as pd
from io import BytesIO

app = FastAPI()

@app.post("/upload_xlsx")
async def upload_xlsx(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_excel(BytesIO(contents))
    
    df.columns = ["Data", "Hora", "Consumo_kW", "Estado"]
    df = df.dropna(subset=["Data", "Hora", "Consumo_kW"])
    df["Datetime"] = pd.to_datetime(df["Data"].astype(str) + " " + df["Hora"].astype(str))
    df["Consumo_kW"] = pd.to_numeric(df["Consumo_kW"], errors="coerce")
    df = df.dropna(subset=["Consumo_kW"])
    df["Data"] = pd.to_datetime(df["Data"])
    df["Energia_15min_kWh"] = df["Consumo_kW"] / 4
    
    energia_diaria = df.groupby(df["Data"].dt.date)["Energia_15min_kWh"].sum()
    energia_total = df["Energia_15min_kWh"].sum()
    media_diaria = energia_diaria.mean()
    consumo_max_dia = energia_diaria.max()
    pot_max_15min = df["Consumo_kW"].max()

    return {
        "energia_total_kWh": round(energia_total, 2),
        "media_diaria_kWh": round(media_diaria, 2),
        "consumo_maximo_diario_kWh": round(consumo_max_dia, 2),
        "potencia_maxima_kW_15min": round(pot_max_15min, 2)
    }
