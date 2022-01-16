# Blackjack Simulator

blackjack-simulator is a python module for playing and simulating multiple games of blackjack.


## Usage
### As a script
```powershell
python .\run.py [--config path/to/config] [-h]
```

### As a Package
```powershell
python -m blackjack [--config path/to/config] [-h]
```

## Config

All settings are configured via a config.ini located in the directory running the module. A specific config file can also be specified via the command line with the `--config` argument.

- Game Settings
  - `DECK_COUNT`: Number of decks that make up a shoe.
  - `BLACKJACK_PAYOUT`: Amount of money Blackjack pays out. (Usually 1.5 or 1.2)
  - `SURRENDER`: Whether/when surrender can de done. (Early, Late, or None)
  - `HIT_ON_SOFT_17`: Wherther the dealer must hit on a soft 17.
  - `DOUBLE_AFTER_SPLIT`: Whether a player can double after splitting.
  - `RESPLIT_ACES`: Whether the player can split Aces after previously splitting Aces.
  - `SPLIT_LIMIT`: The maximum number of times a player can split.
- Table Settings:
  - `TABLE_MINIMUM`: The minimum the player can bet each hand.
  - `TABLE_MAXIMUM`: The maximum the player can bet each hand.
  - `MAX_PLAYS`: The number of times a player can play at a table.
- Player Settings:
  - `DEFAULT_BET`: The default bet to play if a bet is not specified.
  - `DEFAULT_INSURANCE`: The default insurance to bet if offered.
  - `STARTING_WALLET`: Amount of money the player starts with.
  - `HUMAN_PLAYER`: Switch between playing and simulating.
- Misc Settings:
  - `SHOW_STATS`: Displays extra info about each game.


