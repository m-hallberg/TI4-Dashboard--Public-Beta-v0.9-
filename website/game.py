from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Players, Games, Strats, Agendas, Nominations, Votes
from . import db
import time

game = Blueprint('game', __name__)

def strat_init():
    strats = {
        1 : '1leadership',
        2 : '2diplomacy',
        3 : '3politics',
        4 : '4construction',
        5 : '5trade',
        6 : '6warfare',
        7 : '7technology',
        8 : '8imperial',
    }
    Strats.query.delete()
    for id, name in strats.items():
        creation = Strats(id=id, name=name, active=False)
        db.session.add(creation)
        db.session.commit()
    
def new_agenda(new_type):
    game_query = Games.query.filter(Games.id == 1)
    for game in game_query:
        game.agenda += 1
    new_agenda = Agendas(agenda_type = new_type, game = 1)
    if new_type == 'for_against':
        pro = Nominations(title='for', agenda = game.agenda, total = 0)
        con = Nominations(title='against', agenda = game.agenda, total = 0) 
        db.session.add(pro)
        db.session.add(con)
    db.session.add(new_agenda)
    db.session.commit()

def submit_votes(player_selection, player_votes):
    games = Games.query.filter(Games.id == 1)
    player_count = Players.query.filter(Players.game == 1).count()
    for game in games:
        player = game.player
        agenda = game.agenda
    if Nominations.query.filter(Nominations.agenda == agenda, Nominations.title == player_selection).count() == 0:
        new_nomination(player_selection)
    nominations = Nominations.query.filter(Nominations.agenda == agenda, Nominations.title == player_selection)

    for nomination in nominations:
        nom = int(nomination.id)

    vote_add = Votes(player = player,
                     nomination = nom,
                     value = int(player_votes),
                     agenda = agenda
                     )
    db.session.add(vote_add)
    db.session.commit()
    for nomination in nominations:
        nomination.total = nomination.total + int(player_votes)
    db.session.commit()
    if player == player_count:
        winner = Nominations.query.filter(Nominations.agenda == agenda).order_by(Nominations.total.desc()).first()
        agenda = Agendas.query.filter(Agendas.game == 1, Agendas.id == agenda).first()
        agenda.winner = winner.id
        db.session.commit()
        
    

def new_nomination(nom):
    game_query = Games.query.filter(Games.id == 1)
    for game in game_query:
        agenda = game.agenda
    nom_add = Nominations(title=nom, agenda = agenda, total=0)
    db.session.add(nom_add)
    db.session.commit()
 
def strat_reset():
    strats = Strats.query.all()
    for strat in strats:
        strat.active = False
        strat.player = ''
    db.session.commit()

def strat_activate():
    player_query = Players.query.filter(Players.game ==1 )
    for player in player_query:
        for strat in player.strats:
            strat.active = True
        db.session.commit()

def new_speaker(seat):    
    players = []
    new_order = []
    new_speaker = 0
    player_query = Players.query.order_by(Players.seat).all()
    for player in player_query:
        players.append(player.seat)
    for i in range(len(players)):
        new_order.append(players[(((seat + i) % len(players))-1)])
    for index in new_order:
        new_speaker += 1
        player = Players.query.filter_by(seat=index).first()
        player.speaker = new_speaker
    db.session.commit()

def next_player():
    game_query = Games.query.filter(Games.id == 1)  # Gets game with id 1
    for game in game_query:  # Iterates over single game returned by game_query
        current_player = game.player  # Sets current player equal to player before fuction was called
        if game.phase == 1:
            while True:
                current_player += 1  # Increments player value by 1
                if current_player > 8:  # Checks if new player value goes higher than total player count
                    current_player = 1  # Sets player value back to beginning
                player = Players.query.filter(Players.initiative == current_player).first()
                if player:
                    new_player = current_player
                    break
        elif game.phase == 2:
            player_count = Players.query.filter(Players.game == 1).count()
            current_player += 1  # Increments player value by 1
            if current_player > player_count:  # Checks if new player value goes higher than total player count
                current_player = 1  # Sets player value back to beginning
            new_player = current_player
        game.player = new_player  # Updates game db with new player value
    db.session.commit()  # Commits all changes

def use_strategy(initiative):
    strat_query = Strats.query.filter(Strats.id == initiative)
    for strat in strat_query:
        strat.active = False
    db.session.commit()

def update_initiative():
    player_query = Players.query.filter(Games.id==1)
    for player in player_query:
        for strat in player.strats:
            player.initiative = strat.id
        db.session.commit()

def next_phase():
    game_query = Games.query.filter(Games.id == 1)
    for game in game_query:
        if game.phase == 1:
            game.phase = 2
            game.player = 1
        elif game.phase == 2:
            game.phase = 0
            game.player = 0
            game.agenda = 0
            Votes.query.delete()
            Nominations.query.delete()
            Agendas.query.delete()
            strat_reset()
            old_round = game.round
            game.round = old_round + 1 
        elif game.phase == 0:
            game.phase = 1
            strat_activate()
            update_initiative()
            next_player()
        db.session.commit()

