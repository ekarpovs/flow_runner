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
    self._output_from_state = None
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

  @property
  def state_id(self) -> int:
     return self._fsm.current_state_name

  @property
  def output_from_state(self) -> str:
    return self._output_from_state

  @output_from_state.setter
  def output_from_state(self, value: str) -> None:
    self._output_from_state = value
    return


# Methods
  # the runner's life cycle
  # create fsm context  
  def create_frfsm(self, fsm_conf: Dict, fsm_def: Dict) -> None:
    self._frfsm = Frfsm(fsm_conf, fsm_def)
    return

  def start(self) -> None:
    self._fsm.start(self._frfsm.impl)   
    self.output_from_state = self._fsm.current_state_name
    return

  def run_all(self, model: FlowModel) -> None:
    n = self._frfsm.number_of_states
    idx = self.state_idx
    while (idx <= n-2):
      flow_item = model.get_item(idx)
      idx = idx+1
      self.run_step('next', flow_item)
    return

  def run_step(self, event, flow_item: FlowItemModel):
    self._dispatch_event(event, flow_item)
    return

  def _map_event_name(self, event: str) -> str:
    return event

  def _dispatch_event(self, event, flow_item:FlowItemModel) -> None:
    if event == 'next':
      return self._dispatch_next(flow_item)
    if event == 'prev':
      return self._dispatch_prev(flow_item)
    return self._dispatch_current(flow_item)
    

  def _dispatch_next(self, flow_item: FlowItemModel) -> None:
    if self.state_idx == self._frfsm.number_of_states-1:
      return
    event = 'next'
    event = self._map_event_name(event)
    self._fsm.set_user_data("params", flow_item.params)
    state_id = self.state_id
    self.output_from_state = state_id
    data = self.storage.get_state_input_data(state_id, flow_item.aliases)
    self._fsm.set_user_data("data", data)

    # Perform the step
    self._fsm.dispatch(event)

    data = self._fsm.get_user_data("data")
    self.storage.set_state_output_data(state_id, data)
    out_refs = self.storage.get_state_output_refs(state_id)
    # Update external input references of the current state 
    self.storage.set_state_input_refs(self.state_id, out_refs)
    return

  def _dispatch_prev(self, flow_item: FlowItemModel):
    event = 'prev'
    self.storage.clean_state_output_data(self.state_id)
    self._fsm.dispatch(event)
    self.output_from_state = self.state_id
    return

  def _dispatch_current(self, flow_item: FlowItemModel):
    event = 'current'
    self._fsm.set_user_data("params", flow_item.params)
    data = self.storage.get_state_input_data(self.state_id, flow_item.aliases)
    self._fsm.set_user_data("data", data)

    # Perform the step
    self._fsm.dispatch(event)

    # Strore output data of the state
    data = self._fsm.get_user_data("data")
    self.storage.set_state_output_data(self.state_id, data)
    self.output_from_state = self.state_id
    return
