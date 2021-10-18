from gfsm.fsm import FSM
from frfsm.frfsm import Frfsm

from .exec_cntx import Storage
from .exec_cntx import StateContext

class Runner():
  def __init__(self):
    self._fsm = FSM('cntx_test')
    self._frfsm: Frfsm = None
    self._storage = None

    return

# Properties
  @property
  def frfrsm(self):
    return self._frfsm

  @property
  def number_of_states(self):
    return self._frfsm.number_of_states

  @property
  def initialized(self):
    return self._frfsm is not None

  # runtime
  #  
  @property
  def step_id(self):
     return self._fsm.current_state_id

  # @property
  # def step_out_image(self):
  #   io = self._fsm.context.get('io')
  #   out_image = io.get('output')
  #   return out_image


  @property
  def step_meta(self, step_meta):
    self._fsm.context.get_user_data('step')
    return

  @step_meta.setter
  def step_meta(self, step_meta):
    self._fsm.context.set_user_data('step', step_meta)
    return

# Methods
  # the runner's life cycle
  # create fsm engine  
  def create_frfsm(self, fsm_conf, fsm_def):
    self._frfsm = Frfsm(fsm_conf, fsm_def)
    self._storage = Storage()
    for name in self._frfsm.state_names:
      self._storage.put_item(name, StateContext())
    return


  def start(self):
    self._fsm.start(self._frfsm)   
    return


  def init_io(self, cv2image):
    io = {}
    if cv2image is not None:
      io['input'] = cv2image.copy()
      # Store it into fsm context object
      self._fsm.context.set_user_data('io', io)
      #  and into storage
      state_name = self._fsm.context.current_state_name
      item = self._storage.get_item(state_name)
      item.input_ = cv2image.copy()
      item.output_ = cv2image.copy()
      self._storage.put_item(state_name, item)
    return

  def map_event_name(self, event):
    return event


  def dispatch_event(self, event, step_meta=None):
    self.step_meta = step_meta
    event = self.map_event_name(event)
    # Prepare input
    state_name = self._fsm.context.current_state_name
    item = self._storage.get_item(state_name)
    # Previous output will be input for the current state
    in_image = item.output_
    io = self._fsm.context.get_user_data('io')
    io['input'] = in_image.copy()
    # Store it into fsm context object
    self._fsm.context.set_user_data('io', io)

    # Perform the step
    self._fsm.dispatch(event)

    # Get output
    idx = self.step_id
    io = self._fsm.context.get_user_data('io')
    out_image = io.get('output')
    # Update storage
    state_name = self._fsm.context.current_state_name
    item = self._storage.get_item(state_name)
    # Current output will be input for next state
    item.input_ = out_image.copy()
    self._storage.put_item(state_name, item)
    return idx, out_image


  def run_step(self, event, step_meta):
    idx, cv2image = self.dispatch_event(event, step_meta)
    return idx, cv2image


  def run_all(self, flow_meta):
    n = self.number_of_states
    idx = 0
    while (idx < n-1):
      step_meta = flow_meta[idx]
      idx, _ = self.run_step('next', step_meta)
    idx, cv2image = self.run_step('next', step_meta)
    return idx, cv2image
