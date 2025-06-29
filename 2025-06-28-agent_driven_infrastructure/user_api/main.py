from fastapi import FastAPI
import httpx
import uvicorn

app = FastAPI()

RANDOM_USER_API = "https://randomuser.me/api/"


@app.get("/user_details")
async def user_details():
    async with httpx.AsyncClient() as client:
        response = await client.get(RANDOM_USER_API)
        response.raise_for_status()
        return response.json()


def main():
    print("Hello from user-api!")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
