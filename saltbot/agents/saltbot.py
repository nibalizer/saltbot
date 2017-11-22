# Copyright 2017 Google Inc. All Rights Reserved.
# Copyright 2017 Spencer Krum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Some code from (or inspired by)
# https://github.com/skjb/pysc2-tutorial/tree/master/Building%20a%20Basic%20Agent

"""Scripted agents."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import time
import itertools
import random

import numpy

from pysc2.agents import base_agent
from pysc2.lib import actions
from pysc2.lib import features

_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_PLAYER_FRIENDLY = 1
_PLAYER_NEUTRAL = 3  # beacon/minerals
_PLAYER_HOSTILE = 4
_NO_OP = actions.FUNCTIONS.no_op.id
_MOVE_SCREEN = actions.FUNCTIONS.Move_screen.id
_ATTACK_SCREEN = actions.FUNCTIONS.Attack_screen.id
_SELECT_ARMY = actions.FUNCTIONS.select_army.id
_NOT_QUEUED = [0]
_SELECT_ALL = [0]

# Functions
_BUILD_PYLON = actions.FUNCTIONS.Build_Pylon_screen.id
_BUILD_PROBE = actions.FUNCTIONS.Train_Probe_quick.id
_BUILD_GATEWAY = actions.FUNCTIONS.Build_Gateway_screen.id
_NOOP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id

# Features
_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_POWER = features.SCREEN_FEATURES.power.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index

# Unit IDs
_PROTOSS_NEXUS = 59
_PROTOSS_PYLON = 60
_PROTOSS_PROBE = 84

# Parameters
_NOT_QUEUED = [0]
_PLAYER_SELF = 1
_QUEUED = [1]
_SUPPLY_MAX = 4
_SUPPLY_USED = 3





class MineMinerals(base_agent.BaseAgent):
  """An agent specifically for mining up some minerals"""

  def __init__(self):
    super(MineMinerals, self).__init__()

    # configurable parameters
    self.count_max = 10


    # scehduling system
    self.schedule = itertools.cycle(['macro', 'build', 'micro'])
    self.state = 'macro'
    self.count = self.count_max

    # simple flag to do one time setup stuff
    # right now this is just 'which corner' detection
    self.setup_complete = False


    self.base_top_left = None

    # Build order
    self.probe_selected = False
    self.pylon_built = False
    self.gateway_built = False


    # Macro
    self.nexus_selected = False


  def transformLocation(self, x, x_distance, y, y_distance):
      if not self.base_top_left:
          return [x - x_distance, y - y_distance]

      return [x + x_distance, y + y_distance]


  def step(self, obs):
    super(MineMinerals, self).step(obs)

    # Sleep in the loop so we can see what is going on
    time.sleep(0.1)


    # Do setup tasks
    if self.setup_complete:
      # Detect which corner we spawned in (and which direction the enemy is in
      player_y, player_x = (obs.observation["minimap"][_PLAYER_RELATIVE] == _PLAYER_NEUTRAL).nonzero()
      self.base_top_left = player_y.mean() <= 31
      self.setup_complete = True


    # Scheduler loop
    if self.count == 0:
      self.count = self.count_max
      self.state = next(self.schedule)
      self.pylon_built = False
      self.gateway_built = False
      self.probe_selected = False
      self.nexus_selected = False
    else:
      self.count -= 1

    # Build order tasks
    if self.state == 'build':
      print("doing the build order")

      # Create Pylon
      if not self.pylon_built:
        if not self.probe_selected:
          unit_type = obs.observation["screen"][_UNIT_TYPE]
          unit_y, unit_x = (unit_type == _PROTOSS_PROBE).nonzero()

          target = [unit_x[0], unit_y[0]]

          self.probe_selected = True
          
          return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
          
        elif _BUILD_PYLON in obs.observation["available_actions"]:
          unit_type = obs.observation["screen"][_UNIT_TYPE]
          unit_y, unit_x = (unit_type == _PROTOSS_NEXUS).nonzero()

          target = self.transformLocation(int(unit_x.mean()), 0, int(unit_y.mean()), 20)

          self.pylon_built = True

          return actions.FunctionCall(_BUILD_PYLON, [_NOT_QUEUED, target])
      elif not self.gateway_built:
          if _BUILD_GATEWAY in obs.observation["available_actions"]:
              unit_type = obs.observation["screen"][_UNIT_TYPE]
              unit_y, unit_x = (unit_type == _PROTOSS_PYLON).nonzero()
              target = self.transformLocation(int(unit_x.mean()), 10, int(unit_y.mean()), 5)
              power = obs.observation["screen"][_POWER][target[1]][target[0]]
              if power == 1:

                # we have power at the site, build a gateway
                self.gateway_built = True
                return actions.FunctionCall(_BUILD_GATEWAY, [_NOT_QUEUED, target])

    # macro tasks
    if self.state == 'macro':
      print("macroing")
      #  Probes and Pylons
      supply_buffer = obs.observation["player"][_SUPPLY_MAX] - obs.observation["player"][_SUPPLY_USED]

      # build pylons if we have less than 5 supply from supply block
      if supply_buffer > 5:
        if not self.nexus_selected:
          unit_type = obs.observation["screen"][_UNIT_TYPE]
          unit_y, unit_x = (unit_type == _PROTOSS_NEXUS).nonzero()

          target = [int(unit_x.mean()), int(unit_y.mean())]

          self.nexus_selected = True

          return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])
        else:
          print('trying to build a probe')
          if _BUILD_PROBE in obs.observation["available_actions"]:
            self.nexus_selected = False
            return actions.FunctionCall(_BUILD_PROBE, [_QUEUED])
      else:
        if not self.probe_selected:
          unit_type = obs.observation["screen"][_UNIT_TYPE]
          unit_y, unit_x = (unit_type == _PROTOSS_PROBE).nonzero()

          target = [unit_x[0], unit_y[0]]

          self.probe_selected = True

          return actions.FunctionCall(_SELECT_POINT, [_NOT_QUEUED, target])

        elif _BUILD_PYLON in obs.observation["available_actions"]:
          unit_type = obs.observation["screen"][_UNIT_TYPE]
          unit_y, unit_x = (unit_type == _PROTOSS_NEXUS).nonzero()
          x_rand = random.choice(range(-32, 32))
          y_rand = random.choice(range(-32, 32))
          if x_rand <= 0:
            x_rand = 0
          if y_rand <= 0:
            y_rand = 0

          target = self.transformLocation(int(unit_x.mean()), x_rand, int(unit_y.mean()), y_rand)

          self.probe_selected = False
          return actions.FunctionCall(_BUILD_PYLON, [_NOT_QUEUED, target])


      return actions.FunctionCall(_NO_OP, [])

    # micro tasks
    if self.state == 'micro':
      print("microing")
      return actions.FunctionCall(_NO_OP, [])

    return actions.FunctionCall(_NO_OP, [])
