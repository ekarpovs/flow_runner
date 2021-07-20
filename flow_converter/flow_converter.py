from .templates import Templates 
from .step_converter import StepConverter

class FlowConverter():
  def __init__(self, meta):
    self.meta = meta
    self.templates = Templates()
    self.step_converter = StepConverter(self.meta)

  def convert(self):
    states_def = []
    first_state_name = None
    for i, _ in enumerate(self.meta):
      state_entry_action = "" 
      state_exit_action = ""

      convert_step_meta = self.step_converter.convert()
      state_name, trans_def = convert_step_meta(i)
      if i == 0:
        first_state_name = state_name
      # TEMPLATE_STATE = ["name", "entry-action", "exit-action", "transitions"]
      state_def = self.templates.def_state([state_name, state_entry_action, state_exit_action, trans_def])
      states_def.append(state_def)
    # TEMPLATE_FSM = ["info", "context-name", "init-action", "first-state", "states"]    
    fsm_def = self.templates.def_fsm(['', '', '', first_state_name, states_def])
    return fsm_def
