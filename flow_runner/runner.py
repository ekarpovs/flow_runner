from typing import Dict, List
from flow_storage import FlowStorage
from gfsm.fsm import FSM
from frfsm.frfsm import Frfsm
from flow_model import FlowModel, FlowItemModel

class Runner():
  def __init__(self):
    self._storage: FlowStorage = None
    self._fsm = FSM('cntx_test')
    self._frfsm: Frfsm = None
    return

# Properties
  @property
  def storage(self) -> FlowStorage:
    return self._storage
  
  @storage.setter
  def storage(self, storage: FlowStorage) -> None:
    self._storage = storage

  @property
  def initialized(self) -> bool:
    return self._frfsm is not None

  # runtime
  #  
  @property
  def state_idx(self) -> int:
     return self._fsm.current_state_id

# Methods
  # the runner's life cycle
  # create fsm context  
  def create_frfsm(self, fsm_conf: Dict, fsm_def: Dict) -> None:
    self._frfsm = Frfsm(fsm_conf, fsm_def)
    return

  def start(self) -> None:
    self._fsm.start(self._frfsm.impl)   
    return

  def run_all(self, model: FlowModel) -> None:
    n = self._frfsm.number_of_states
    idx = 0
    while (idx <= n-1):
      flow_item = model.get_item(idx)
      idx = idx+1
      self.run_step('next', flow_item)
    return

  def run_step(self, event, flow_item: FlowItemModel):
    self._dispatch_event(event, flow_item)
    return

  def _map_event_name(self, event: str) -> str:
    return event

  def _dispatch_event(self, event, flow_item:FlowItemModel):
    if event == 'next':
  	  self._dispatch_next(flow_item)
    elif event == 'prev':
  	  self._dispatch_prev(flow_item)
    else:
  	  self._dispatch_current(flow_item)
    return

  def _dispatch_next(self, flow_item: FlowItemModel) -> None:
    event = 'next'
    event = self._map_event_name(event)
    self._fsm.set_user_data("params", flow_item.params)
    state_id = self._fsm.current_state_name
    data = self.storage.get_state_input_data(state_id)
    self._fsm.set_user_data("data", data)

    # Perform the step
    self._fsm.dispatch(event)

    # Strore output data of the previous state
    data = self._fsm.get_user_data("data")
    self.storage.set_state_output_data(state_id, data)
    out_refs = self.storage.get_state_output_refs(state_id)
    # Update external input references of the current state 
    state_id = self._fsm.current_state_name
    self.storage.set_state_input_refs(state_id, out_refs)
    return

  def _dispatch_prev(self, flow_item: FlowItemModel):
    event = 'prev'
    state_id = self._fsm.current_state_name
    self.storage.clean_state_output_data(state_id)
    self._fsm.dispatch(event)
    return

  def _dispatch_current(self, flow_item: FlowItemModel):
    event = 'current'
    self._fsm.set_user_data("params", flow_item.params)
    state_id = self._fsm.current_state_name
    data = self.storage.get_state_input_data(state_id)
    self._fsm.set_user_data("data", data)

    # Perform the step
    self._fsm.dispatch(event)

    # Strore output data of the state
    data = self._fsm.get_user_data("data")
    self.storage.set_state_output_data(state_id, data)
    return
