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
_NOOP = actions.FUNCTIONS.no_op.id
_SELECT_POINT = actions.FUNCTIONS.select_point.id

# Features
_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_UNIT_TYPE = features.SCREEN_FEATURES.unit_type.index

# Unit IDs
_PROTOSS_NEXUS = 59
_PROTOSS_PROBE = 84

# Parameters
_PLAYER_SELF = 1
_NOT_QUEUED = [0]
_QUEUED = [1]




class MineMinerals(base_agent.BaseAgent):
  """An agent specifically for mining up some minerals"""

  base_top_left = None

  # Build order
  pylon_built = False
  probe_selected = False

  def transformLocation(self, x, x_distance, y, y_distance):
      if not self.base_top_left:
          return [x - x_distance, y - y_distance]

      return [x + x_distance, y + y_distance]


  def step(self, obs):
    super(MineMinerals, self).step(obs)

    time.sleep(0.1)

    # Detect upper left
    player_y, player_x = (obs.observation["minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
    self.base_top_left = player_y.mean() <= 31

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

    return actions.FunctionCall(_NO_OP, [])
