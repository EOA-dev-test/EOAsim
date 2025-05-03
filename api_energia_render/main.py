
from fastapi import FastAPI, File, UploadFile
import pandas as pd
from io import StringIO

app = FastAPI()

@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(StringIO(contents.decode("utf-8")))
    df.columns = ["Data", "Hora", "Consumo_kW", "Estado"]
    df = df.dropna(subset=["Data", "Hora", "Consumo_kW"])
    df["Datetime"] = pd.to_datetime(df["Data"] + " " + df["Hora"])
    df["Consumo_kW"] = pd.to_numeric(df["Consumo_kW"], errors="coerce")
    df = df.dropna(subset=["Consumo_kW"])
    df["Data"] = pd.to_datetime(df["Data"])
    df["Energia_15min_kWh"] = df["Consumo_kW"] / 4
    energia_diaria = df.groupby(df["Data"].dt.date)["Energia_15min_kWh"].sum()
    energia_total = df["Energia_15min_kWh"].sum()
    media_diaria = energia_diaria.mean()
    consumo_max_diario = energia_diaria.max()
    pot_max_15min = df["Consumo_kW"].max()

    relatorio = f"""
Relatório de Diagnóstico Energético – Simulação Técnica e Financeira (dados CSV E-REDES)

Período Analisado: {df['Data'].min().date()} a {df['Data'].max().date()}

🔹 Energia total consumida: {energia_total:.2f} kWh
🔹 Média de consumo diário: {media_diaria:.2f} kWh/dia
🔹 Dia com maior consumo: {consumo_max_diario:.2f} kWh
🔹 Potência máxima registada em 15 minutos: {pot_max_15min:.2f} kW

📌 Sugestões:
- Potência contratada adequada: ≥ {pot_max_15min + 1:.1f} kVA
- Sistema solar ideal: 1,5 a 2,0 kWp
- Considerar bateria se objetivo for aumentar autoconsumo
"""
    return {"relatorio": relatorio.strip()}
