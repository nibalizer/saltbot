SaltBot
=======


Saltbot is an ai that plays StarCraft II

In it's current development stage, it is a series of agents written agains the pysc2 environment from DeepMind.



Requirements
------------

Requires the [sc2 RL](https://github.com/deepmind/pysc2) environment from DeepMind.


Usage
-----


From the root directory of the repository run:

```bash
python -m pysc2.bin.agent --map CollectMineralShards --agent saltbot.agents.scripted_agent.NibzCollectMineralShards
```

