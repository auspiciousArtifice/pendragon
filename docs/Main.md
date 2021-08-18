# Pendragon Documentation

Pendragon is a Discord bot for playing [the medieval social deception board game, Avalon](https://en.wikipedia.org/wiki/The_Resistance_(game)).

---

## Game Documentation

---

## User Documentation

### Commands

- **rules**  
  Sends message with link to rules of Avalon.
[Here is a link to the rules.](https://tinyurl.com/ycf4jttk)

- **gather**  
  Starts game if it hasn't began yet. Host is set as person who sent message. Fails if session doesn't exist or if the game started already.

- **disband**  
  Disbands current game session. Uses person who sent message to check game host.

- **begin**  
  Begins game session if enough players have joined. Fails if session doesn't exist or game started already.  

- **join**  
  Adds message sender to current game session if it exists.  

- **leave**  
  Removes message sender from current game session if the session exists and they are in the session.  

- **kick** \<player\>  
  Attempts to remove player specified in the kick message.  

- **players**  
  Lists all the current players in a session.  

- **percival**  
  Toggles whether Percival should be added or not. Off by default.  

- **morgana**  
  Toggles whether Morgana should be added or not. Off by default.  

- **mordred**  
  Toggles whether Mordred should be added or not. Off by default.  

- **oberon**  
  Toggles whether Oberon should be added or not. Off by default.  
  
- **lancelot**  
  Toggles whether Lancelot should be added or not. Off by default.  

- **all_roles**  
  Puts all roles into the game. Note: 1 villain role must be removed for a standard balanced game config.  

- **nominate** \<list of players\>  
  Nominates players towards current quest. Can only be used by the king. Errors out if a non-king player attempts to nominate.  

- **remove**  
  Removes nominated questing players from current quest.  
  
- **start_voting**  
  Starts voting process after all players have been nominated for current quest.  

- **vote** \<yes/no\>  
  Votes yea or nay on the currently nominated questing players. Will most likely be deprecated in favour of voting via reactions to embed.  

- **turn**  
  Shows the current turn and the turn order.  

- **lady**  
  Uses the Lady of the Lake to reveal the allegiance of a player.  

- **assassinate**  
  Attempts to assassinate Merlin. Only usable by the assassin.  

---

## Developer Documentation

### Installation

The bot needs the following files to run.

`.env` - Contains two arguments:  

- `DISCORD_TOKEN=<token>`  
- `DISCORD_GUILD=<token>`

`bot.py` - The main file to run the bot. Typically started with `python bot.py`.  
`requirements.txt` - List of dependencies required for the bot.  
`avalon.py` - All game logic here.  
`pencog.py` - Cog and Discord logic here. Used for sharding support later on.  
`settings.json` - All default settings for game sessions. Number of players is the primary way of determining which config is used.  

### Glossary

- **Game session**: A player that joins a game will not be able to participate in another one. One session per player, whether as a host or not.

### Commands

- **debug** \<subcommand\>
  
  Sends message with requested session variable data. Only used for debugging.

  Subcommands:
  
  - gamestate
  - players
  - nominated
  - host
  - king
  - voted
  - votes
  - quest
  - turn