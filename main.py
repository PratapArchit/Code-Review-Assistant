"""
Code Review Assistant - FastAPI backend with OpenAI integration (2025-compatible)
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from enum import Enum
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from colorama import Fore, Style  
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key:
    print(f"{Fore.GREEN}✅ OPENAI_API_KEY loaded successfully!{Style.RESET_ALL}")
else:
    print(f"{Fore.YELLOW}⚠️  No OPENAI_API_KEY found. Using static fallback mode.{Style.RESET_ALL}")

SQLALCHEMY_DATABASE_URL = "sqlite:///./code_reviews.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ReviewReport(Base):
    __tablename__ = "review_reports"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    language = Column(String)
    code_content = Column(Text)
    score = Column(Float)
    issues = Column(JSON)
    suggestions = Column(JSON)
    metrics = Column(JSON)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    user_id = Column(String, nullable=True)


Base.metadata.create_all(bind=engine)

class SeverityEnum(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Issue(BaseModel):
    severity: SeverityEnum
    line: int
    message: str
    category: str
    code_snippet: Optional[str] = None


class CodeMetrics(BaseModel):
    lines: int
    functions: int
    classes: int
    complexity: int
    duplicates: int
    test_coverage: Optional[float] = None


class ReviewResponse(BaseModel):
    id: int
    filename: str
    language: str
    score: float
    issues: List[Issue]
    suggestions: List[str]
    metrics: CodeMetrics
    timestamp: datetime
    summary: str


class CodeSubmission(BaseModel):
    code: str
    language: str
    filename: Optional[str] = "code_snippet"

app = FastAPI(title="Code Review Assistant API", version="1.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CodeReviewLLM:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("⚠️  No OPENAI_API_KEY found. Using static fallback mode.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)

    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Main analysis function."""
        if not self.client:
            return self._fallback_analysis(code, language)

        prompt = self._build_prompt(code, language)
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert code reviewer who provides structured JSON feedback."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1800,
            )
            result = response.choices[0].message.content
            return self._parse_llm_response(result)
        except Exception as e:
            print(f"❌ LLM API Error: {e}")
            return self._fallback_analysis(code, language)

    def _build_prompt(self, code: str, language: str) -> str:
        return f"""Review this {language} code for:
1. Code quality and readability
2. Modularity and structure
3. Potential bugs and security issues
4. Best practices adherence
5. Performance considerations

Provide your analysis strictly in this JSON format:
{{
  "score": <0-100>,
  "issues": [
    {{"severity": "error|warning|info", "line": <int>, "message": "<text>", "category": "<category_name>"}}
  ],
  "suggestions": ["<tip1>", "<tip2>", ...],
  "summary": "<brief_summary>",
  "metrics": {{"complexity": <1-10>, "maintainability": <1-10>}}
}}

Code:
```{language}
{code}
```"""

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            json_str = response[start:end]
            return json.loads(json_str)
        except Exception:
            print("⚠️  LLM returned malformed JSON — using fallback.")
            return self._fallback_analysis("", "unknown")

    def _fallback_analysis(self, code: str, language: str) -> Dict[str, Any]:
        lines = code.split("\n")
        issues = []
        for i, line in enumerate(lines, 1):
            if "TODO" in line:
                issues.append({
                    "severity": "info",
                    "line": i,
                    "message": "Pending TODO found",
                    "category": "Comments"
                })
            if "print(" in line and language == "python":
                issues.append({
                    "severity": "warning",
                    "line": i,
                    "message": "Debug print found",
                    "category": "Code Quality"
                })

        return {
            "score": 70,
            "issues": issues,
            "suggestions": [
                "Add error handling",
                "Remove debug prints",
                "Follow naming conventions",
                "Write unit tests for main functions"
            ],
            "summary": "Static fallback review completed.",
            "metrics": {"complexity": 5, "maintainability": 7}
        }


llm_reviewer = CodeReviewLLM()

