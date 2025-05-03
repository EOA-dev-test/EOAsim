from fastapi import FastAPI, File, UploadFile
import pandas as pd
from io import BytesIO

app = FastAPI()

@app.post("/upload_xlsx")
async def upload_xlsx(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))

        # Aqui deves adaptar conforme o formato real da folha
        df.columns = [col.strip() for col in df.columns]

        if "Data" in df.columns and "Hora" in df.columns and "Consumo_kW" in df.columns:
            df["Datetime"] = pd.to_datetime(df["Data"].astype(str) + " " + df["Hora"].astype(str))
            df["Consumo_kW"] = pd.to_numeric(df["Consumo_kW"], errors="coerce")
            df = df.dropna(subset=["Consumo_kW"])

            df["Energia_15min_kWh"] = df["Consumo_kW"] / 4
            energia_total = df["Energia_15min_kWh"].sum()
            media_diaria = df.groupby(df["Datetime"].dt.date)["Energia_15min_kWh"].sum().mean()
            consumo_max_dia = df.groupby(df["Datetime"].dt.date)["Energia_15min_kWh"].sum().max()
            pot_max_15min = df["Consumo_kW"].max()

            return {
                "energia_total_kWh": round(energia_total, 2),
                "media_diaria_kWh": round(media_diaria, 2),
                "consumo_max_dia_kWh": round(consumo_max_dia, 2),
                "pot_max_15min_kW": round(pot_max_15min, 2)
            }
        else:
            return {"erro": "Colunas esperadas não encontradas no ficheiro."}
    except Exception as e:
        return {"erro": str(e)}
