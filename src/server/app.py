from fastapi import FastAPI
import os
from dotenv import load_dotenv
from server.routers.itemsRouter import router as items_router
from server.routers.stockDataRouter import router as stocks_Router

# Load environment variables
load_dotenv()

app = FastAPI()



# Include the item routes
app.include_router(items_router)
app.include_router(stocks_Router)


# Run the app (for development)
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("FASTAPI_PORT", 3000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)