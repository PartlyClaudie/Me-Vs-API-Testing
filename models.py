from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Poll(db.Model):
    __tablename__ = "polls"

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    options = db.relationship("Option", backref="poll", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "options": [option.to_dict() for option in self.options],
        }


class Option(db.Model):
    __tablename__ = "options"

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey("polls.id"), nullable=False)
    votes = db.relationship("Vote", backref="option", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "text": self.text,
            "vote_count": len(self.votes),
        }


class Vote(db.Model):
    __tablename__ = "votes"

    id = db.Column(db.Integer, primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey("options.id"), nullable=False)
    poll_id = db.Column(db.Integer, db.ForeignKey("polls.id"), nullable=False)
    voter_id = db.Column(db.String(100), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("poll_id", "voter_id", name="one_vote_per_voter_per_poll"),
    )