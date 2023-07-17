from __future__ import print_function
import os
import time
from random import choice
from threading import Thread
from vizdoom import *
import vizdoom as vzd
def demo_name(episode_):
    return f'multi_rec{episode_}.lmp'
def set_timeout(game):
    timeout_minutes = 0.2
    game.set_episode_timeout(int(timeout_minutes * 60 * game.get_ticrate()))
    print('Game timeout:', game.get_episode_timeout())
def player1():
    game = DoomGame()
    game.load_config(os.path.join(vzd.scenarios_path, "cig.cfg"))
    game.add_game_args(f'-record {demo_name(0)}')
    game.add_game_args("-host 2 -deathmatch +sv_spawnfarthest 1")
    # game.set_mode(Mode.ASYNC_PLAYER)
    game.add_game_args("+name Player1 +colorset 0")
    set_timeout(game)
    # Unfortunately multiplayer game cannot be recorded using new_episode() method, use this command instead.
    game.init()
    actions = [[True, False, False], [False, True, False], [False, False, True]]
    for episode in range(1):
        # game.add_game_args(f'-record {demo_name(episode)}')
        if episode > 0:
            game.new_episode()
        i = 0
        while not game.is_episode_finished():
            i += 1
            if game.is_player_dead():
                game.respawn_player()
            game.make_action(choice(actions))
            if game.get_episode_time() + 1 == game.get_episode_timeout():
                game.send_game_command('stop')
            done = game.is_episode_finished()
            # print(game.get_episode_time(), game.get_episode_timeout(), game.get_ticrate())
    print("Game finished!")
    print("Player1 frags:", game.get_game_variable(GameVariable.FRAGCOUNT))
    game.close()
def player2():
    game = DoomGame()
    game.load_config(os.path.join(vzd.scenarios_path, "cig.cfg"))
    game.set_window_visible(True)
    game.add_game_args("-join 127.0.0.1")
    game.add_game_args("+name Player2 +colorset 3")
    set_timeout(game)
    game.init()
    actions = [[True, False, False], [False, True, False], [False, False, True]]
    for episode in range(1):
        if episode > 0:
            game.new_episode()
        while not game.is_episode_finished():
            if game.is_player_dead():
                game.respawn_player()
            game.make_action(choice(actions))
    print("Player2 frags:", game.get_game_variable(GameVariable.FRAGCOUNT))
    game.close()
def replay_as_player2():
    game = DoomGame()
    game.load_config(os.path.join(vzd.scenarios_path, "cig.cfg"))
    # At this moment ViZDoom will crash if there is no starting point - this is workaround for multiplayer map.
    game.add_game_args("-host 1 -deathmatch")
    game.set_mode(Mode.PLAYER)
    game.init()
    # Replays episode recorded by player 1 from perspective of player2.
    game.replay_episode(demo_name(0), 2)
    while not game.is_episode_finished():
        # time.sleep(1)
        game.advance_action()
    print("Game finished!")
    print("Player1 frags:", game.get_game_variable(GameVariable.PLAYER1_FRAGCOUNT))
    print("Player2 frags:", game.get_game_variable(GameVariable.PLAYER2_FRAGCOUNT))
    game.close()
    # Delete multi_rec.lmp
    # os.remove(demo_name(0))
if __name__ == '__main__':
    print("\nRECORDING")
    print("************************\n")
    # if not os.path.exists('multi_rec.lmp'):
    #     os.mknod('multi_rec.lmp')
    p1 = Thread(target=player1)
    p1.start()
    time.sleep(0.1)
    player2()
    print("\nREPLAY")
    time.sleep(1)
    print("************************\n")
    replay_as_player2()
