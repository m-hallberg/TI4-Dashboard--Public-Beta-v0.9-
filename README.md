# TI4-Dashboard--Public-Beta-v0.9-

This is a very rouugh draft of a project I've been working on for a little while. TI4 has a lot of things to track. Some of them simpler than others. When I play the game, I always 
wish I had some kind of public information board that shows me which player is active and which strategy cards are yet to be played. I also found it a bit annoying to track votes on 
agendas, especially when the player count is high and there are lots of nominations and votes flying around. This tool is meant to solve those problems. 

The main features are:
  -Player by player turn tracking
  -Speaker token tracking
  -Agenda tracking and calculator
  -Round counter
  -Game timer

Some features I'd like to implement later:
  -Input validation (important and already on the way)
  -Track multiple games simultaneously
  -Embedded music player
  -Map generator
  -Links to helful game resources

There are some other features I'd like to implement, but where it's at now is (relatively) stable, so I'd like to get input from other, more experienced TI player. What do you think
of the project so far? What features would you like to see added? What elements could be improved?

A bit about this implementation:
  -This is a python program. It was developed for Python 3.11.5. I couldn't say how well it works on any previous version of Python.
  -There are few dependencies you'll need to intstall for Python:
    -Flask 2.2.2
    -flask-sqlalchemy 3.1.1
    -flask-login 0.6.2

By default, the webapp will run on http://127.0.0.1:5000

As of right now there is NO input validation. If you run into an error (it will be very obvious if there's an error), your best bet is to hit the back button and then refresh. If that doesn't 
work, just create a new game. Input validation is coming very soon.
