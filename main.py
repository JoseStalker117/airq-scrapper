from fastapi import FastAPI
import fadmin

app = FastAPI(title="API MongoDB", version="1.0.0")


@app.get("/")
async def root():
    return {"message": "Estás conectado a FastAPI"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)