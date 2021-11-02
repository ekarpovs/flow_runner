from typing import List
from flow_model.flowitemmodel import FlowItemModel
from flow_model.flowmodel import FlowModel
from gfsm.fsm import FSM
from frfsm.frfsm import Frfsm

from .storage import Storage

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

  @property
  def step_meta(self):
    self._fsm.get_user_data('step')
    return

  @step_meta.setter
  def step_meta(self, step_meta):
    self._fsm.set_user_data('step', step_meta)
    return

# Methods
  # the runner's life cycle
  # create fsm engine  
  def create_frfsm(self, fsm_conf, fsm_def):
    self._frfsm = Frfsm(fsm_conf, fsm_def)
    self._storage = Storage()
    for state_name in self._frfsm.state_names:
      self._storage.put_state_data(state_name, {'input': None, 'output': None})
    return


  def start(self):
    self._fsm.start(self._frfsm.impl)   
    return


  def init_storage(self, cv2image):
    user_data = {}
    if cv2image is not None:
      user_data['image'] = cv2image.copy()
      # Store it into the fsm context object
      self._fsm.set_user_data('user_data', user_data)
      #  and into the storage
      state_name = self._fsm.current_state_name
      state_data = {}
      state_data['input'] = cv2image.copy()
      # state_data['output'] = cv2image.copy()
      self._storage.put_state_data(state_name, state_data)
    return

  def map_event_name(self, event):
    return event


  def dispatch_event(self, event, flow_item:FlowItemModel):
    if event == 'next':
  	  idx, out_image = self.dispatch_next(flow_item)
    elif event == 'prev':
  	  idx, out_image = self.dispatch_prev(flow_item)
    else:
  	  idx, out_image = self.dispatch_current(flow_item)
    return idx, out_image

  def dispatch_next(self, flow_item: FlowItemModel):
    event = 'next'
    self.step_meta = flow_item
    event = self.map_event_name(event)
    # Prepare input
    state_name = self._fsm.current_state_name
    state_data = self._storage.get_state_data(state_name)
    in_image = state_data.get('input')
    # Store it into fsm context object
    user_data = self._fsm.get_user_data('user_data')
    user_data['image'] = in_image.copy()
    self._fsm.set_user_data('user_data', user_data)

    # Perform the step
    self._fsm.dispatch(event)

    # Get the output
    idx = self.step_id
    user_data = self._fsm.get_user_data('user_data')
    out_image = user_data.get('image')

    # Update new state storage
    state_name = self._fsm.current_state_name
    state_data = self._storage.get_state_data(state_name)
    # Current output will be input for next state
    # state_data['input'] = out_image.copy()
    state_data['input'] = out_image.copy()
    self._storage.put_state_data(state_name, state_data)
    return idx, out_image


  def dispatch_prev(self, flow_item: FlowItemModel):
    event = 'prev'
    source_state_name = self._fsm.current_state_name
    source_state_data = self._storage.get_state_data(source_state_name)

    self._fsm.dispatch(event)

    # Get the output
    idx = self.step_id
    target_state_name = self._fsm.current_state_name
    if source_state_name != source_state_name:
      # Prevent to delete initial storage item
      source_state_data['input'] = None
      source_state_data['output'] = None
      self._storage.put_state_data(source_state_name, source_state_data)
    # Update new state storage
    target_state_data = self._storage.get_state_data(target_state_name)
    out_image = target_state_data['input']
    return idx, out_image


  def dispatch_current(self, flow_item: FlowItemModel):
    event = 'current'
    self.step_meta = flow_item
    # Prepare input
    state_name = self._fsm.current_state_name
    state_data = self._storage.get_state_data(state_name)
    in_image = state_data.get('input')
    # Store it into fsm context object
    user_data = self._fsm.get_user_data('user_data')
    user_data['image'] = in_image.copy()
    self._fsm.set_user_data('user_data', user_data)

    # Perform the step
    self._fsm.dispatch(event)

    # Get the output
    idx = self.step_id
    user_data = self._fsm.get_user_data('user_data')
    out_image = user_data.get('image')

    # Update new state storage
    state_name = self._fsm.current_state_name
    state_data = self._storage.get_state_data(state_name)
    # Current output will be input for next state
    # state_data['input'] = out_image.copy()
    state_data['output'] = out_image.copy()
    self._storage.put_state_data(state_name, state_data)
    return idx, out_image



  def run_step(self, event, flow_item: FlowItemModel):
    idx, cv2image = self.dispatch_event(event, flow_item)
    return idx, cv2image


  def run_all(self, model: List[FlowModel]):
    n = self.number_of_states
    idx = 0
    while (idx < n-1):
      step_meta = model.get_item(idx)
      idx, _ = self.run_step('next', step_meta)
    idx, cv2image = self.run_step('next', step_meta)
    return idx, cv2image
