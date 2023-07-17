import os
import torch
import torch.nn as nn

import cv2
import numpy as np
import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import EvalCallback

import src

ENV_NAME = "ViZDoomCorridor-v0"
MODEL_NAME = "ppo_vizdoom_corridor"
IMAGE_SHAPE = (60, 80)
TRAINING_TIMESTEPS = int(1e5)
N_STEPS = 128
N_ENVS = 8
FRAME_SKIP = 4


class ObservationWrapper(gym.ObservationWrapper):
    def __init__(self, env, shape=IMAGE_SHAPE):
        super().__init__(env)
        self.image_shape = shape
        self.image_shape_reverse = shape[::-1]
        self.env.frame_skip = FRAME_SKIP

        num_channels = env.observation_space.shape[2]
        new_shape = (shape[0], shape[1], num_channels)
        self.observation_space = gym.spaces.Box(0, 255, shape=new_shape, dtype=np.uint8)

    def observation(self, observation):
        observation = cv2.resize(observation, self.image_shape_reverse, interpolation=cv2.INTER_AREA)
        return observation


def wrap_env(env):
    env = ObservationWrapper(env)
    env = gym.wrappers.TransformReward(env, lambda r: r * 0.01)
    return env


def main():
    learn = False
    train_envs = make_vec_env(ENV_NAME, n_envs=N_ENVS, wrapper_class=wrap_env)
    val_envs = make_vec_env(ENV_NAME, n_envs=N_ENVS, wrapper_class=wrap_env)
    if learn:
        agent = PPO("CnnPolicy", train_envs, verbose=1, n_steps=N_STEPS, learning_rate=1e-4, batch_size=128,
                    tensorboard_log="logs")
        evaluation_callback = EvalCallback(val_envs, best_model_save_path=MODEL_NAME, eval_freq=5000,
                                           n_eval_episodes=10, verbose=1)
        agent.learn(total_timesteps=TRAINING_TIMESTEPS, callback=evaluation_callback, tb_log_name='ppo_vizdoom')
        # agent.save(MODEL_NAME)
        train_envs.close()
        val_envs.close()
    else:
        model = PPO.load('ppo_vizdoom_corridor/best_model.zip')
        obs = val_envs.reset()
        for i in range(1000):
            action, _states = model.predict(obs)
            obs, rewards, dones, info = val_envs.step(action)
            val_envs.render('human')


if __name__ == "__main__":
    main()