def game_start():
    start = round(time.time()*1000)
    game = Games(
        start=start,
        player = 0,  
        agenda = 0,
        round = 1,
        phase = 1)
    db.session.add(game)
    Votes.query.delete()
    Nominations.query.delete()
    Agendas.query.delete()
    db.session.commit()
    next_player()
    
    


@game.route('/speaker-test')
def speaker_test():
    strat_init()
    return render_template("home.html")
    

@game.route('/current-game', methods=['GET', 'POST'])
def current_game():
    game_query = Games.query.filter(Games.id == 1)
    agenda_query = Agendas.query.filter(Agendas.game == 1).order_by(Agendas.id)

    for game in game_query:
        
        if game.phase == 0:
            player_query = Players.query.order_by(Players.speaker)
            strat_query = Strats.query.order_by(Strats.id)
            if request.form.get('submit_strats'):
                for player in player_query:
                    cur_strat = int(request.form.get(f'{player.seat}'))
                    new_strat = Strats.query.filter(Strats.id == cur_strat).first()
                    new_strat.player = player.seat
                    print(new_strat.player)
                db.session.commit()
                next_phase()
                return redirect(url_for('game.current_game'))
                                  

            
            return render_template("choose-strat.html",
                                   game_state=game_query,
                                   strats=strat_query,
                                   players=player_query)
        
        
        if game.phase == 1:
            player_query = Players.query.order_by(Players.initiative)
            strat_query = Strats.query.order_by(Strats.id)
            if request.form.get('game_action'):
                if request.form.get('game_action') == 'next_player':
                    for game in game_query:
                        next_player()
                elif request.form.get('game_action') == 'use_strategy':
                    for game in game_query:
                        use_strategy(game.player)
                elif request.form.get('game_action') ==  'next_phase':
                    for game in game_query:
                        next_phase()
                return redirect(url_for('game.current_game'))

            if request.form.get('change_speaker'):
                new_speaker(int(request.form.get('change_speaker')))
                return redirect(url_for('game.current_game'))
            
            return render_template("action-phase.html", 
                                   game_state = game_query,
                                   strats = strat_query,
                                   players = player_query
                                   )

        elif game.phase == 2:
            player_query = Players.query.order_by(Players.speaker)
            agenda_query = Agendas.query.order_by(Agendas.id)
            if request.form.get('game_action'):
                if request.form.get('game_action') == 'next_player':
                    for game in game_query:
                        next_player()
                elif request.form.get('game_action') == 'use_strategy':
                    for game in game_query:
                        use_strategy(game.player)
                elif request.form.get('game_action') ==  'next_phase':
                    for game in game_query:
                        next_phase()
                return redirect(url_for('game.current_game'))

            if request.form.get('change_speaker'):
                new_speaker(int(request.form.get('change_speaker')))
                return redirect(url_for('game.current_game'))
            
            if request.form.get('new_agenda'):
                new_agenda(request.form.get('new_agenda'))
                return redirect(url_for('game.current_game'))
            
            if request.form.get('agenda_action'):
                agenda_action = request.form.get('agenda_action')

                if agenda_action == 'submit_votes':
                    submit_votes(request.form.get('player_selection'), request.form.get('player_votes'))

                elif agenda_action == 'new_planet_submit':
                    planet_add = request.form.get('new_planet')
                    new_nomination(planet_add)

                return redirect(url_for('game.current_game'))


            return render_template("agenda-phase.html", 
                                   game_state=game_query,
                                   players = player_query,
                                   agendas = agenda_query
                                   )

        
    #return render_template("current-game.html", game_players=game_players, game_state=game_state, strat_state=strat_state, strat_players=strat_players)


