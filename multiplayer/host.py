import os
import random

import vizdoom as vzd

MAP = "map01"
CONFIG_FILE = os.path.join(vzd.scenarios_path, 'cig.cfg')
GAME_ARGS = "-host 2 \
             -port 5029 \
             -deathmatch \
             +viz_connect_timeout 60 \
             +timeLimit 10.0 \
             +sv_forcerespawn 1 \
             +sv_noautoaim 1 \
             +sv_respawnprotect 1 \
             +sv_spawnfarthest 1 \
             +sv_nocrouch 1 \
             +viz_respawn_delay 10 \
             +viz_nocheat 1 \
             +name Host +colorset 0"


def create_game(config_file: str, map: str, game_args: str):
    game = vzd.DoomGame()
    game.load_config(config_file)
    game.set_doom_map(map)
    game.add_game_args(game_args)
    game.set_mode(vzd.Mode.ASYNC_SPECTATOR)
    return game


if __name__ == '__main__':
    actions = [
        [1, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0],
    ]

    game = create_game(CONFIG_FILE, MAP, GAME_ARGS)
    game.init()

    while not game.is_episode_finished():
        # s = game.get_state()
        # game.make_action(random.choice(actions))

        if game.is_player_dead():
            game.respawn_player()

    game.close()
