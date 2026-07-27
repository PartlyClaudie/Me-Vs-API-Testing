import uuid
from flask import make_response
from sqlalchemy.exc import IntegrityError
from models import db, Poll, Option, Vote
from flask import Flask, jsonify, request, render_template
from models import db, Poll, Option

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///polls.db"
db.init_app(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/polls", methods=["POST"])
def create_poll():
    data = request.get_json()

    if not data or not data.get("question"):
        return jsonify({"error": "question is required"}), 400

    options = data.get("options", [])
    if len(options) < 2:
        return jsonify({"error": "at least 2 options are required"}), 400

    poll = Poll(question=data["question"])
    for option_text in options:
        poll.options.append(Option(text=option_text))

    db.session.add(poll)
    db.session.commit()

    return jsonify(poll.to_dict()), 201

@app.route("/api/polls", methods=["GET"])
def list_polls():
    polls = Poll.query.all()
    return jsonify([poll.to_dict() for poll in polls])


@app.route("/api/polls/<int:poll_id>", methods=["GET"])
def get_poll(poll_id):
    poll = Poll.query.get(poll_id)
    if not poll:
        return jsonify({"error": "poll not found"}), 404
    return jsonify(poll.to_dict())

@app.route("/api/polls/<int:poll_id>/vote", methods=["POST"])
def cast_vote(poll_id):
    poll = Poll.query.get(poll_id)
    if not poll:
        return jsonify({"error": "poll not found"}), 404

    data = request.get_json()
    option_id = data.get("option_id") if data else None

    option = Option.query.filter_by(id=option_id, poll_id=poll_id).first()
    if not option:
        return jsonify({"error": "option not found for this poll"}), 400

    voter_id = request.cookies.get("voter_id")
    new_voter = voter_id is None
    if new_voter:
        voter_id = str(uuid.uuid4())

    vote = Vote(poll_id=poll_id, option_id=option_id, voter_id=voter_id)
    db.session.add(vote)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "you have already voted on this poll"}), 409

    response = make_response(jsonify(poll.to_dict()))
    if new_voter:
        response.set_cookie("voter_id", voter_id, max_age=60 * 60 * 24 * 365)
    return response

@app.route("/api/reset", methods=["POST"])
def reset():
    db.session.query(Vote).delete()
    db.session.query(Option).delete()
    db.session.query(Poll).delete()
    db.session.commit()
    return "", 204

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)