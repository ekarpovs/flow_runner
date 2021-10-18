from gfsm.fsm_builder.fsm_builder import FsmBuilder

class Frfsm():
  def __init__(self, fsm_conf, fsm_def):
    fsm_builder = FsmBuilder(fsm_conf, fsm_def)
    self._fsm_impl = fsm_builder.build()

  @property
  def impl(self):
    return self._fsm_impl

  @property
  def state_names(self):
    return self._fsm_impl.get('states').keys()

  @property
  def number_of_states(self):
    return len(self._fsm_impl.get('states', 0))