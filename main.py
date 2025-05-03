from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd

app = FastAPI()

# Permitir CORS se quiseres usar com o Lovable ou outro front-end
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def upload_form():
    return """
    <html>
        <head>
            <title>Upload de Ficheiro E-REDES (.xlsx)</title>
        </head>
        <body>
            <h1>Upload de Ficheiro E-REDES (.xlsx)</h1>
            <form action="/upload_xlsx" enctype="multipart/form-data" method="post">
                <input name="file" type="file" accept=".xlsx">
                <input type="submit" value="Enviar">
            </form>
        </body>
    </html>
    """

@app.post("/upload_xlsx")
async def upload_xlsx(file: UploadFile = File(...)):
    try:
        # Lê o Excel diretamente com o pandas (usando openpyxl)
        df = pd.read_excel(file.file, engine='openpyxl')

        # Verifica e ajusta nomes de colunas esperadas
        expected_cols = ["Data", "Hora", "Consumo_kW"]
        df.columns = [col.strip() for col in df.columns[:len(expected_cols)]]
        df = df.rename(columns={df.columns[0]: "Data", df.columns[1]: "Hora", df.columns[2]: "Consumo_kW"})

        # Elimina linhas sem consumo
        df = df.dropna(subset=["Data", "Hora", "Consumo_kW"])

        # Converte data/hora e valores numéricos
        df["Datetime"] = pd.to_datetime(df["Data"].astype(str) + " " + df["Hora"].astype(str), errors="coerce")
        df["Consumo_kW"] = pd.to_numeric(df["Consumo_kW"], errors="coerce")
        df = df.dropna(subset=["Datetime", "Consumo_kW"])
        df["Data"] = pd.to_datetime(df["Datetime"].dt.date)
        df["Energia_15min_kWh"] = df["Consumo_kW"] / 4

        # Cálculos
        energia_diaria = df.groupby("Data")["Energia_15min_kWh"].sum()
        energia_total = df["Energia_15min_kWh"].sum()
        media_diaria = energia_diaria.mean()
        consumo_max_diario = energia_diaria.max()
        potencia_max_15min = df["Consumo_kW"].max()

        return JSONResponse({
            "energia_total_kWh": round(energia_total, 2),
            "media_diaria_kWh": round(media_diaria, 2),
            "consumo_max_diario_kWh": round(consumo_max_diario, 2),
            "potencia_max_15min_kW": round(potencia_max_15min, 2)
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})
