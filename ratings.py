from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from models import Rating
from database import session

router = APIRouter()

class RatingSchema(BaseModel):
    id: int
    userId: int
    movieId: int
    rating: float
    timestamp: int

@router.get("/ratings")
def get_ratings():
    ratings = session.query(Rating).all()
    return [{"id": r.id, "userId": r.userId, "movieId": r.movieId, "rating": r.rating, "timestamp": r.timestamp} for r in ratings]

@router.post("/ratings", status_code=201)
def create_rating(rating: RatingSchema):
    existing = session.query(Rating).filter(Rating.id == rating.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Rating with given id already exists")
    db_rating = Rating(**rating.dict())
    session.add(db_rating)
    session.commit()
    return rating

@router.get("/ratings/{rating_id}")
def get_rating(rating_id: int):
    rating = session.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    return {"id": rating.id, "userId": rating.userId, "movieId": rating.movieId, "rating": rating.rating, "timestamp": rating.timestamp}

@router.put("/ratings/{rating_id}")
def update_rating(rating_id: int, rating: RatingSchema):
    db_rating = session.query(Rating).filter(Rating.id == rating_id).first()
    if not db_rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    for key, value in rating.dict().items():
        setattr(db_rating, key, value)
    session.commit()
    return rating

@router.delete("/ratings/{rating_id}", status_code=204)
def delete_rating(rating_id: int):
    rating = session.query(Rating).filter(Rating.id == rating_id).first()
    if not rating:
        raise HTTPException(status_code=404, detail="Rating not found")
    session.delete(rating)
    session.commit()
    return {}
