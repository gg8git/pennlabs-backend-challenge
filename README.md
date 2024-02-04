# Penn Labs Backend Challenge

## Documentation

Fill out this section as you complete the challenge!

## Installation

1. Click the green "use this template" button to make your own copy of this repository, and clone it. Make sure to create a **private repository**.
2. Change directory into the cloned repository.
3. Install `pipx`
   - `brew install pipx` (macOS)
   - See instructions here https://github.com/pypa/pipx for other operating systems
4. Install `poetry`
   - `pipx install poetry`
5. Install packages using `poetry install`.

## File Structure

- `app.py`: Main file. Has configuration and setup at the top. Add your [URL routes](https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing) to this file!
- `models.py`: Model definitions for SQLAlchemy database models. Check out documentation on [declaring models](https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/) as well as the [SQLAlchemy quickstart](https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/#quickstart) for guidance
- `bootstrap.py`: Code for creating and populating your local database. You will be adding code in this file to load the provided `clubs.json` file into a database.

## Developing

0. Determine how to model the data contained within `clubs.json` and then complete `bootstrap.py`
1. Activate the Poetry shell with `poetry shell`.
2. Run `python3 bootstrap.py` to create the database and populate it.
3. Use `flask run` to run the project.
4. Follow the instructions [here](https://www.notion.so/pennlabs/Backend-Challenge-862656cb8b7048db95aaa4e2935b77e5).
5. Document your work in this `README.md` file.

## Documentation

Explanations for classes and methods are provided by comments. The following documentation contains my rationale for the program design.

### models.py

The models.py class has four primary classes--Club, User, Tag, and Review. 

First, I thought it made the most sense for either Club or User to drive the majority of the program. I finally decided on storing most of the information under Club because I thought that most of the information contained in Penn Club Review should be directly linked to each club. This choice was most likely more important to make because of limitations such as the structure of many-to-many relations in Flask SQL-Alchemy, which are generally driven from one direction and hard to build upon without creating additional new classes (which I did not want to do). 

The Club class has a few fields, including code, name, description, and more. I initially wanted to access information about each class on the API side through IDs, but the requirements for this project included tasks such as searching for club using name and accessing user profiles given usernames, so I ended up scrapping the ID field and making usernames and club names unique and the primary keys of their respective classes to align with those expectations. Most of the methods underneath Club were simply accessor methods.

For the User class, I incorporated pretty basic fields, including username, email, password, first name, and last name. Similarly, most of the methods under User were accessor methods, except for the methods that had to do with setting and checking passwords. [see if need to elaborate further on passwords]

To connect the Club and User class, I had to create multiple many-to-many mappings, such as those for officer, member, and favorite. Other than favorite, officer and member were stored from the club side, due to the club-focused emphasis I explained above. It is probably worth noting that I did look into creating a single many-to-many mapping to register membership, with an extra field that expressed the role of the User, but I found that creating such a mapping was significantly harder in Flask than I think it would have been in Django. It is probably also worth noting that I set up the program such that all officers that were added were also added as members, and any members that were removed were also removed as officers.

The Tag class was pretty basic. Each Tag object had a name, and then I created one more many-to-many field to associate tags with clubs. 

While Club, User, and Tag were basically necessary to create given the instructions we were provided, I decided to create an extra class called Review. I thought that a webside called "Penn Club Review" might as well have some system for users to review clubs and provide their opinion on different clubs. I gave the Review class a bunch of fields I thought were necessary, and then used one-to-many mappings to store these reviews under the Club and User classes. This allowed me to access the reviews associated with each club and each user in a much cleaner way.

In sum:
4 Classes (Club, User, Tag, Review)
5 Mappings(many-to-many: members, officers, favorites, tags; one-to-many: reviews (for both clubs and users))

### app.py

This file mostly contained the API I created in order to allow the frontend to access the information stored in the database. In particular, I had a set of routes for each class I created in models.py.

First, I had a set of routes for anything related to clubs. This included a general route to access all clubs and add clubs, as well as individual routes to look at the information for each club and modify that information. From the club side, you can edit almost anything to do with the club other than the number of favorites you have. I imagine that these routes would be used by officers of clubs in some sort of dashboard to manage their club information, their members, and their reviews. I created one extra route to access club emails, because I've noticed that getting a list of member emails is probably the most important thing for officers. 

Second, I had a set of routes for anything related to users. Similarly, this included a general route to access all users and to add users, as well as individual routes to look at the information for each user and modify that information. From the user side, you can edit almost anything that has to do with being a user except for your status as the officer of a club. I imagine that users who are not officers will use these routes to see information about themselves, their clubs, and to post reviews of clubs.

Third, I had a set of routes for anything related to reviews. While I imagine that most review posts or management will be done through clubs and users. I think that this route will still likely be useful for the frontend (perhaps to see all reviews, or something else of the sort).

Finally, I had a set of routes for everything related to tags. This can probably be used on the main page when people are browsing through clubs, in order to filter for clubs. 

I thought these routes were sufficient to allow the frontend to access the majority of the information they may potentially need from the backend.

## Submitting

Follow the instructions on the Technical Challenge page for submission.

## Installing Additional Packages

Use any tools you think are relevant to the challenge! To install additional packages
run `poetry add <package_name>` within the directory. Make sure to document your additions.

### Additional Packages

I chose to download two additional packages, which were flask_bcrypt and flask_login. Neither of these packages are central to the operation of the program, but could be useful for further expansion.
