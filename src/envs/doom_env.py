import warnings
from typing import Optional

import pygame
import numpy as np
import gymnasium as gym
import vizdoom.vizdoom as vzd

OFFSET = 25


def colorize_labels(labels: np.ndarray) -> np.ndarray:
    color_map = np.random.default_rng(3).uniform(low=0, high=255, size=(256, 3)).astype(np.uint8)
    return color_map[labels]


class VizdoomEnv(gym.Env):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "render_fps": vzd.DEFAULT_TICRATE,
    }

    def __init__(self, config: str,
                 render_fps: int = 1,
                 render_mode: str = None):
        """
        Arguments:
            config (str): path to the config file to load. Most settings should be set by this config file.
            render_fps (int): how many frames should be advanced per action. 1 = take action on every frame. Default: 1.
            render_mode(Optional[str]): the render mode to use could be either 'human' or 'rgb_array'

        This environment forces window to be hidden. Use `render()` function to see the game.

        Observations are dictionaries with different amount of entries, depending on if depth/label buffers were
        enabled in the config file (CHANNELS == 1 if GRAY8, else 3):
          "screen"        = the screen image buffer (always available) in shape (HEIGHT, WIDTH, CHANNELS)
          "depth"         = the depth image in shape (HEIGHT, WIDTH, 1), if enabled by the config file,
          "labels"        = the label image buffer in shape (HEIGHT, WIDTH, 1), if enabled by the config file.
                            For info on labels, access `env.state.labels` variable.
          "automap"       = the automap image buffer in shape (HEIGHT, WIDTH, CHANNELS), if enabled by the config file
          "game_variables" = all game variables, in the order specified by the config file
        """

        super().__init__()
        self.render_fps = render_fps
        self.frame_skip = 1
        self.render_mode = render_mode

        # init game
        self.game = vzd.DoomGame()
        self.game.load_config(config)
        self.game.set_window_visible(False)

        screen_format = self.game.get_screen_format()
        if screen_format not in [vzd.ScreenFormat.RGB24, vzd.ScreenFormat.GRAY8]:
            warnings.warn(
                f"Detected screen format {screen_format.name}. "
                f"Only RGB24 and GRAY8 are supported in the Gymnasium "
                f"wrapper. Forcing RGB24."
            )
            self.game.set_screen_format(vzd.ScreenFormat.RGB24)

        self.state = None

        self.clock = None
        self.window = None
        self.window_size = None

        if render_mode == "human":
            pygame.init()
            self.window_size = (2 * self.game.get_screen_width() + 3 * OFFSET,
                                2 * self.game.get_screen_height() + 3 * OFFSET)
            self.window = pygame.display.set_mode(self.window_size)
            self.clock = pygame.time.Clock()

        self.depth = self.game.is_depth_buffer_enabled()
        self.labels = self.game.is_labels_buffer_enabled()
        self.automap = self.game.is_automap_buffer_enabled()

        self.observation_space = self.__get_observation_space()
        self.action_space = gym.spaces.Discrete(self.game.get_available_buttons_size())

        self.game.init()

    def step(self, action: int):
        assert self.action_space.contains(action), f"{action} ({type(action)}) invalid"
        assert self.state is not None, "Call `reset` before using `step` method."

        act = np.zeros(self.action_space.n)
        act[action] = 1
        act = np.uint8(act)
        env_action = act.tolist()
        reward = self.game.make_action(env_action, self.frame_skip)
        self.state = self.game.get_state()
        terminated = self.game.is_episode_finished()

        if self.render_mode == "human":
            self.render()
        return self.__collect_observations(), reward, terminated, False, {}

    def reset(self, seed: int = None, options: list = None):
        super().reset(seed=seed)

        if seed is not None:
            self.game.set_seed(seed)
        self.game.new_episode()
        self.state = self.game.get_state()

        return self.__collect_observations(), {}

    def render(self):
        if self.render_mode == "rgb_array":
            return self.state.screen_buffer
        elif self.render_mode == "human":
            # Transpose image (pygame wants (width, height, channels), we have (height, width, channels))
            screen, depth, labels, automap = self.__get_human_render_data()

            horiz_split = (self.window_size[0] + OFFSET) // 2
            vert_split = (self.window_size[1] + OFFSET) // 2

            self.window.blit(pygame.surfarray.make_surface(screen), (OFFSET, OFFSET))
            self.window.blit(pygame.surfarray.make_surface(depth), (horiz_split, OFFSET))
            self.window.blit(pygame.surfarray.make_surface(labels), (OFFSET, vert_split))
            self.window.blit(pygame.surfarray.make_surface(automap), (horiz_split, vert_split))

            pygame.display.update()

            pygame.event.pump()
            pygame.display.flip()
            self.clock.tick(self.metadata["render_fps"])

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()

    def __get_human_render_data(self):
        state = self.state
        w, h = self.game.get_screen_width(), self.game.get_screen_height()
        screen, depth = state.screen_buffer, np.zeros((h, w, 3))
        labels, automap = np.zeros((h, w, 3)), np.zeros((h, w, 3))

        if self.game.get_screen_channels() == 1:
            screen = np.repeat(state.screen_buffer, 3, axis=2)
        screen = screen.transpose((1, 0, 2))

        if self.depth:
            depth = np.repeat(state.depth_buffer[..., np.newaxis], 3, axis=2)
        depth = depth.transpose((1, 0, 2))

        if self.labels:
            labels = colorize_labels(state.labels_buffer)
            labels = labels.transpose((1, 0, 2))

        if self.automap:
            automap = state.automap_buffer
            if self.game.get_screen_channels() == 1:
                automap = np.repeat(state.automap_buffer, 3, axis=2)
            automap = automap.transpose((1, 0, 2))

        return screen, depth, labels, automap

    def __collect_observations(self):
        observation = {}
        if self.state is not None:
            observation["screen"] = self.state.screen_buffer
            if self.game.get_screen_channels() == 1:
                observation["screen"] = self.state.screen_buffer[..., np.newaxis]
            if self.depth:
                observation["depth"] = self.state.depth_buffer[..., np.newaxis]
            if self.labels:
                observation["labels"] = self.state.labels_buffer[..., np.newaxis]
            if self.automap:
                observation["automap"] = self.state.automap_buffer
                if self.game.get_screen_channels() == 1:
                    observation["automap"] = self.state.automap_buffer[..., np.newaxis]
            if self.num_game_variables > 0:
                observation["game_variables"] = self.state.game_variables.astype(np.float32)
        else:
            # there is no state in the terminal step, so a zero observation is returned instead
            for space_key, space_item in self.observation_space.spaces.items():
                observation[space_key] = np.zeros(space_item.shape, dtype=space_item.dtype)
        return observation

    def __get_observation_space(self):
        scalar_shape = (self.game.get_screen_height(), self.game.get_screen_width(), 1)
        channel_shape = (self.game.get_screen_height(), self.game.get_screen_width(), self.game.get_screen_channels())

        spaces = {"screen": gym.spaces.Box(0, 255, channel_shape, dtype=np.uint8)}

        if self.depth:
            spaces["depth"] = gym.spaces.Box(0, 255, scalar_shape, dtype=np.uint8)
        if self.labels:
            spaces["labels"] = gym.spaces.Box(0, 255, scalar_shape, dtype=np.uint8)
        if self.automap:
            spaces["automap"] = gym.spaces.Box(0, 255, channel_shape, dtype=np.uint8)

        self.num_game_variables = self.game.get_available_game_variables_size()
        if self.num_game_variables > 0:
            spaces["game_variables"] = gym.spaces.Box(
                np.finfo(np.float32).min,
                np.finfo(np.float32).max,
                (self.num_game_variables,),
                dtype=np.float32,
            )

        return gym.spaces.Dict(spaces)
