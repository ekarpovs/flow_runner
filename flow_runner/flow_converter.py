import copy
from enum import Enum


class Offset(Enum):
  NO = 0
  FORWARD = 1
  REARWARD = -1

class FlowConverter():
  def __init__(self, meta):
    self.meta = meta
    # Predefine transitions
    # TEMPLATE_TRANSITION = ["name", "src", "event", "target", "action", "start-action", "end-action"]
    self.state_transitions = [
      [
        self.def_transition(["", "", "next", "", "", "", ""]),
        self.def_transition(["", "", "current", "", "", "", ""])
      ],
      [
        self.def_transition(["", "", "next", "", "", "", "____frfsm-actions.last_state_executed"]),
        self.def_transition(["", "", "current", "", "", "", ""]),
        self.def_transition(["", "", "prev", "", "", "", "____frfsm-actions.last_state_not_executed"]),
      ],       
      [
        self.def_transition(["", "", "next", "", "", "", ""]),
        self.def_transition(["", "", "current", "", "", "", ""]),
        self.def_transition(["", "", "prev", "", "", "", ""]),
      ]
    ]

# Utilites
  @staticmethod
  def inst_template(keys, values):
    return dict(zip(keys, values))

  def def_fsm(self, values):
    TEMPLATE_FSM = ["info", "context-name", "init-action", "first-state", "states"]    
    return self.inst_template(TEMPLATE_FSM, values)

  def def_state(self, values):
    TEMPLATE_STATE = ["name", "entry-action", "exit-action", "transitions"]
    return self.inst_template(TEMPLATE_STATE, values)

  def def_transition(self, values):
    TEMPLATE_TRANSITION = ["name", "src", "event", "target", "action", "start-action", "end-action"]
    return self.inst_template(TEMPLATE_TRANSITION, values)
 
# Runtime
  @staticmethod
  def parse_step_meta(meta, idx):
    def split_exec_name(meta, idx, offset=Offset['NO']):
      exec_name = [meta[idx+int(offset.value)]['exec']]
      return "{}-{}".format(idx+int(offset.value), exec_name[0].split('.')[1]), exec_name[0]

    def get(state_transitions):
      state_name, act_name = split_exec_name(meta, idx)
      trans_def = copy.deepcopy(state_transitions)
      for n, tr in enumerate(trans_def):
        tr['name'] = 'tr' + str(idx) + str(n) 
        tr['src'] = state_name
        event_name = trans_def[n]['event'] 
        if event_name == 'next':
          if idx < len(meta)-1:
            tr['target'], _ = split_exec_name(meta, idx, Offset['FORWARD'])
          else:
            tr['target'] = state_name
          tr['action'] = act_name
        elif event_name == 'prev':
          tr['target'], _ = split_exec_name(meta, idx, Offset['REARWARD'])
        else:
          tr['action'] = act_name
          tr['target'] = state_name
      return state_name, trans_def
    return get    

  def convert(self):
    meta = self.meta
    state_transitions = self.state_transitions

    states_def = []
    first_state_name = None
    for i, _ in enumerate(meta):
      state_entry_action = '' 
      state_exit_action = ''
      parser = self.parse_step_meta(meta, i)
      if i == 0:
        state_name, trans_def = parser(state_transitions[0])
        state_entry_action = '____frfsm-actions.reset_context' 
        first_state_name = state_name
      elif i == len(meta)-1:
        state_name, trans_def = parser(state_transitions[1])
      else:
        state_name, trans_def = parser(state_transitions[2])
      # TEMPLATE_STATE = ["name", "entry-action", "exit-action", "transitions"]
      state_def = self.def_state([state_name, state_entry_action, state_exit_action, trans_def])
      states_def.append(state_def)
    # TEMPLATE_FSM = ["info", "context-name", "init-action", "first-state", "states"]    
    fsm_def = self.def_fsm(['', '', '', first_state_name, states_def])
    return fsm_def
