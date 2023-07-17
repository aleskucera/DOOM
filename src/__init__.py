from gymnasium.envs.registration import register

register(
    id="ViZDoomMulti-v0",
    entry_point="src.envs:ViZDoomEnv",
    kwargs={"config": "scenarios/multi.cfg"},
)

register(
    id="ViZDoomBasic-v0",
    entry_point="src.envs:ViZDoomEnv",
    kwargs={"config": "scenarios/basic.cfg"},
)

register(
    id="ViZDoomCorridor-v0",
    entry_point="src.envs:ViZDoomEnv",
    kwargs={"config": "scenarios/deadly_corridor.cfg"},
)
