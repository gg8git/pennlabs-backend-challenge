from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

DB_FILE = "clubreview.db"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_FILE}"
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

from models import Club, User, Review, Tag


@app.route("/")
def main():
    return "Welcome to Penn Club Review!"

@app.route("/api")
def api():
    return jsonify({"message": "Welcome to the Penn Club Review API!."})

# POST: input username, email, password, first name, last name - registers user in site if registration is valid
@app.route("/register", methods=["POST"])
def register():
    registration = request.get_json()

    required_fields = ["username", "email", "password", "first_name", "last_name"]
    for field in required_fields:
        if field not in registration:
            abort(400, f"Missing required field: {field}")
    
    user = User(username=registration["username"],email=registration["email"],password=registration["password"],
                first_name=registration["first_name"],last_name=registration["last_name"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Registration successful"})

# POST: input username, email, password, first name, last name - registers user in site if registration is valid
@app.route("/login", methods=["POST"])
def login():
    login = request.get_json()

    required_fields = ["username/email","password"]
    for field in required_fields:
        if field not in login:
            abort(400, f"Missing required field: {field}")
    
    user = User.query.filter_by(username=login["username/email"]).first()
    if user:
        if user.check_password(login["password"]):
            return jsonify({"message": "Login successful"})
        return jsonify({"message": "Invalid password"})
    else:
        user = User.query.filter_by(email=login["username/email"]).first()
        if user:
            if user.check_password(login["password"]):
                return jsonify({"message": "Login successful"})
            return jsonify({"message": "Invalid password"})
    return jsonify({"message": "Invalid email/username"})

# GET: no input - returns json with information of all clubs
# PUT: input code, name, description, tags - adds club to database
@app.route("/api/clubs", methods=["GET", "PUT"])
def access_all_clubs():
    if request.method == "GET":
        clubs = [{
            "code": club.get_club_code(), 
            "name": club.get_club_name(), 
            "description": club.get_club_description(), 
            "favorite_count": club.get_favorite_count(),
            "tags": [tag.get_tag_name() for tag in club.get_tags()],
            "members": [member.get_full_name() for member in club.get_members()],
            "officers": [officer.get_full_name() for officer in club.get_officers()],
            "reviews": [review.get_review_id() for review in club.get_reviews()]
        } for club in Club.query.all()]
        return jsonify({"clubs": clubs})
    elif request.method == "PUT":
        club = request.get_json()

        required_fields = ["code", "name", "description"]
        for field in required_fields:
            if field not in club:
                abort(400, f"Missing required field: {field}")

        if Club.query.filter_by(code=club["code"],name=club["name"]).first():
            return jsonify({"message": "Club already exists"})
        
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

        db.session.commit()
        return jsonify({"message": "Club added"})

# GET: no input - returns json with current club information 
# PATCH: input code, name, description, tags - updates current club information
# DELETE: no input - deletes current club from database
@app.route("/api/clubs/<string:club_name>", methods=["GET", "PATCH", "DELETE"])
def access_club(club_name):
    club = Club.query.filter_by(name=club_name).first()
    if request.method == "GET":
        if club:
            return jsonify({
                "code": club.get_club_code(), 
                "name": club.get_club_name(), 
                "description": club.get_club_description(), 
                "favorite_count": club.get_favorite_count(),
                "tags": [tag.get_tag_name() for tag in club.get_tags()],
                "members": [member.get_full_name() for member in club.get_members()],
                "officers": [officer.get_full_name() for officer in club.get_officers()],
                "reviews": [review.get_review_id() for review in club.get_reviews()]
            })
    elif request.method == "PATCH":
        new_club = request.get_json()
        if "code" in new_club:
            club.code = new_club["code"]
        if "name" in new_club:
            club.name = new_club["name"]
        if "description" in new_club:
            club.description = new_club["description"]
        db.session.commit()
        return jsonify({"message": "Club modified"})
    elif request.method == "DELETE":
        if club:
            db.session.delete(club)
            db.session.commit()
            return jsonify({"message": "Club deleted"})
        else:
            abort(400, "Club does not exist")

# GET: no input - returns json with current club tags 
# PUT: input tag name - adds tag to current club tags
# DELETE: input tag name - deletes tag from current club tags
@app.route("/api/clubs/<string:club_name>/tags", methods=["GET", "PUT", "DELETE"])
def access_club_tags(club_name):
    club = Club.query.filter_by(name=club_name).first()
    if request.method == "GET":
        if club:
            tags = [tag.get_tag_name() for tag in club.get_tags()]
            return jsonify({"tags": tags})
    elif request.method == "PUT":
        tag_data = request.get_json()
        if "name" in tag_data:
            tag = Tag.query.filter_by(name=tag_data["name"]).first()
            if tag:
                club.add_tag(tag)
            else:
                new_tag = Tag(name=tag_data["name"])
                club.add_tag(new_tag)
            db.session.commit()
            return jsonify({"message": "Tag added to club"})
    elif request.method == "DELETE":
        tag_data = request.get_json()
        if "name" in tag_data:
            tag = Tag.query.filter_by(name=tag_data["name"]).first()
            if tag:
                club.remove_tag(tag)
            else:
                abort(400, "Invalid tag name")
            db.session.commit()
            return jsonify({"message": "Tag removed from club"})

# GET: no input - returns json with current club members 
# PUT: input username - adds member to current club members
# DELETE: input username - deletes member from current club members
@app.route("/api/clubs/<string:club_name>/members", methods=["GET", "PUT", "DELETE"])
def access_club_members(club_name):
    club = Club.query.filter_by(name=club_name).first()
    if request.method == "GET":
        if club:
            members = [member.get_full_name() for member in club.get_members()]
            return jsonify({"members": members})
    elif request.method == "PUT":
        member = request.get_json()
        if "username" in member:
            user = User.query.filter_by(username=member["username"]).first()
            if user:
                club.add_member(user)
            else:
                abort(400, "Invalid username")
            db.session.commit()
            return jsonify({"message": "User added to club"})
    elif request.method == "DELETE":
        member = request.get_json()
        if "username" in member:
            user = User.query.filter_by(username=member["username"]).first()
            if user:
                club.remove_member(user)
            else:
                abort(400, "Invalid username")
            db.session.commit()
            return jsonify({"message": "User removed from club"})
        
# GET: no input - returns json with current club officers 
# PUT: input officer name - adds officer to current club officers
# DELETE: input officer name - deletes officer from current club officers
@app.route("/api/clubs/<string:club_name>/members/emails", methods=["GET"])
def access_club_members_emails(club_name):
    club = Club.query.filter_by(name=club_name).first()
    if club:
        emails = [member.get_user_email() for member in club.get_members()]
        return jsonify({"emails": emails})
        
@app.route("/api/clubs/<string:club_name>/officers", methods=["GET", "PUT", "DELETE"])
def access_club_officers(club_name):
    club = Club.query.filter_by(name=club_name).first()
    if request.method == "GET":
        if club:
            officers = [officer.get_full_name() for officer in club.get_officers()]
            return jsonify({"members": officers})
    elif request.method == "PUT":
        officer = request.get_json()
        if "username" in officer:
            user = User.query.filter_by(username=officer["username"]).first()
            if user:
                club.add_officer(user)
            else:
                abort(400, "Invalid username")
            db.session.commit()
            return jsonify({"message": "User added to club officers"})
    elif request.method == "DELETE":
        officer = request.get_json()
        if "username" in officer:
            user = User.query.filter_by(username=officer["username"]).first()
            if user:
                club.remove_officer(user)
            else:
                abort(400, "Invalid username")
            db.session.commit()
            return jsonify({"message": "User removed from club officers"})

# GET: no input - returns json with current club reviews 
# PUT: input title, rating, username - adds review to current club reviews
# DELETE: input review id - deletes review from current club reviews
@app.route("/api/clubs/<string:club_name>/reviews", methods=["GET", "PUT", "DELETE"])
def access_club_reviews(club_name):
    club = Club.query.filter_by(name=club_name).first()
    if request.method == "GET":
        if club:
            reviews = [{
                "id": review.get_review_id(),
                "title": review.get_review_title(), 
                "rating": review.get_review_rating(), 
                "description": review.get_review_description(), 
                "user": review.get_review_user(), 
                "club": review.get_review_club()
            } for review in club.get_reviews()]
            return jsonify({"reviews": reviews})
    elif request.method == "PUT":
        review = request.get_json()
        required_fields = ["title", "rating", "username"]
        for field in required_fields:
            if field not in review:
                abort(400, f"Missing required field: {field}")
        user = User.query.filter_by(username=review["username"]).first()
        if not user:
            abort(400, "Invalid username")
        if review["rating"] > 10 or review["rating"] < 0:
            abort(400, "Invalid rating")
        new_review = Review(title=review["title"],rating=review["rating"],review_user=user,review_club=club)
        if "description" in required_fields:
            new_review.set_review_description(review["description"])
        db.session.add(new_review)
        db.session.commit()
        return jsonify({"message": "Review added to club"})
    elif request.method == "DELETE":
        review_data = request.get_json()
        if "id" in review:
            review = Review.query.filter_by(id=review_data["id"]).first()
            if review and (review.get_review_club() == club.get_club_name()):
                db.session.delete(review)
            else:
                abort(400, "Invalid review id")
            db.session.commit()
            return jsonify({"message": "Review removed from club"})

# GET: no input - returns json with all club information where the club name contains the given string
@app.route("/api/clubs/search-club/<string:search_str>", methods=["GET"])
def search_club(search_str):
    clubs = [{
        "code": club.get_club_code(), 
        "name": club.get_club_name(), 
        "description": club.get_club_description(), 
        "tags": [tag.get_tag_name() for tag in club.get_tags()],
        "members": [member.get_full_name() for member in club.get_members()],
        "officers": [officer.get_full_name() for officer in club.get_officers()],
        "reviews": [review.get_review_id() for review in club.get_reviews()]
    } for club in Club.query.filter(Club.name.ilike(f"%{search_str}%")).all()]
    return jsonify({"clubs": clubs})
    
@app.route("/api/users", methods=["GET", "PUT"])
def access_all_users():
    if request.method == "GET":
        users = [{
            "username": user.get_username(), 
            "email": user.get_user_email(), 
            "first_name": user.get_first_name(), 
            "last_name": user.get_last_name(),
            "favorites": [club.get_club_name() for club in user.get_favorites()],
            "membership": [club.get_club_name() for club in user.get_member_clubs()],
            "officership": [club.get_club_name() for club in user.get_officer_clubs()],
            "reviews": [review.get_review_id() for review in user.get_reviews()]
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
        
        db.session.commit()
        return jsonify({"message": "User added"})

# GET: no input - returns json with current user information 
# PATCH: input username, email, first_name, last_name - updates current user information
# DELETE: no input - deletes current user from database
@app.route("/api/users/<string:username>", methods=["GET", "PATCH", "DELETE"])
def access_user(username):
    user = User.query.filter_by(username=username).first()
    if request.method == "GET":
        if user:
            return jsonify({
                "username": user.get_username(), 
                "email": user.get_user_email(), 
                "first_name": user.get_first_name(), 
                "last_name": user.get_last_name(),
                "favorites": [club.get_club_name() for club in user.get_favorites()],
                "membership": [club.get_club_name() for club in user.get_member_clubs()],
                "officership": [club.get_club_name() for club in user.get_officer_clubs()],
                "reviews": [review.get_review_id() for review in user.get_reviews()]
            })
    elif request.method == "PATCH":
        new_user = request.get_json()
        if "username" in new_user:
            user.username = new_user["username"]
        if "email" in new_user:
            user.email = new_user["email"]
        if "first_name" in new_user:
            user.first_name = new_user["first_name"]
        if "last_name" in new_user:
            user.last_name = new_user["last_name"]
        db.session.commit()
        return jsonify({"message": "User modified"})
    elif request.method == "DELETE":
        if user:
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": "User deleted"})
        else:
            abort(400, "User does not exist")

# POST: input new password - changes password for current user
@app.route("/api/users/<string:username>/change-password", methods=["POST"])
def change_user_password(username):
    user = User.query.filter_by(username=username).first()
    new_password = request.get_json()
    user.set_password(new_password)
    if (user.check_password(new_password)):
        return jsonify({"message": "Password change successful"})
    return jsonify({"message": "Password change unsuccessful"})

# GET: no input - returns json with current user's favorite clubs 
# PUT: input club name - adds club to current user's favorite clubs
# DELETE: input club name - deletes club from current user's favorite clubs
@app.route("/api/users/<string:username>/favorites", methods=["GET", "PUT", "DELETE"])
def access_user_favorites(username):
    user = User.query.filter_by(username=username).first()
    if request.method == "GET":
        if user:
            favorites = [club.get_club_name() for club in user.get_favorites()]
            return jsonify({"favorites": favorites})
    elif request.method == "PUT":
        club_data = request.get_json()
        if "name" in club_data:
            club = Club.query.filter_by(name=club_data["name"]).first()
            if club:
                user.add_favorite(club)
            else:
                abort(400, "Invalid club name")
            db.session.commit()
            return jsonify({"message": "Club added to user favorites"})
    elif request.method == "DELETE":
        club_data = request.get_json()
        if "name" in club_data:
            club = Club.query.filter_by(name=club_data["name"]).first()
            if club:
                user.remove_favorite(club)
            else:
                abort(400, "Invalid club name")
            db.session.commit()
            return jsonify({"message": "Club removed from user favorites"})

# GET: no input - returns json with current user's membership clubs 
# PUT: input club name - adds club to current user's membership clubs
# DELETE: input club name - deletes club from current user's membership clubs
@app.route("/api/users/<string:username>/members", methods=["GET", "PUT", "DELETE"])
def access_user_member_clubs(username):
    user = User.query.filter_by(username=username).first()
    if request.method == "GET":
        if user:
            clubs = [club.get_club_name() for club in user.get_member_clubs()]
            return jsonify({"clubs": clubs})
    elif request.method == "PUT":
        club_data = request.get_json()
        if "name" in club_data:
            club = Club.query.filter_by(name=club_data["name"]).first()
            if club:
                user.join_club(club)
            else:
                abort(400, "Invalid club name")
            db.session.commit()
            return jsonify({"message": "Club added to user membership"})
    elif request.method == "DELETE":
        club_data = request.get_json()
        if "name" in club_data:
            club = Club.query.filter_by(name=club_data["name"]).first()
            if club:
                user.leave_club(club)
            else:
                abort(400, "Invalid club name")
            db.session.commit()
            return jsonify({"message": "Club removed from user membership"})
        
# GET: no input - returns json with current user's officership clubs 
# PUT: input club name - adds club to current user's officership clubs
# DELETE: input club name - deletes club from current user's officership clubs
@app.route("/api/users/<string:username>/officers", methods=["GET"])
def access_user_officer_clubs(username):
    user = User.query.filter_by(username=username).first()
    if request.method == "GET":
        if user:
            clubs = [club.get_club_name() for club in user.get_officer_clubs()]
            return jsonify({"clubs": clubs})
        
# GET: no input - returns json with current user's reviews 
# PUT: input title, rating, club name - adds review to current user's reviews
# DELETE: input review id - deletes review from current user's reviews
@app.route("/api/users/<string:username>/reviews", methods=["GET", "PUT", "DELETE"])
def access_user_reviews(username):
    user = User.query.filter_by(username=username).first()
    if request.method == "GET":
        if user:
            reviews = [{
                "id": review.get_review_id(),
                "title": review.get_review_title(), 
                "rating": review.get_review_rating(), 
                "description": review.get_review_description(), 
                "user": review.get_review_user(), 
                "club": review.get_review_club()
            } for review in user.get_reviews()]
            return jsonify({"reviews": reviews})
    elif request.method == "PUT":
        review = request.get_json()
        required_fields = ["title", "rating", "club_name"]
        for field in required_fields:
            if field not in review:
                abort(400, f"Missing required field: {field}")
        club = Club.query.filter_by(name=review["club_name"]).first()
        if not club:
            abort(400, "Invalid club name")
        if review["rating"] > 10 or review["rating"] < 0:
            abort(400, "Invalid rating")
        new_review = Review(title=review["title"],rating=review["rating"],review_user=user,review_club=club)
        if "description" in required_fields:
            new_review.set_review_description(review["description"])
        db.session.add(new_review)
        db.session.commit()
        return jsonify({"message": "Review added to user reviews"})
    elif request.method == "DELETE":
        review_data = request.get_json()
        if "id" in review:
            review = Review.query.filter_by(id=review_data["id"]).first()
            if review and (review.get_review_user() == user.get_username()):
                db.session.delete(review)
            else:
                abort(400, "Invalid review id")
            db.session.commit()
            return jsonify({"message": "Review removed from user reviews"})
        
@app.route("/api/reviews", methods=["GET", "PUT"])
def access_all_reviews():
    if request.method == "GET":
        reviews = [{
            "id": review.get_review_id(),
            "title": review.get_review_title(), 
            "rating": review.get_review_rating(), 
            "description": review.get_review_description(), 
            "user": review.get_review_user(), 
            "club": review.get_review_club()
        } for review in Review.query.all()]
        return jsonify({"reviews": reviews})
    elif request.method == "PUT":
        review = request.get_json()

        required_fields = ["title", "rating", "username", "club_name"]
        for field in required_fields:
            if field not in review:
                abort(400, f"Missing required field: {field}")

        user = User.query.filter_by(username=review["username"]).first()
        if not user:
            abort(400, "Invalid username")
        club = Club.query.filter_by(name=review["club_name"]).first()
        if not club:
            abort(400, "Invalid club name")
        if review["rating"] > 10 or review["rating"] < 0:
            abort(400, "Invalid rating")
        new_review = Review(title=review["title"],rating=review["rating"],review_user=user,review_club=club)
        if "description" in required_fields:
            new_review.set_review_description(review["description"])
        db.session.add(new_review)
        
        db.session.commit()
        return jsonify({"message": "Review added"})
    
@app.route("/api/reviews/<int:review_id>", methods=["GET", "PATCH", "DELETE"])
def access_review(review_id):
    review = Review.query.filter_by(id=review_id).first()
    if request.method == "GET":
        if review:
            return jsonify({
                "id": review.get_review_id(),
                "title": review.get_review_title(), 
                "rating": review.get_review_rating(), 
                "description": review.get_review_description(), 
                "user": review.get_review_user(), 
                "club": review.get_review_club()
            })
    elif request.method == "PATCH":
        new_review = request.get_json()
        if "title" in new_review:
            review.title = new_review["title"]
        if "rating" in new_review:
            review.rating = new_review["rating"]
        if "description" in new_review:
            review.description = new_review["description"]
        db.session.commit()
        return jsonify({"message": "Review modified"})
    elif request.method == "DELETE":
        if review:
            db.session.delete(review)
            db.session.commit()
            return jsonify({"message": "Review deleted"})
        else:
            abort(400, "Review does not exist")

@app.route("/api/tags", methods=["GET", "PUT"])
def access_all_tags():
    if request.method == "GET":
        tags = [{
            "name": tag.get_tag_name(), 
            "tagged_clubs_count": tag.get_tagged_clubs_count(), 
            "tagged_clubs": [club.get_club_name() for club in tag.get_tagged_clubs()]
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
        
        db.session.commit()
        return jsonify({"message": "Tag added"})
    
@app.route("/api/tags/<string:tag_name>", methods=["GET", "PATCH", "DELETE"])
def access_tag(tag_name):
    tag = Tag.query.filter_by(name=tag_name).first()
    if request.method == "GET":
        if tag:
            return jsonify({
                "name": tag.get_tag_name(), 
                "tagged_clubs_count": tag.get_tagged_clubs_count(), 
                "tagged_clubs": [club.get_club_name() for club in tag.get_tagged_clubs()]
            })
    elif request.method == "PATCH":
        new_tag = request.get_json()
        if "name" in new_tag:
            tag.name = new_tag["name"]
        db.session.commit()
        return jsonify({"message": "Tag modified"})
    elif request.method == "DELETE":
        if tag:
            db.session.delete(tag)
            db.session.commit()
            return jsonify({"message": "Tag deleted"})
        else:
            abort(400, "Tag does not exist")

if __name__ == "__main__":
    app.run()
