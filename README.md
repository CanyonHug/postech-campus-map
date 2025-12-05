---

## 📍 POSTECH Campus Map

**Search, navigate, and reserve campus facilities — all in one platform**

---

### 🧩 Overview

POSTECH Campus Map is a web-based platform designed to help students explore and utilize on-campus facilities more efficiently.

With an interactive campus map powered by **Kakao Maps API**, users can:
✔ Search facilities by category or keyword
✔ View details such as location, description, and available services
✔ Navigate with real-time walking routes
✔ Make reservations (for logged-in users)

An onboarding flow introduces key features for first-time visitors.

---

### 🚀 Key Features

| Feature                     | Description                                                                       |
| --------------------------- | --------------------------------------------------------------------------------- |
| 🔍 Facility search          | Search by category (e.g., restaurants, cafe, sports, dormitory, etc.) or keywords |
| 🗺 Interactive map          | Zoom-responsive icons, clickable markers, pop-up overlays                         |
| 🧭 Walking navigation       | Real-time path guidance from current or selected location                         |
| 🏷 Facility info overlays   | Details in both Korean & English                                                  |
| 🔐 Login & Guest mode       | Guest can explore, logged-in users can reserve                                    |
| 📱 Mobile responsive design | Supports mobile browsers with adaptive UI                                         |
| 👋 Onboarding               | First-time guided tour with service introduction                                  |

---

### 🏛 Technology Stack

| Component        | Technology                                                              |
| ---------------- | ----------------------------------------------------------------------- |
| Backend & Server | **Python Flask**                                                        |
| Frontend UI      | HTML, CSS, Bootstrap, JavaScript                                        |
| Map & Navigation | **Kakao Maps JavaScript API** (+ Kakao Mobility API)                    |
| Authentication   | Basic session authentication                                            |
| Storage          | In-memory(dummy) facility & reservation data *(DB integration planned)* |

---

### 📦 Project Structure

```
project-folder/
│
├─ static/
│   ├─ images/
│   ├─ logos/
│   │   ├─ FacilityMarks/
│   │   └─ DepartmentsMark/
│
├─ templates/
│   ├─ landing.html
│   ├─ login.html
│   ├─ onboarding.html
│   └─ map.html
│
├─ postech_map.py   ← Flask main application
├─ requirements.txt
└─ README.md
```

*(Structure may evolve as DB integration and new UI updates progress.)*

---

### ⚙️ Local Development Setup

#### 1️⃣ Create virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

#### 2️⃣ Install dependencies

Currently, the requirements.txt file has not been fully prepared.

#### 3️⃣ Run the server

```bash
export FLASK_APP=postech_map.py
flask run
```

Default development URL:
👉 [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

---

### 👥 User Modes

| Mode           | Access                                    |
| -------------- | ----------------------------------------- |
| Guest          | Can explore facilities but cannot reserve |
| Logged-in user | Full access including reservations        |

Default login credentials (temporary for demo):

```
ID: postechian
PW: 1234
```

*(Will be replaced with real DB & SSO login in later versions)*

---

### 📄 License

Internal university project — not intended for commercial use.

---

## 🎯 Goal

Enhance the daily life convenience of POSTECH students
through a unified, intuitive and smart campus map solution. 🏫✨

---
