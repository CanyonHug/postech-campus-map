from flask import (
    Flask, render_template, request,
    redirect, url_for, session, jsonify
)

import os, requests, json

app = Flask(__name__)
app.secret_key = "CHANGE_ME_TO_RANDOM_SECRET"  # should be changed if real service is realeased

# ==== KAKAO API setting ====
KAKAO_JS_KEY = "5d56f31f9b7f606e8d08dba91f71c3da"  # kakao developers에서 받은 JS 키
KAKAO_NAV_REST_KEY = "4a1ec0d7f44f7b800848e51bf8a2cffc"


# Dummy User 
USERS = {
    "postechian": {"password": "1234", "name": "포스테키안"},
    "friendly": {"password": "4321", "name": "friendly"},
}

# load facilities from JSON
def load_facilities():
    # Get the folder where this python file lives
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, 'facilities.json')

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: Could not find facilities.json!")
        return []  # Return an empty list so the app doesn't crash
    except json.JSONDecodeError as e:
        print(f"Error: facilities.json has a formatting mistake: {e}")
        return []

# Define the path for reservations JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESERVATIONS_FILE = os.path.join(BASE_DIR, 'reservations.json')

def load_reservations():
    """Loads reservations from the JSON file on startup."""
    if not os.path.exists(RESERVATIONS_FILE):
        return []  # Return empty list if file doesn't exist yet
    
    try:
        with open(RESERVATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        print("Warning: Could not read reservations.json, starting fresh.")
        return []

def save_reservations():
    """Saves the current RESERVATIONS list to the JSON file."""
    try:
        with open(RESERVATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(RESERVATIONS, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Error saving reservations: {e}")

# 시설 더미 데이터 (DB 대신 메모리) Facility Dummy Data (DB x, Memory O)
# ---- 시설 더미 데이터 (기존 4개 + 추가) ----
FACILITIES = load_facilities()


RESERVATIONS = []  # {user_id, facility_id, datetime, memo} 같은 구조로 저장한다고 가정
RESERVATIONS = load_reservations()


# ===== 유틸 =====
def current_user():
    if session.get("user"):
        return {"id": session["user"], "name": session.get("name"), "is_guest": False}
    if session.get("guest"):
        return {"id": None, "name": "Guest", "is_guest": True}
    return None


# ===== 라우트 =====
@app.route("/")
def landing():
    user = current_user()
    return render_template("landing.html", user=user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form.get("user_id")
        password = request.form.get("password")

        user = USERS.get(user_id)
        if user and user["password"] == password:
            session.clear()
            session["user"] = user_id
            session["name"] = user["name"]
            session["onboarded"] = False  # 새 유저면 온보딩부터
            return redirect(url_for("onboarding"))
        return render_template("login.html", error="ID 또는 비밀번호가 올바르지 않습니다.")

    return render_template("login.html")


@app.route("/guest")
def guest():
    session.clear()
    session["guest"] = True
    session["onboarded"] = False
    return redirect(url_for("onboarding"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/onboarding")
def onboarding():
    user = current_user()
    if not user:
        # 아무 세션 없으면 첫 화면으로
        return redirect(url_for("landing"))
    return render_template("onboarding.html", user=user)


@app.route("/onboarding/complete", methods=["POST"])
def onboarding_complete():
    if not current_user():
        return redirect(url_for("landing"))
    session["onboarded"] = True
    return redirect(url_for("campus_map"))


@app.route("/map")
def campus_map():
    user = current_user()
    if not user:
        return redirect(url_for("landing"))

    if not session.get("onboarded"):
        return redirect(url_for("onboarding"))

    return render_template(
        "map.html",
        user=user,
        kakao_js_key=KAKAO_JS_KEY,
    )


# ===== API (JS에서 사용) =====

@app.route("/api/facilities")
def api_facilities():
    """
    ?category=Restaurant   같이 주면 해당 카테고리만 필터링
    ?q=검색어               이름/설명 검색
    """
    category = request.args.get("category")
    query = request.args.get("q", "").lower().strip()

    results = FACILITIES
    if category and category != "All":
        results = [f for f in results if f["category"] == category]

    if query:
        results = [
            f for f in results
            if query in f["name_ko"].lower()
            or query in f["name_en"].lower()
            or query in f["desc_ko"].lower()
            or query in f["desc_en"].lower()
        ]

    return jsonify(results)


@app.route("/api/reserve", methods=["POST"])
def api_reserve():
    user = current_user()
    if not user or user["is_guest"]:
        return jsonify({"ok": False, "error": "로그인한 사용자만 예약할 수 있습니다."}), 401

    data = request.get_json()
    # ... (Keep your existing data extraction logic for facility_id, time_slot, etc.) ...
    
    facility_id = data.get("facility_id")
    time_slot = data.get("time_slot")
    duration = data.get("duration", 60)
    memo = data.get("memo", "")

    if not time_slot:
        return jsonify({"ok": False, "error": "시간을 선택해주세요."}), 400

    # ... (Keep your conflict check logic here) ...

    # [UPDATED SECTION] Append to list AND save to file
    RESERVATIONS.append({
        "user_id": user["id"],
        "facility_id": facility_id,
        "time_slot": time_slot,
        "duration": duration,
        "memo": memo,
    })
    
    save_reservations()  # <--- THIS IS THE NEW LINE TO ADD
    
    print(f"Reservation saved: {time_slot}, Duration: {duration} min")
    return jsonify({"ok": True})

@app.route("/api/my_reservations")
def api_my_reservations():
    user = current_user()
    if not user or user["is_guest"]:
        return jsonify([]) # Return empty list for guests or if not logged in

    # Filter global RESERVATIONS list for the current user ID
    # We use the 'RESERVATIONS' list that we loaded from the JSON file earlier
    my_res = [r for r in RESERVATIONS if r["user_id"] == user["id"]]
    
    # Sort by time (latest first) so the newest reservations show up top
    my_res.sort(key=lambda x: x["time_slot"], reverse=True)
    
    return jsonify(my_res)


@app.route("/api/route_walk")
def api_route_walk():
    """
    스타트/도착 좌표를 받아 Kakao Mobility 길찾기 API로 경로를 받아온 뒤
    Polyline을 그릴 수 있는 형태로 가공해 반환.
    """
    if not KAKAO_NAV_REST_KEY:
        return jsonify({"ok": False, "error": "Kakao REST 키가 서버에 설정되어 있지 않습니다."}), 500

    try:
        origin_lat = float(request.args.get("origin_lat"))
        origin_lng = float(request.args.get("origin_lng"))
        dest_lat = float(request.args.get("dest_lat"))
        dest_lng = float(request.args.get("dest_lng"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "좌표 파라미터가 잘못되었습니다."}), 400

    headers = {
        "Authorization": f"KakaoAK {KAKAO_NAV_REST_KEY}"
    }

    # Kakao Mobility Directions API (자동차 기준 경로)
    # 도보 기준 시간은 클라이언트에서 별도 계산
    url = "https://apis-navi.kakaomobility.com/v1/directions"
    params = {
        "origin": f"{origin_lng},{origin_lat}",       # lng,lat 순서
        "destination": f"{dest_lng},{dest_lat}",
        "priority": "DISTANCE",
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=5)
    except requests.RequestException:
        return jsonify({"ok": False, "error": "Kakao 길찾기 API 요청 실패"}), 502

    if not resp.ok:
        return jsonify({"ok": False, "error": f"Kakao API 오류 ({resp.status_code})"}), 502

    data = resp.json()

    try:
        route = data["routes"][0]
        summary = route["summary"]
        distance = summary["distance"]   # m
        duration = summary["duration"]   # s

        # sections -> roads -> vertexes 에서 좌표 추출
        path = []
        for section in route.get("sections", []):
            for road in section.get("roads", []):
                v = road.get("vertexes", [])
                # vertexes = [x1, y1, x2, y2, ...]  (x=lng, y=lat)
                for i in range(0, len(v), 2):
                    path.append({
                        "lng": v[i],
                        "lat": v[i + 1],
                    })
    except (KeyError, IndexError):
        return jsonify({"ok": False, "error": "유효한 경로를 찾지 못했습니다."}), 500

    if not path:
        return jsonify({"ok": False, "error": "경로 좌표가 없습니다."}), 500

    return jsonify({
        "ok": True,
        "distance": distance,
        "duration": duration,
        "path": path,
    })


if __name__ == "__main__":
    app.run(debug=True)