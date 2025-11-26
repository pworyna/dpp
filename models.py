from sqlalchemy import Column, Integer, String, Float, ForeignKey
from database import Base

class Movie(Base):
    __tablename__ = "movies"
    movieId = Column(Integer, primary_key=True)
    title = Column(String)
    genres = Column(String)

class Link(Base):
    __tablename__ = "links"
    movieId = Column(Integer, primary_key=True)
    imdbId = Column(Integer)
    tmdbId = Column(Float)

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True)
    userId = Column(Integer)
    movieId = Column(Integer, ForeignKey("movies.movieId"))
    rating = Column(Float)
    timestamp = Column(Integer)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    userId = Column(Integer)
    movieId = Column(Integer, ForeignKey("movies.movieId"))
    tag = Column(String)
    timestamp = Column(Integer)
