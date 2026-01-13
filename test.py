import pytest
from fastapi.testclient import TestClient
from main import app
from database import session
from models import Movie, Link, Rating, Tag

client = TestClient(app)

@pytest.fixture
def movie_fixture():
    movie = Movie(movieId=999900, title="Test Movie", genres="Comedy")
    session.add(movie)
    session.commit()
    yield movie
    session.delete(movie)
    session.commit()

@pytest.fixture
def link_fixture():
    link = Link(movieId=999900, imdbId=999999, tmdbId=12345.0)
    session.add(link)
    session.commit()
    yield link
    session.delete(link)
    session.commit()

@pytest.fixture
def rating_fixture():
    rating = Rating(id=999900, userId=1, movieId=999900, rating=4.5, timestamp=111111111)
    session.add(rating)
    session.commit()
    yield rating
    session.delete(rating)
    session.commit()

@pytest.fixture
def tag_fixture():
    tag = Tag(id=999900, userId=1, movieId=999900, tag="funny", timestamp=111111111)
    session.add(tag)
    session.commit()
    yield tag
    session.delete(tag)
    session.commit()

def test_movies_list_increases_after_create():
    before = client.get("/movies").json()
    count_before = len(before)
    payload = {"movieId": 999901, "title": "New Movie X", "genres": "Action"}
    r = client.post("/movies", json=payload)
    assert r.status_code == 201
    after = client.get("/movies").json()
    assert len(after) == count_before + 1
    m = session.query(Movie).filter(Movie.movieId == 999901).first()
    session.delete(m)
    session.commit()

def test_get_movie_item(movie_fixture):
    r = client.get(f"/movies/{movie_fixture.movieId}")
    assert r.status_code == 200
    data = r.json()
    assert data["movieId"] == movie_fixture.movieId
    assert data["title"] == "Test Movie"

def test_get_movie_404():
    r = client.get("/movies/1234567890")
    assert r.status_code == 404

def test_update_movie(movie_fixture):
    payload = {"movieId": movie_fixture.movieId, "title": "Updated Title", "genres": "Drama"}
    r = client.put(f"/movies/{movie_fixture.movieId}", json=payload)
    assert r.status_code == 200
    updated = session.query(Movie).filter(Movie.movieId == movie_fixture.movieId).first()
    assert updated.title == "Updated Title"

def test_delete_movie():
    m = Movie(movieId=999902, title="To Delete", genres="Horror")
    session.add(m)
    session.commit()
    r = client.delete(f"/movies/{m.movieId}")
    assert r.status_code == 204
    assert session.query(Movie).filter(Movie.movieId == m.movieId).first() is None

def test_links_list_increases_after_create():
    before = client.get("/links").json()
    cnt = len(before)
    payload = {"movieId": 999903, "imdbId": 777777, "tmdbId": 3333.0}
    r = client.post("/links", json=payload)
    assert r.status_code == 201
    after = client.get("/links").json()
    assert len(after) == cnt + 1
    # cleanup
    l = session.query(Link).filter(Link.movieId == 999903).first()
    session.delete(l)
    session.commit()

def test_get_link_item(link_fixture):
    r = client.get(f"/links/{link_fixture.movieId}")
    assert r.status_code == 200
    data = r.json()
    assert data["movieId"] == link_fixture.movieId
    assert data["imdbId"] == link_fixture.imdbId

def test_get_link_404():
    r = client.get("/links/1234567890")
    assert r.status_code == 404

def test_update_link(link_fixture):
    payload = {"movieId": link_fixture.movieId, "imdbId": 111111, "tmdbId": 2222.0}
    r = client.put(f"/links/{link_fixture.movieId}", json=payload)
    assert r.status_code == 200
    updated = session.query(Link).filter(Link.movieId == link_fixture.movieId).first()
    assert updated.imdbId == 111111

def test_delete_link():
    l = Link(movieId=999904, imdbId=888888, tmdbId=4444.0)
    session.add(l)
    session.commit()
    r = client.delete(f"/links/{l.movieId}")
    assert r.status_code == 204
    assert session.query(Link).filter(Link.movieId == l.movieId).first() is None

def test_ratings_list_increases_after_create():
    before = client.get("/ratings").json()
    cnt = len(before)
    payload = {"id": 999905, "userId": 5, "movieId": 1, "rating": 3.5, "timestamp": 222222222}
    r = client.post("/ratings", json=payload)
    assert r.status_code == 201
    after = client.get("/ratings").json()
    assert len(after) == cnt + 1
    rr = session.query(Rating).filter(Rating.id == 999905).first()
    session.delete(rr)
    session.commit()

def test_get_rating_item(rating_fixture):
    r = client.get(f"/ratings/{rating_fixture.id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == rating_fixture.id
    assert abs(data["rating"] - 4.5) < 1e-9

def test_get_rating_404():
    r = client.get("/ratings/1234567890")
    assert r.status_code == 404

def test_update_rating(rating_fixture):
    payload = {"id": rating_fixture.id, "userId": rating_fixture.userId, "movieId": rating_fixture.movieId, "rating": 1.0, "timestamp": rating_fixture.timestamp}
    r = client.put(f"/ratings/{rating_fixture.id}", json=payload)
    assert r.status_code == 200
    updated = session.query(Rating).filter(Rating.id == rating_fixture.id).first()
    assert abs(updated.rating - 1.0) < 1e-9

def test_delete_rating():
    rr = Rating(id=999906, userId=2, movieId=1, rating=2.0, timestamp=333333333)
    session.add(rr)
    session.commit()
    r = client.delete(f"/ratings/{rr.id}")
    assert r.status_code == 204
    assert session.query(Rating).filter(Rating.id == rr.id).first() is None

def test_tags_list_increases_after_create():
    before = client.get("/tags").json()
    cnt = len(before)
    payload = {"id": 999907, "userId": 6, "movieId": 1, "tag": "cool", "timestamp": 444444444}
    r = client.post("/tags", json=payload)
    assert r.status_code == 201
    after = client.get("/tags").json()
    assert len(after) == cnt + 1
    tt = session.query(Tag).filter(Tag.id == 999907).first()
    session.delete(tt)
    session.commit()

def test_get_tag_item(tag_fixture):
    r = client.get(f"/tags/{tag_fixture.id}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == tag_fixture.id
    assert data["tag"] == "funny"

def test_get_tag_404():
    r = client.get("/tags/1234567890")
    assert r.status_code == 404

def test_update_tag(tag_fixture):
    payload = {"id": tag_fixture.id, "userId": tag_fixture.userId, "movieId": tag_fixture.movieId, "tag": "serious", "timestamp": tag_fixture.timestamp}
    r = client.put(f"/tags/{tag_fixture.id}", json=payload)
    assert r.status_code == 200
    updated = session.query(Tag).filter(Tag.id == tag_fixture.id).first()
    assert updated.tag == "serious"

def test_delete_tag():
    tt = Tag(id=999908, userId=3, movieId=1, tag="tmp", timestamp=555555555)
    session.add(tt)
    session.commit()
    r = client.delete(f"/tags/{tt.id}")
    assert r.status_code == 204
    assert session.query(Tag).filter(Tag.id == tt.id).first() is None