def calculate_metrics(code: str, language: str) -> CodeMetrics:
    lines = code.split("\n")
    function_patterns = {
        "python": ["def "],
        "javascript": ["function ", "=>"],
        "java": ["public ", "void "],
        "cpp": ["int ", "void ", "class "]
    }
    fn_count = sum(code.count(p) for p in function_patterns.get(language, []))
    cls_count = code.count("class ")
    complexity_keywords = ["if", "for", "while", "case", "catch", "&&", "||"]
    complexity = sum(code.count(k) for k in complexity_keywords)
    complexity_score = min(10, complexity // 3)
    duplicates = len(lines) - len(set(lines))
    return CodeMetrics(
        lines=len(lines),
        functions=fn_count,
        classes=cls_count,
        complexity=complexity_score,
        duplicates=duplicates
    )

@app.get("/")
async def root():
    return {"message": "Code Review Assistant API (2025-ready)", "version": "1.0.1"}

@app.post("/review", response_model=ReviewResponse)
async def review_code(submission: CodeSubmission, db: Session = Depends(get_db)):
    """Submit code for review"""
    llm_result = llm_reviewer.analyze_code(submission.code, submission.language)
    metrics = calculate_metrics(submission.code, submission.language)
    if "metrics" in llm_result:
        metrics.complexity = llm_result["metrics"].get("complexity", metrics.complexity)

    db_review = ReviewReport(
        filename=submission.filename,
        language=submission.language,
        code_content=submission.code,
        score=llm_result.get("score", 75),
        issues=llm_result.get("issues", []),
        suggestions=llm_result.get("suggestions", []),
        metrics=metrics.model_dump(),
        timestamp=datetime.now(timezone.utc)
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    return ReviewResponse(
        id=db_review.id,
        filename=db_review.filename,
        language=db_review.language,
        score=db_review.score,
        issues=[Issue(**i) for i in db_review.issues],
        suggestions=db_review.suggestions,
        metrics=CodeMetrics(**db_review.metrics),
        timestamp=db_review.timestamp,
        summary=llm_result.get("summary", "Code review completed")
    )

@app.post("/review/upload", response_model=ReviewResponse)
async def review_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload file for review"""
    code = await file.read()
    code_str = code.decode("utf-8")
    ext = file.filename.split(".")[-1]
    lang_map = {
        "js": "javascript", "jsx": "javascript",
        "ts": "typescript", "tsx": "typescript",
        "py": "python", "java": "java",
        "cpp": "cpp", "cc": "cpp",
        "go": "go", "rs": "rust"
    }
    language = lang_map.get(ext, "unknown")
    submission = CodeSubmission(code=code_str, language=language, filename=file.filename)
    return await review_code(submission, db)

@app.get("/reviews", response_model=List[ReviewResponse])
async def get_reviews(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get list of recent reviews"""
    reviews = db.query(ReviewReport).order_by(ReviewReport.timestamp.desc()).offset(skip).limit(limit).all()
    return [
        ReviewResponse(
            id=r.id,
            filename=r.filename,
            language=r.language,
            score=r.score,
            issues=[Issue(**i) for i in r.issues],
            suggestions=r.suggestions,
            metrics=CodeMetrics(**r.metrics),
            timestamp=r.timestamp,
            summary=f"Review of {r.filename}"
        )
        for r in reviews
    ]

@app.get("/reviews/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: int, db: Session = Depends(get_db)):
    """Fetch a review by ID"""
    review = db.query(ReviewReport).filter(ReviewReport.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ReviewResponse(
        id=review.id,
        filename=review.filename,
        language=review.language,
        score=review.score,
        issues=[Issue(**i) for i in review.issues],
        suggestions=review.suggestions,
        metrics=CodeMetrics(**review.metrics),
        timestamp=review.timestamp,
        summary=f"Review of {review.filename}"
    )

@app.delete("/reviews/{review_id}")
async def delete_review(review_id: int, db: Session = Depends(get_db)):
    """Delete a review"""
    review = db.query(ReviewReport).filter(ReviewReport.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
