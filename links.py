from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from models import Link
from database import session

router = APIRouter()

class LinkSchema(BaseModel):
    movieId: int
    imdbId: Optional[int] = None
    tmdbId: Optional[float] = None

@router.get("/links")
def get_links():
    links = session.query(Link).all()
    return [{"movieId": l.movieId, "imdbId": l.imdbId, "tmdbId": l.tmdbId} for l in links]

@router.post("/links", status_code=201)
def create_link(link: LinkSchema):
    existing = session.query(Link).filter(Link.movieId == link.movieId).first()
    if existing:
        raise HTTPException(status_code=400, detail="Link for given movieId already exists")
    db_link = Link(**link.dict())
    session.add(db_link)
    session.commit()
    return link

@router.get("/links/{movie_id}")
def get_link(movie_id: int):
    link = session.query(Link).filter(Link.movieId == movie_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return {"movieId": link.movieId, "imdbId": link.imdbId, "tmdbId": link.tmdbId}

@router.put("/links/{movie_id}")
def update_link(movie_id: int, link: LinkSchema):
    db_link = session.query(Link).filter(Link.movieId == movie_id).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")
    for key, value in link.dict().items():
        setattr(db_link, key, value)
    session.commit()
    return link

@router.delete("/links/{movie_id}", status_code=204)
def delete_link(movie_id: int):
    link = session.query(Link).filter(Link.movieId == movie_id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    session.delete(link)
    session.commit()
    return {}
