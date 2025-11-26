from fastapi import FastAPI
from database import Base, engine, session
import csv
from models import Movie
import movies, links, ratings, tags


Base.metadata.create_all(engine)

def load_data():

    import csv
    from models import Movie, Link, Rating, Tag
    from database import session

    with open("movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            
            if session.query(Movie).filter(Movie.movieId == int(row["movieId"])).first():
                continue
            session.add(Movie(
                movieId=int(row["movieId"]),
                title=row["title"],
                genres=row["genres"]
            ))

    with open("links.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["movieId"] == "":
                continue
            if session.query(Link).filter(Link.movieId == int(row["movieId"])).first():
                continue
            session.add(Link(
                movieId=int(row["movieId"]),
                imdbId=int(row["imdbId"]) if row.get("imdbId") else None,
                tmdbId=float(row["tmdbId"]) if row.get("tmdbId") else None
            ))

    with open("ratings.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            
            session.add(Rating(
                userId=int(row["userId"]),
                movieId=int(row["movieId"]),
                rating=float(row["rating"]),
                timestamp=int(row["timestamp"])
            ))

    with open("tags.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            session.add(Tag(
                userId=int(row["userId"]),
                movieId=int(row["movieId"]),
                tag=row["tag"],
                timestamp=int(row["timestamp"])
            ))

    session.commit()


if session.query(Movie).first() is None:
    try:
        load_data()
    except FileNotFoundError:
      
        pass

app = FastAPI()
app.include_router(movies.router)
app.include_router(links.router)
app.include_router(ratings.router)
app.include_router(tags.router)

@app.get("/")
def root():
    return {"hello": "world"}
