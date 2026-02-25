from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pydantic import BaseModel
from .data_service import get_data_service
from .groq_service import get_groq_service
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import hashlib
import sys

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Zomato Bangalore AI Recommender")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache
recommendation_cache = {}

class RecommendationRequest(BaseModel):
    location: str # Required
    price_range: str # Required
    cuisines: Optional[List[str]] = None # Optional Multi-select
    min_rating: Optional[float] = None # Optional
    limit: int = 15

@app.on_event("startup")
async def startup_event():
    try:
        get_data_service()
        get_groq_service()
        print("Backend Engine Started.", flush=True)
    except Exception as e:
        print(f"Startup error: {e}", file=sys.stderr, flush=True)

@app.get("/")
async def root():
    return {"status": "operational"}

@app.get("/api/locations")
async def get_locations():
    return get_data_service().get_unique_locations()

@app.get("/api/cuisines")
async def get_cuisines():
    return get_data_service().get_unique_cuisines()

@app.post("/api/recommend")
@limiter.limit("5/minute")
async def recommend(recommend_req: RecommendationRequest, request: Request):
    data_svc = get_data_service()
    groq_svc = get_groq_service()
    
    # Cache Check
    cache_key = hashlib.md5(recommend_req.model_dump_json().encode()).hexdigest()
    if cache_key in recommendation_cache:
        return recommendation_cache[cache_key]
    
    # 1. Get unique candidates from data layer
    try:
        candidates = data_svc.filter_restaurants(
            location=recommend_req.location,
            selected_cuisines=recommend_req.cuisines,
            min_rating=recommend_req.min_rating,
            price_range=recommend_req.price_range,
            limit=recommend_req.limit
        )
    except Exception as e:
        print(f"Filtering error: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail="Search failed at data layer.")
    
    if not candidates:
        return {"recommendations": [], "summary": "No unique matches found in our Bangalore records."}
    
    # 2. Expert AI Reasoning
    preferences = {
        "location": recommend_req.location,
        "cuisines": recommend_req.cuisines,
        "min_rating": recommend_req.min_rating,
        "price_range": recommend_req.price_range
    }
    
    try:
        ai_recommendations = groq_svc.get_recommendations(preferences, candidates)
        if "error" not in ai_recommendations:
            recommendation_cache[cache_key] = ai_recommendations
        return ai_recommendations
    except Exception as e:
        # Structured Fallback
        return {
            "recommendations": [
                {
                    "name": c['name'], 
                    "full_address": c['address'], 
                    "rating": c['rate'], 
                    "price_for_two": c['approx_cost(for two people)'],
                    "recommendation_reason": "A highly rated restaurant from our database matching your area and price range."
                } 
                for c in candidates[:5]
            ],
            "summary": "AI logic encountered an error, but here are the top 5 direct matches from our records.",
            "is_fallback": True
        }
