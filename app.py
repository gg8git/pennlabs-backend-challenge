from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

DB_FILE = "clubreview.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE}"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from models import Club, User, Tag


@app.route("/")
def main():
    return "Welcome to Penn Club Review!"

@app.route("/api")
def api():
    return jsonify({"message": "Welcome to the Penn Club Review API!."})

@app.route("/api/clubs", methods=["GET", "PUT"])
def get_all_clubs():
    if request.method == "GET":
        clubs = [{
            "id": club.id, 
            "code": club.code, 
            "name": club.name, 
            "description": club.description, 
            "tags": [tag.name for tag in club.get_tags()]
        } for club in Club.query.all()]
        return jsonify({"clubs": clubs})
    elif request.method == "PUT":
        club = request.get_json()

        required_fields = ["code", "name", "description"]
        for field in required_fields:
            if field not in club:
                abort(400, f"Missing required field: {field}")

        new_club = Club(code=club["code"],name=club["name"],description=club["description"])
        db.session.add(new_club)
        if "tags" in club:
            for tag_name in club["tags"]:
                tag = Tag.query.filter_by(name=tag_name).first()
                if tag:
                    new_club.add_tag(tag)
                else:
                    new_tag = Tag(name=tag_name)
                    new_club.add_tag(new_tag)
        
        return jsonify({"message": "Club added"})

@app.route("/api/clubs/<string:club_name>", methods=["GET", "PATCH", "DELETE"])
def get_club(club_name):
    if request.method == "GET":
        club = Club.query.filter_by(name=club_name).first()
        if club:
            return jsonify({
                "id": club.id, 
                "code": club.code, 
                "name": club.name, 
                "description": club.description, 
                "favorite_count": club.get_favorite_count(),
                "tags": [tag.name for tag in club.get_tags()]
            })
    elif request.method == "PATCH":
        new_club = request.get_json()
        club = Club.query.filter_by(name=club_name).first()
        if "code" in new_club:
            club.code = new_club["code"]
        if "name" in new_club:
            club.name = new_club["name"]
        if "description" in new_club:
            club.description = new_club["description"]
        return jsonify({"message": "Club modified"})
    elif request.method == "DELETE":
        club = Club.query.filter_by(name=club_name).first()
        if club:
            db.session.delete(club)
            return jsonify({"message": "Club deleted"})
        else:
            abort(400, "Club does not exist")

@app.route("/api/clubs/<string:club_name>/tags", methods=["GET", "PUT"])
def get_club_tags(club_name):
    if request.method == "GET":
        club = Club.query.filter_by(name=club_name).first()
        if club:
            tags = [tag.name for tag in club.get_tags()]
            return jsonify({"tags": tags})
    elif request.method == "PUT":
        tag_name = request.get_json()["name"]
        club = Club.query.filter_by(name=club_name).first()
        if tag_name:
            tag = Tag.query.filter_by(name=tag_name).first()
            if tag:
                club.add_tag(tag)
            else:
                new_tag = Tag(name=tag_name)
                club.add_tag(new_tag)
            return jsonify({"message": "Tag added to club"})

@app.route("/api/clubs/search-club/<string:search_str>", methods=["GET"])
def search_club(search_str):
    clubs = [{
        "id": club.id, 
        "code": club.code, 
        "name": club.name, 
        "description": club.description, 
        "tags": [tag.name for tag in club.get_tags()]
    } for club in Club.query.filter_by(name=f"%{search_str}%").all()]
    return jsonify({"clubs": clubs})
    
@app.route("api/users", methods=["GET", "PUT"])
def get_all_users():
    if request.method == "GET":
        users = [{
            "id": user.id, 
            "username": user.username, 
            "email": user.email, 
            "first_name": user.first_name, 
            "last_name": user.last_name,
            "favorites": [club.name for club in user.get_favorites()],
            "membership": [club.name for club in user.get_clubs()]
        } for user in User.query.all()]
        return jsonify({"users": users})
    elif request.method == "PUT":
        user = request.get_json()

        required_fields = ["username", "email", "first_name", "last_name"]
        for field in required_fields:
            if field not in user:
                abort(400, f"Missing required field: {field}")

        new_user = User(username=user["username"],email=user["email"],first_name=user["first_name"],last_name=user["last_name"])
        db.session.add(new_user)
        
        return jsonify({"message": "User added"})

@app.route("api/users/<string:username>", methods=["GET", "PATCH", "DELETE"])
def get_user(username):
    if request.method == "GET":
        user = User.query.filter_by(username=username).first()
        if user:
            return jsonify({
                "id": user.id, 
                "username": user.username, 
                "email": user.email, 
                "first_name": user.first_name, 
                "last_name": user.last_name,
                "favorites": [club.name for club in user.get_favorites()],
                "clubs": [club.name for club in user.get_clubs()]
            })
    elif request.method == "PATCH":
        new_user = request.get_json()
        user = User.query.filter_by(username=username).first()
        if "username" in new_user:
            user.username = new_user["username"]
        if "email" in new_user:
            user.email = new_user["email"]
        if "first_name" in new_user:
            user.first_name = new_user["first_name"]
        if "last_name" in new_user:
            user.last_name = new_user["last_name"]
        return jsonify({"message": "User modified"})
    elif request.method == "DELETE":
        user = User.query.filter_by(username=username).first()
        if user:
            db.session.delete(user)
            return jsonify({"message": "User deleted"})
        else:
            abort(400, "User does not exist")


@app.route("api/users/<string:username>/favorites", methods=["GET"])
def get_user_favorites(username):
    user = User.query.filter_by(username=username).first()
    if user:
        favorites = [club.name for club in user.get_favorites()]
        return jsonify({"favorites": favorites})

@app.route("api/users/<string:username>/clubs", methods=["GET"])
def get_user_clubs(username):
    user = User.query.filter_by(username=username).first()
    if user:
        clubs = [club.name for club in user.get_clubs()]
        return jsonify({"clubs": clubs})

@app.route("api/tags", methods=["GET", "PUT"])
def get_all_tags():
    if request.method == "GET":
        tags = [{
            "id": tag.id, 
            "name": tag.name, 
            "tagged_clubs_count": tag.get_tagged_clubs_count(), 
            "tagged_clubs": tag.get_tagged_clubs(), 
        } for tag in Tag.query.all()]
        return jsonify({"tags": tags})
    elif request.method == "PUT":
        tag = request.get_json()

        required_fields = ["name"]
        for field in required_fields:
            if field not in tag:
                abort(400, f"Missing required field: {field}")

        new_tag = Tag(name=tag["name"])
        db.session.add(new_tag)
        
        return jsonify({"message": "Tag added"})
    
@app.route("api/tags/<string:tag_name>", methods=["GET", "PATCH", "DELETE"])
def get_tag(tag_name):
    if request.method == "GET":
        tag = Tag.query.filter_by(name=tag_name).first()
        if tag:
            return jsonify({
                "id": tag.id, 
                "name": tag.name, 
                "tagged_clubs_count": tag.get_tagged_clubs_count(), 
                "tagged_clubs": tag.get_tagged_clubs(), 
            })
    elif request.method == "PATCH":
        new_tag = request.get_json()
        tag = Tag.query.filter_by(name=tag_name).first()
        if "name" in new_tag:
            tag.name = new_tag["name"]
        return jsonify({"message": "Tag modified"})
    elif request.method == "DELETE":
        tag = Tag.query.filter_by(name=tag_name).first()
        if tag:
            db.session.delete(tag)
            return jsonify({"message": "Tag deleted"})
        else:
            abort(400, "Tag does not exist")

if __name__ == "__main__":
    app.run()
