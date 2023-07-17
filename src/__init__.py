from gymnasium.envs.registration import register

register(
    id="VizdoomMulti-v0",
    entry_point="src.envs:VizdoomEnv",
    kwargs={"config": "scenarios/multi.cfg"},
)