@game.route('/create-game', methods=['GET', 'POST'])
def create_game():
    if request.method == 'POST':
        if request.form.get('clearconfirm') == 'true':
            strat_init()
            Games.query.delete()  # Clears gamestate table
            Players.query.delete()  # Clears player table
            print('Player table cleared successfully.')
            if request.form.get('p1name'):
                p1name = request.form.get('p1name')
                p1seat = request.form.get('p1seat')
                p1race = request.form.get('p1race')
                p1color = request.form.get('p1color')
                p1strat = request.form.get('p1strat')
                print(p1name, p1seat, p1race, p1color)
                strat_query= Strats.query.filter(Strats.name == p1strat)
                for strat in strat_query:
                    strat.player = p1seat
                    strat.active = True
                    initiative = strat.id
                p1 = Players(name=p1name, seat=p1seat, game=1, initiative=initiative, race=p1race, color=p1color, speaker=p1seat)
                db.session.add(p1)
                db.session.commit()
                print('Player 1 Added Successfully!')
            if request.form.get('p2name'):
                p2name = request.form.get('p2name')
                p2seat = request.form.get('p2seat')
                p2race = request.form.get('p2race')
                p2color = request.form.get('p2color')
                p2strat = request.form.get('p2strat')
                print(p2name, p2seat, p2race, p2color)
                strat_query= Strats.query.filter(Strats.name == p2strat)
                for strat in strat_query:
                    strat.player = p2seat
                    strat.active = True
                    initiative = strat.id
                p2 = Players(name=p2name, seat=p2seat, game=1, initiative=initiative, race=p2race, color=p2color, speaker=p2seat)
                db.session.add(p2)
                db.session.commit()
                print('Player 2 Added Successfully!')
            if request.form.get('p3name'):
                p3name = request.form.get('p3name')
                p3seat = request.form.get('p3seat')
                p3race = request.form.get('p3race')
                p3color = request.form.get('p3color')
                p3strat = request.form.get('p3strat')
                print(p3name, p3seat, p3race, p3color)
                strat_query= Strats.query.filter(Strats.name == p3strat)
                for strat in strat_query:
                    strat.player = p3seat
                    strat.active = True
                    initiative = strat.id
                p3 = Players(name=p3name, seat=p3seat, game=1, initiative=initiative, race=p3race, color=p3color, speaker=p3seat)
                db.session.add(p3)
                db.session.commit()
                print('Player 3 Added Successfully!')
            if request.form.get('p4name'):
                p4name = request.form.get('p4name')
                p4seat = request.form.get('p4seat')
                p4race = request.form.get('p4race')
                p4color = request.form.get('p4color')
                p4strat = request.form.get('p4strat')
                print(p4name, p4seat, p4race, p4color)
                strat_query= Strats.query.filter(Strats.name == p4strat)
                for strat in strat_query:
                    strat.player = p4seat
                    strat.active = True
                    initiative = strat.id
                p4 = Players(name=p4name, seat=p4seat, game=1, initiative=initiative, race=p4race, color=p4color, speaker=p4seat)
                db.session.add(p4)
                db.session.commit()
                print('Player 4 Added Successfully!')
            if request.form.get('p5name'):
                p5name = request.form.get('p5name')
                p5seat = request.form.get('p5seat')
                p5race = request.form.get('p5race')
                p5color = request.form.get('p5color')
                p5strat = request.form.get('p5strat')
                print(p5name, p5seat, p5race, p5color)
                strat_query= Strats.query.filter(Strats.name == p5strat)
                for strat in strat_query:
                    strat.player = p5seat
                    strat.active = True
                    initiative = strat.id
                p5 = Players(name=p5name, seat=p5seat, game=1, initiative=initiative, race=p5race, color=p5color, speaker=p5seat)
                db.session.add(p5)
                db.session.commit()
                print('Player 5 Added Successfully!')
            if request.form.get('p6name'):
                p6name = request.form.get('p6name')
                p6seat = request.form.get('p6seat')
                p6race = request.form.get('p6race')
                p6color = request.form.get('p6color')
                p6strat = request.form.get('p6strat')
                print(p6name, p6seat, p6race, p6color)
                strat_query= Strats.query.filter(Strats.name == p6strat)
                for strat in strat_query:
                    strat.player = p6seat
                    strat.active = True
                    initiative = strat.id
                p6 = Players(name=p6name, seat=p6seat, game=1, initiative=initiative, race=p6race, color=p6color, speaker=p6seat)
                db.session.add(p6)
                db.session.commit()
                print('Player 6 Added Successfully!')
            if request.form.get('p7name'):
                p7name = request.form.get('p7name')
                p7seat = request.form.get('p7seat')
                p7race = request.form.get('p7race')
                p7color = request.form.get('p7color')
                p7strat = request.form.get('p7strat')
                print(p7name, p7seat, p7race, p7color)
                strat_query= Strats.query.filter(Strats.name == p7strat)
                for strat in strat_query:
                    strat.player = p7seat
                    strat.active = True
                    initiative = strat.id
                p7 = Players(name=p7name, seat=p7seat, game=1, initiative=initiative, race=p7race, color=p7color, speaker=p7seat)
                db.session.add(p7)
                db.session.commit()
                print('Player 7 Added Successfully!')
            if request.form.get('p8name'):
                p8name = request.form.get('p8name')
                p8seat = request.form.get('p8seat')
                p8race = request.form.get('p8race')
                p8color = request.form.get('p8color')
                p8strat = request.form.get('p8strat')
                print(p8name, p8seat, p8race, p8color)
                strat_query= Strats.query.filter(Strats.name == p8strat)
                for strat in strat_query:
                    strat.player = p8seat
                    strat.active = True
                    initiative = strat.id
                p8 = Players(name=p8name, seat=p8seat, game=1, initiative=initiative, race=p8race, color=p8color, speaker=p8seat)
                db.session.add(p8)
                db.session.commit()
                print('Player 8 Added Successfully!')
            game_start()
            
            return redirect(url_for('game.current_game'))
        
    return render_template("create-game.html")