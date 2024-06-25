from fastapi import FastAPI, BackgroundTasks, HTTPException, Form
from fastapi.responses import PlainTextResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
from requests.exceptions import ProxyError, ConnectTimeout
from faker import Faker
import re
from concurrent.futures import ThreadPoolExecutor
import urllib.parse
import time

app = FastAPI()
fake = Faker()

class Proxy(BaseModel):
    ip: str
    port: str

class VisitRequest(BaseModel):
    url: str
    platform: str
    count: int
    delay: int
    parallel_processes: int

@app.get("/", response_class=PlainTextResponse)
def rotate_ip():
    try:
        random_ip = fake.ipv4()

        headers = {
            "X-Forwarded-For": random_ip,
            "Client-IP": random_ip,
            "X-Real-IP": random_ip
        }

        test_url = "http://pubproxy.com/api/proxy?limit=5&format=txt"
        response = requests.get(test_url, headers=headers, verify=False)
        data = response.json()

        proxies = []
        for proxy_data in data['data']:
            ip, port = proxy_data['ipPort'].split(":")
            proxy = f"{ip}:{port}"
            proxies.append(proxy)

        return "\n".join(proxies)
    except ProxyError as e:
        return PlainTextResponse(f"ProxyError: {str(e)}", status_code=500)
    except ConnectTimeout as e:
        return PlainTextResponse(f"ConnectTimeoutError: {str(e)}", status_code=500)
    except Exception as e:
        return PlainTextResponse(str(e), status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
