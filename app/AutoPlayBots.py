from components.GameManager import GameManager
from components.ChessBot import ChessBot
from storage.DatabaseManager import DatabaseManager

if __name__ == '__main__':
    db_manager = DatabaseManager()
    bot = ChessBot(db_manager)

    game_manager = GameManager()
    game_manager.set_player_types('bot', 'bot')
    game_manager.bot_delay = 0

    games_played = 0

    try:
        while True:
            print('Starting a new game between bots...')
            game_manager.game_loop()
            game_manager.commit_thread.join()
            games_played += 1
            print('Game ended.\n')
            game_manager.reset()
    except KeyboardInterrupt:
        print(f'\nGames played: {games_played}')
        print('Exiting...')

