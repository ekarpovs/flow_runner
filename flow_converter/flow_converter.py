from .templates import Templates 
from .step_converter import StepConverter

class FlowConverter():
  def __init__(self, meta):
    self.meta = meta
    self.templates = Templates()
    self.step_converter = StepConverter(self.meta)

  def meta_to_fsm_def(self):
    states_def = []
    first_state_name = None
    for i, _ in enumerate(self.meta):
      state_entry_action = "" 
      state_exit_action = ""
      convert_step_meta = self.step_converter.convert()
      state_name, trans_def, state_entry_action, state_exit_action = convert_step_meta(i)
      if i == 0:
        first_state_name = state_name
      # TEMPLATE_STATE = ["name", "entry-action", "exit-action", "transitions"]
      state_def = self.templates.def_state([state_name, state_entry_action, state_exit_action, trans_def])
      states_def.append(state_def)
    # Decorate states by stm elements
    if self.meta_has_statement():
      states_def = self.decorate(states_def)
    # TEMPLATE_FSM = ["info", "context-name", "init-action", "first-state", "states"]    
    fsm_def = self.templates.def_fsm(['', '', '', first_state_name, states_def])
    return fsm_def

  def convert(self):
    fsm_def = self.meta_to_fsm_def()
    return fsm_def

  def meta_has_statement(self):
    return 'stm' in {k for m in self.meta for k in m.keys()}

  def state_is_statement(self, state_def):
    stm_name = state_def.get('name').split('-')[1]
    return stm_name == 'forinrangestm' or stm_name == 'whilestm'
    
  def decorate(self, states_def):
    for idx, state_def in enumerate(states_def):
      if self.state_is_statement(state_def):
        state_name = state_def.get('name') 
        stm_name = state_name.split('-')[1]
        if stm_name == 'forinrangestm':
          state_def['exit-action'] = '____frfsm-actions.forinrange_exit'
        if stm_name == 'whilestm':
          state_def['exit-action'] = '____frfsm-actions.while_exit'
        next_state_def = states_def[idx+1]
        next_state_def['exit-action'] = '____frfsm-actions.stm_included'
        # Change the last state in the stm transition destination
        step_meta = self.meta[idx]
        include = step_meta.get('params').get('include')
        last_state_def_inside_stm = states_def[idx+include]
        transitions_def = last_state_def_inside_stm.get('transitions')
        for tr in transitions_def:
          if tr['event'] == 'next':
            tr['target'] = state_name
    return states_def