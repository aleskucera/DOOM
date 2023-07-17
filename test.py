#!/usr/bin/env python3

#####################################################################
# Example for running a vizdoom scenario as a gym env
#####################################################################
import time
import gymnasium

from vizdoom import gymnasium_wrapper  # noqa
from gymnasium import envs
from gymnasium.utils.play import play
import src

keys_to_action = {
    (ord("w"),): 0,
    (ord("s"),): 1,
    (ord("a"),): 2,
    (ord("d"),): 3,
    (ord("q"),): 4,
    (ord("e"),): 5,
    (ord("r"),): 6,
}

if __name__ == "__main__":
    env = gymnasium.make("ViZDoomMulti-v0", render_mode="human")
    obs = env.reset()

    # play(env, keys_to_action=keys_to_action)
    for _ in range(10):
        done = False
        obs, info = env.reset(seed=42)
        while not done:
            random_action = env.action_space.sample()
            obs, rew, terminated, truncated, info = env.step(random_action)
            done = terminated or truncated
            time.sleep(0.1)
