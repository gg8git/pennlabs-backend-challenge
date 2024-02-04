from app import db, bcrypt
from flask_login import UserMixin
from datetime import date

# Your database models should go here.
# Check out the Flask-SQLAlchemy quickstart for some good docs!
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/

tags = db.Table('tags',
    db.Column('tag_name', db.Integer, db.ForeignKey('tag.name'), primary_key=True),
    db.Column('club_name', db.Integer, db.ForeignKey('club.name'), primary_key=True)
)

members = db.Table('members',
    db.Column('user_username', db.Integer, db.ForeignKey('user.username'), primary_key=True),
    db.Column('club_name', db.Integer, db.ForeignKey('club.name'), primary_key=True)
)

# add officers

favorites = db.Table('favorites',
    db.Column('user_username', db.Integer, db.ForeignKey('user.username'), primary_key=True),
    db.Column('club_name', db.Integer, db.ForeignKey('club.name'), primary_key=True)
)
    
class Club(db.Model):
    code = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(180), primary_key=True, unique=True, nullable=False)
    description = db.Column(db.String(300), nullable=False)
    favorite_count = db.Column(db.Integer)
    tags = db.relationship('Tag', secondary=tags, lazy='dynamic',
        backref=db.backref('tagged_clubs', lazy='dynamic'))
    members = db.relationship('User', secondary=members, lazy='dynamic',
        backref=db.backref('membership_clubs', lazy='dynamic'))
    reviews = db.relationship('Review', backref='review_club', lazy=True)
    
    def __repr__(self):
        return f"Club ({self.code}, {self.name})"
    
    def get_club_code(self):
        return self.code
    
    def get_club_name(self):
        return self.name
    
    def get_club_description(self):
        return self.description
    
    def get_favorite_count(self):
        favorite_count = len(self.favorite_users.all())
        return favorite_count
    
    def get_members(self):
        return self.members
    
    def add_member(self, user):
        if user not in self.members:
            self.members.append(user)
            db.session.commit()

    def remove_member(self, user):
        if user in self.members:
            self.members.remove(user)
            db.session.commit()
    
    def get_tags(self):
        return self.tags

    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
            db.session.commit()

    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
            db.session.commit()

    def get_reviews(self):
        return self.reviews

class User(db.Model, UserMixin):
    username = db.Column(db.String(30), primary_key=True, unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    favorites = db.relationship('Club', secondary=favorites, lazy='dynamic',
        backref=db.backref('favorite_users', lazy='dynamic'))
    reviews = db.relationship('Review', backref='review_user', lazy=True)

    def __repr__(self):
        return f"User ('{self.username}', '{self.email}')"
    
    def get_username(self):
        return self.username
    
    def get_user_email(self):
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_first_name(self):
        return self.first_name
    
    def get_last_name(self):
        return self.first_name
    
    def set_password(self, new_password):
        self.password = bcrypt.generate_password_hash(new_password)

    def check_password(self, check_password):
        return bcrypt.check_password_hash(self.password, check_password)
    
    def get_favorites(self):
        return self.favorites
    
    def add_favorite(self, club):
        if club not in self.favorites:
            self.favorites.append(club)
            db.session.commit()

    def remove_favorite(self, club):
        if club in self.favorites:
            self.favorites.remove(club)
            db.session.commit()
    
    def get_clubs(self):
        return self.membership_clubs.all()
    
    def join_club(self, club):
        club.add_member(self)
    
    def leave_club(self, club):
        club.remove_member(self)

    def get_reviews(self):
        self.reviews

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    title = db.Column(db.String(150), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    user = db.Column(db.String(30), db.ForeignKey('user.username'), nullable=False)
    club = db.Column(db.String(180), db.ForeignKey('club.name'), nullable=False)

    def get_review_id(self):
        return self.id
    
    def get_review_title(self):
        return self.title
    
    def get_review_rating(self):
        return self.rating
    
    def get_review_description(self):
        if self.description:
            return self.description
        else:
            return ""
        
    def set_review_description(self, desc):
        self.description = desc
    
    def get_review_user(self):
        return self.user
    
    def get_review_club(self):
        return self.club
    
class Tag(db.Model):
    name = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)
    club_count = db.Column(db.Integer)

    def get_tag_name(self):
        return self.name

    def get_tagged_clubs_count(self):
        self.club_count = len(self.tagged_clubs.all())
        return self.club_count

    def get_tagged_clubs(self):
        return self.tagged_clubs.all()