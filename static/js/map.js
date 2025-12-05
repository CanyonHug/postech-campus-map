// map.js

let map;
let markers = [];
let polylines = [];
let selectedLang = "ko";
let startPoint = null;
let endPoint = null;

function initMap() {
    const container = document.getElementById("map");
    const options = {
        center: new kakao.maps.LatLng(36.01449, 129.32154),
        level: 3,
    };
    map = new kakao.maps.Map(container, options);

    loadFacilities();

    // 현재 위치 버튼 구현(가능한 브라우저에서)
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((pos) => {
            const latlng = new kakao.maps.LatLng(pos.coords.latitude, pos.coords.longitude);
            const marker = new kakao.maps.Marker({ position: latlng });
            marker.setMap(map);
        });
    }
}

function loadFacilities() {
    const category = document.getElementById("category-select").value;
    const query = document.getElementById("search-input").value;

    const url = new URL("/api/facilities", window.location.origin);
    if (category && category !== "All") url.searchParams.set("category", category);
    if (query) url.searchParams.set("q", query);

    fetch(url.toString())
        .then((res) => res.json())
        .then((facilities) => {
            clearMarkers();
            facilities.forEach((f) => addFacilityMarker(f));
        });
}

function clearMarkers() {
    markers.forEach((m) => m.setMap(null));
    markers = [];
}

function addFacilityMarker(facility) {
    const position = new kakao.maps.LatLng(facility.lat, facility.lng);
    const marker = new kakao.maps.Marker({ position });
    marker.setMap(map);
    markers.push(marker);

    const name = selectedLang === "ko" ? facility.name_ko : facility.name_en;
    const desc = selectedLang === "ko" ? facility.desc_ko : facility.desc_en;

    const iwContent = `
        <div style="padding:8px 12px;max-width:220px;">
          <strong>${name}</strong><br/>
          <small>${desc}</small><br/>
          <button type="button" class="info-btn" data-id="${facility.id}">예약</button>
          <button type="button" class="info-btn secondary" data-nav="start" data-id="${facility.id}">출발지</button>
          <button type="button" class="info-btn secondary" data-nav="end" data-id="${facility.id}">도착지</button>
        </div>
    `;

    const infowindow = new kakao.maps.InfoWindow({ content: iwContent });

    kakao.maps.event.addListener(marker, "click", function () {
        infowindow.open(map, marker);

        // 정보창이 열릴 때 안의 버튼들에 이벤트 다시 연결
        setTimeout(() => {
            const el = infowindow.a; // infoWindow element
            if (!el) return;
            el.querySelectorAll(".info-btn").forEach((btn) => {
                btn.addEventListener("click", (e) => handleInfoWindowClick(e, facility));
            });
        }, 0);
    });
}

function handleInfoWindowClick(e, facility) {
    const target = e.currentTarget;
    const navType = target.dataset.nav;

    if (navType === "start") {
        startPoint = facility;
        drawRoute();
        return;
    }
    if (navType === "end") {
        endPoint = facility;
        drawRoute();
        return;
    }

    // 예약 버튼
    openReserveModal(facility);
}

function drawRoute() {
    // 이전 라인 제거
    polylines.forEach((p) => p.setMap(null));
    polylines = [];

    if (!startPoint || !endPoint) return;

    const linePath = [
        new kakao.maps.LatLng(startPoint.lat, startPoint.lng),
        new kakao.maps.LatLng(endPoint.lat, endPoint.lng),
    ];

    const polyline = new kakao.maps.Polyline({
        path: linePath,
        strokeWeight: 4,
        strokeColor: "#ff3366",
        strokeOpacity: 0.8,
    });
    polyline.setMap(map);
    polylines.push(polyline);

    // 화면에 둘 다 보이도록
    const bounds = new kakao.maps.LatLngBounds();
    bounds.extend(linePath[0]);
    bounds.extend(linePath[1]);
    map.setBounds(bounds);
}

function resetRoute() {
    startPoint = null;
    endPoint = null;
    polylines.forEach((p) => p.setMap(null));
    polylines = [];
}

// 예약 모달 관련
function openReserveModal(facility) {
    const config = window.CAMPUS_MAP_CONFIG || {};
    if (config.isGuest) {
        alert("로그인한 사용자만 예약할 수 있습니다.");
        return;
    }

    const backdrop = document.getElementById("reserve-modal-backdrop");
    backdrop.style.display = "flex";

    const title = document.getElementById("reserve-title");
    const desc = document.getElementById("reserve-desc");
    const hint = document.getElementById("reserve-hint");

    title.textContent = selectedLang === "ko" ? facility.name_ko : facility.name_en;
    desc.textContent = selectedLang === "ko" ? facility.desc_ko : facility.desc_en;
    hint.textContent = "";

    const confirmBtn = document.getElementById("reserve-confirm");
    confirmBtn.onclick = function () {
        const time = document.getElementById("reserve-time").value;
        const memo = document.getElementById("reserve-memo").value;

        if (!time) {
            hint.textContent = "예약 시간을 입력해주세요.";
            return;
        }

        fetch("/api/reserve", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                facility_id: facility.id,
                time_slot: time,
                memo: memo,
            }),
        })
            .then((res) => {
                if (!res.ok) return res.json().then((d) => Promise.reject(d));
                return res.json();
            })
            .then(() => {
                alert("예약이 완료되었습니다.");
                closeReserveModal();
            })
            .catch((err) => {
                alert(err.error || "예약 중 오류가 발생했습니다.");
            });
    };
}

function closeReserveModal() {
    const backdrop = document.getElementById("reserve-modal-backdrop");
    backdrop.style.display = "none";
    document.getElementById("reserve-time").value = "";
    document.getElementById("reserve-memo").value = "";
}

document.addEventListener("DOMContentLoaded", () => {
    selectedLang = (window.CAMPUS_MAP_CONFIG && window.CAMPUS_MAP_CONFIG.lang) || "ko";

    initMap();

    document.getElementById("category-select").addEventListener("change", loadFacilities);
    document.getElementById("search-btn").addEventListener("click", loadFacilities);
    document.getElementById("reset-category").addEventListener("click", () => {
        document.getElementById("category-select").value = "All";
        loadFacilities();
    });

    document.getElementById("search-input").addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            loadFacilities();
        }
    });

    document.querySelectorAll(".toggle-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".toggle-btn").forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
            selectedLang = btn.dataset.lang;
            loadFacilities(); // 이름/설명 다시 반영
        });
    });

    document.getElementById("clear-route").addEventListener("click", resetRoute);

    document.getElementById("reserve-cancel").addEventListener("click", closeReserveModal);
});
