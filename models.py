from app import db, bcrypt
from flask_login import UserMixin
from datetime import date

# Your database models should go here.
# Check out the Flask-SQLAlchemy quickstart for some good docs!
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/

tags = db.Table('tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True)
)

members = db.Table('members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True),
    db.Column('role', db.Integer, nullable=False),
    db.Column('join_date', db.Date, nullable=False),
)

favorites = db.Table('favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('club_id', db.Integer, db.ForeignKey('club.id'), primary_key=True)
)

ROLE_MEMBER = 0
ROLE_OFFICER = 1
ROLE_FOUNDER = 2

ROLE_NAMES = {
    ROLE_MEMBER: 'Member',
    ROLE_OFFICER: 'Officer',
    ROLE_FOUNDER: 'Founder',
}
    
class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(30), unique=True, nullable=False)
    name = db.Column(db.String(180), unique=True, nullable=False)
    description = db.Column(db.String(300), unique=True, nullable=False)
    favorite_count = db.Column(db.Integer)
    tags = db.relationship('Tag', secondary=tags, lazy='subquery',
        backref=db.backref('tagged_clubs', lazy=True))
    members = db.relationship('User', secondary=members, lazy='subquery',
        backref=db.backref('membership_clubs', lazy=True))
    
    def __repr__(self):
        return f"Club ({self.code}, {self.name})"
    
    def get_club_name(self):
        return self.name
    
    def get_club_description(self):
        return self.description
    
    def get_favorite_count(self):
        favorite_count = len(self.favorite_users.all())
        return favorite_count
    
    def get_members(self):
        return self.members
    
    def add_member(self, user, role):
        if user not in self.members and role in ROLE_NAMES.keys:
            self.members.append(user)
            db.session.execute(members.insert().values(user_id=user.id, club_id=self.id, role=role, join_date=date.today()))
            db.session.commit()

    def remove_member(self, user):
        if user in self.members:
            self.members.remove(user)
            db.session.execute(members.delete().where(members.c.user_id == user.id, members.c.club_id == self.id))
            db.session.commit()
    
    def get_tags(self):
        return self.tags

    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)
            db.session.execute(tags.insert().values(tag_id=tag.id, club_id=self.id))
            db.session.commit()

    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)
            db.session.execute(tags.delete().where(tags.c.tag_id == tag.id, tags.c.club_id == self.id))
            db.session.commit()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(20), unique=True, nullable=False)
    last_name = db.Column(db.String(20), unique=True, nullable=False)
    favorites = db.relationship('Club', secondary=favorites, lazy='subquery',
        backref=db.backref('favorite_users', lazy=True))

    def __repr__(self):
        return f"User ('{self.username}', '{self.email}')"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_first_name(self):
        return self.first_name
    
    def get_user_email(self):
        return self.email
    
    def set_password(self, new_password):
        self.password = bcrypt.generate_password_hash(new_password)

    def check_password(self, check_password):
        return bcrypt.check_password_hash(self.password, check_password)
    
    def get_favorites(self):
        return self.favorites
    
    def get_clubs(self):
        return self.membership_clubs.all()
    
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    club_count = db.Column(db.Integer)

    def get_tagged_clubs_count(self):
        self.club_count = len(self.tagged_clubs.all())
        return self.club_count

    def get_tagged_clubs(self):
        return self.tagged_clubs.all()