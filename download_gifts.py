# download_gifts.py — ينزل هدايا تلجرام (Lottie JSON) ويسوي gifts/gifts.json
# التشغيل: python download_gifts.py   (يسألك عن توكن البوت من BotFather)
# مكتبات خارجية ما يحتاج: urllib و gzip و json بس.
import os, json, gzip, urllib.request, urllib.parse

TOKEN = os.environ.get("BOT_TOKEN") or input("Bot token: ").strip()
API = "https://api.telegram.org/bot" + TOKEN + "/"
FILE = "https://api.telegram.org/file/bot" + TOKEN + "/"
OUT = "gifts"
os.makedirs(OUT, exist_ok=True)

def call(method, **params):
    data = urllib.parse.urlencode(params).encode()
    with urllib.request.urlopen(API + method, data) as r:
        j = json.load(r)
    if not j.get("ok"):
        raise SystemExit("API error: " + str(j))
    return j["result"]

def fetch(path):
    with urllib.request.urlopen(FILE + path) as r:
        return r.read()

gifts = call("getAvailableGifts")["gifts"]
print("Found", len(gifts), "gifts")
manifest = []
for g in gifts:
    st = g["sticker"]
    gid = str(g["id"])
    try:
        info = call("getFile", file_id=st["file_id"])
        raw = fetch(info["file_path"])
        if st.get("is_animated"):            # TGS = gzip(Lottie JSON)
            name = gid + ".json"
            open(os.path.join(OUT, name), "wb").write(gzip.decompress(raw))
            kind = "lottie"
        else:                                # webp / webm ثابت
            ext = os.path.splitext(info["file_path"])[1] or ".webp"
            name = gid + ext
            open(os.path.join(OUT, name), "wb").write(raw)
            kind = "image"
        manifest.append({"id": gid, "file": name, "type": kind,
                         "emoji": st.get("emoji", ""), "stars": g.get("star_count")})
        print("OK ", name)
    except Exception as e:
        print("FAIL", gid, e)

json.dump(manifest, open(os.path.join(OUT, "gifts.json"), "w"), ensure_ascii=False, indent=1)
print("Done ->", OUT + "/  (ارفع المجلد كله لـ GitHub)")
