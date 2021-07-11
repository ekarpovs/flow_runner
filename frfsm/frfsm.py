from gfsm.fsm import FSM
from gfsm.fsm_builder.fsm_builder import FsmBuilder

class Frfsm():
  def __init__(self, fsm_conf, fsm_def):
    fsm_builder = FsmBuilder(fsm_conf, fsm_def)
    self.fsm_impl = fsm_builder.build()

  def get_number_of_states(self):
    return len(self.fsm_impl['states'])