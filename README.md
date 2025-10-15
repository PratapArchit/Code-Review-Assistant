# 🧠 Code Review Assistant

An AI-powered platform that **automatically reviews your code** for best practices, performance issues, potential bugs, and modularity.  
Built with **FastAPI**, **React + Vite**, **TailwindCSS**, and integrated with the **OpenAI API**.

---

## 🚀 Overview

**Code Review Assistant** analyzes uploaded or pasted code and generates:
- ✅ Intelligent review reports with severity-based issues (Error / Warning / Info)
- 💡 Suggestions for improvements in code quality, structure, and maintainability
- 📊 Metrics like line count, complexity, and duplication
- 🧾 Persistent review history stored in SQLite

---

## 🧩 Tech Stack

| Layer | Technology |
|--------|-------------|
| **Backend** | FastAPI, SQLAlchemy, Pydantic, OpenAI API |
| **Frontend** | React, Vite, TailwindCSS |
| **Database** | SQLite |
| **Language Support** | Python, C++, Java, JavaScript, TypeScript, Go, Rust |

---

## 📂 Project Structure

```
code-review-assistant/
│
├── backend/
│   ├── main.py                # FastAPI app
│   ├── code_reviews.db        # SQLite database (auto-generated)
│   ├── .env                   # Stores OPENAI_API_KEY
│   └── requirements.txt       # Backend dependencies
│
├── code-review-frontend/
│   ├── src/
│   │   ├── App.jsx            # React UI logic
│   │   ├── main.jsx           # Entry point
│   │   ├── index.css          # Tailwind base styles
│   │   └── components/        # Optional UI subcomponents
│   ├── vite.config.js         # Proxy config to backend
│   └── package.json
│
└── README.md
```

---

## ⚙️ Backend Setup (FastAPI)

### 1️⃣ Create Virtual Environment
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # (Windows)
# or
source venv/bin/activate       # (macOS/Linux)
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Configure Environment
Create a `.env` file:
```
OPENAI_API_KEY=sk-yourkeyhere
```
> 🔑 Get your key from [OpenAI API Keys](https://platform.openai.com/account/api-keys)

### 4️⃣ Run the Backend
```bash
python main.py
```
Server runs at → [http://127.0.0.1:8000](http://127.0.0.1:8000)  
Swagger Docs → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 💻 Frontend Setup (React + Vite + Tailwind)

### 1️⃣ Install Node Modules
```bash
cd ../code-review-frontend
npm install
```

### 2️⃣ Configure Tailwind (if needed)
```js
// tailwind.config.js
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: { extend: {} },
  plugins: [],
};
```

### 3️⃣ Run Frontend
```bash
npm run dev
```

Frontend runs at → [http://localhost:5173](http://localhost:5173)

---

## 🔗 Backend-Frontend Integration

In `vite.config.js`, make sure proxy routes to backend:
```js
server: {
  port: 5173,
  proxy: {
    "/review": "http://127.0.0.1:8000",
  },
},
```

---

## 🧪 Testing the System

### ✅ Example 1 — C++ Test
```cpp
#include <iostream>
using namespace std;
int factorial(int n){return n<=1?1:n*factorial(n-1);}
int main(){
  cout << factorial(5);
  return 0;
}
```

### ✅ Example 2 — Python Test
```python
def average(nums):
    return sum(nums) / len(nums)

print(average([]))
```

Expected Review:
- ⚠️ Potential divide by zero
- 💡 Consider handling empty input
- ⚙️ Complexity = 3, Lines = 10

---

## 📊 API Endpoints

| Method | Endpoint | Description |
|---------|-----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/review` | Submit code for review |
| `POST` | `/review/upload` | Upload code file |
| `GET` | `/reviews` | Fetch all reviews |
| `GET` | `/reviews/{id}` | Fetch single review |
| `DELETE` | `/reviews/{id}` | Delete a review |

---

## 🧠 Sample Response

```json
{
  "filename": "sample.cpp",
  "language": "cpp",
  "score": 82.5,
  "issues": [
    {"severity": "warning", "line": 6, "message": "No input validation"},
    {"severity": "info", "line": 12, "message": "Avoid using namespace std"}
  ],
  "suggestions": [
    "Add input validation",
    "Use references instead of copying vectors"
  ],
  "metrics": {
    "lines": 25,
    "functions": 3,
    "complexity": 5
  },
  "summary": "Good structure but missing error handling"
}
```

---

## 🧩 Future Enhancements
- [ ] Real-time linting while typing  
- [ ] Multi-file project support  
- [ ] Syntax highlighting and inline issue markers  
- [ ] GitHub repo analysis integration  
- [ ] Export reports to JSON/PDF  

---

## 🧑‍💻 Author

**Pratap Archit**  
🎓 B.Tech CSE | VIT Vellore  
💡 AI & Web Systems Developer  
🌐 GitHub: [github.com/prataparchit](https://github.com/prataparchit)

---

### 🏁 Summary
After setup:
1. Run backend → `python main.py`
2. Run frontend → `npm run dev`
3. Visit → [http://localhost:5173](http://localhost:5173)
4. Paste code → Click **Review Code** ✅

Your **AI Code Review Assistant** is ready! 💻✨
