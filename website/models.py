from . import db 


class Games(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start = db.Column(db.Integer)
    player = db.Column(db.Integer)
    agenda = db.Column(db.Integer)
    phase = db.Column(db.Integer)
    round = db.Column(db.Integer)
    agendas = db.relationship('Agendas')
    players = db.relationship('Players')

class Players(db.Model):
    seat = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    game = db.Column(db.Integer, db.ForeignKey('games.id'))
    initiative = db.Column(db.Integer)
    speaker = db.Column(db.Integer)
    race = db.Column(db.String)
    color = db.Column(db.String)
    strats = db.relationship('Strats')
    votes = db.relationship('Votes')

class Strats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    active = db.Column(db.Boolean, default=True)
    player = db.Column(db.Integer, db.ForeignKey('players.seat'))

class Agendas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agenda_type = db.Column(db.String)
    game = db.Column(db.Integer, db.ForeignKey('games.id'))
    winner = db.Column(db.Integer)
    votes = db.relationship('Votes')
    nominations = db.relationship('Nominations')

class Nominations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    agenda = db.Column(db.Integer, db.ForeignKey('agendas.id'))
    total = db.Column(db.Integer)
    votes = db.relationship('Votes')

class Votes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.Integer, db.ForeignKey('players.seat'))
    nomination = db.Column(db.Integer, db.ForeignKey('nominations.id'))
    value = db.Column(db.Integer)
    agenda = db.Column(db.Integer, db.ForeignKey('agendas.id'))

    
