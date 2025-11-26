from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from models import Movie
from database import session

router = APIRouter()

class MovieSchema(BaseModel):
    movieId: int
    title: str
    genres: str

@router.get("/movies")
def get_movies():
    movies = session.query(Movie).all()
    return [{"movieId": m.movieId, "title": m.title, "genres": m.genres} for m in movies]

@router.post("/movies", status_code=201)
def create_movie(movie: MovieSchema):
    existing = session.query(Movie).filter(Movie.movieId == movie.movieId).first()
    if existing:
        raise HTTPException(status_code=400, detail="Movie with given movieId already exists")
    db_movie = Movie(**movie.dict())
    session.add(db_movie)
    session.commit()
    return movie

@router.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    movie = session.query(Movie).filter(Movie.movieId == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"movieId": movie.movieId, "title": movie.title, "genres": movie.genres}

@router.put("/movies/{movie_id}")
def update_movie(movie_id: int, movie: MovieSchema):
    db_movie = session.query(Movie).filter(Movie.movieId == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    for key, value in movie.dict().items():
        setattr(db_movie, key, value)
    session.commit()
    return movie

@router.delete("/movies/{movie_id}", status_code=204)
def delete_movie(movie_id: int):
    movie = session.query(Movie).filter(Movie.movieId == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    session.delete(movie)
    session.commit()
    return {}
