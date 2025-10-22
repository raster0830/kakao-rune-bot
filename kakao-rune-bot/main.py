from fastapi import FastAPI, Request
import httpx
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "message": "카카오봇 서버 정상 작동 중"}

@app.post("/kakao")
async def kakao_webhook(req: Request):
    data = await req.json()
    user_msg = data.get("userRequest", {}).get("utterance", "").strip()

    if user_msg.startswith("/룬"):
        query = user_msg.replace("/룬", "").strip()
        if not query:
            return {"text": "검색어를 입력해주세요. 예: /룬 룬이름"}

        # mabimobi.life에서 검색
        search_url = f"https://mabimobi.life/runes?t=search&q={query}"
        async with httpx.AsyncClient() as client:
            r = await client.get(search_url)
            soup = BeautifulSoup(r.text, "html.parser")

        # 검색 결과 추출
        results = soup.select("div.rune-card")
        if not results:
            return {"text": f"'{query}'에 대한 결과를 찾을 수 없습니다."}

        msg_list = []
        for item in results[:3]:  # 최대 3개까지만
            name = item.select_one(".rune-name").get_text(strip=True)
            desc = item.select_one(".rune-desc").get_text(strip=True)
            msg_list.append(f"🔹 {name}\n{desc}")

        reply_text = "\n\n".join(msg_list)
        return {"text": reply_text}

    return {"text": "명령어를 인식하지 못했습니다. 예: /룬 룬이름"}
