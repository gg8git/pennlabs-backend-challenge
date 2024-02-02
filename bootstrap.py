import os
import json

from app import app, db, DB_FILE

from models import User, Club, Tag

def create_user():
    user_josh = User(username="justjoshing",email="josh@upenn.edu",password="awooga",first_name="Josh",last_name="Joshua")
    db.session.add(user_josh)
    db.session.commit()

def load_data():
    script_path = os.path.abspath(__file__)
    clubs_json_path = os.path.join(os.path.dirname(script_path), 'clubs', 'clubs.json')

    if os.path.exists(clubs_json_path):
        with open(clubs_json_path, 'r') as file:
            clubs_data = json.load(file)
            for club in clubs_data:
                new_club = Club(code=club["code"],name=club["name"],description=club["description"])
                db.session.add(new_club)
                for tag_name in club["tags"]:
                    tag = Tag.query.filter_by(name=tag_name).first()
                    if tag:
                        new_club.add_tag(tag)
                    else:
                        new_tag = Tag(name=tag_name)
                        new_club.add_tag(new_tag)


# No need to modify the below code.
if __name__ == "__main__":
    # Delete any existing database before bootstrapping a new one.
    LOCAL_DB_FILE = "instance/" + DB_FILE
    if os.path.exists(LOCAL_DB_FILE):
        os.remove(LOCAL_DB_FILE)

    with app.app_context():
        db.create_all()
        create_user()
        load_data()
