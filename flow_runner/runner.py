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

  def _dispatch_event(self, event, flow_item:FlowItemModel) -> None:
    if event == 'next':
      if flow_item.name == 'glbstm.for_begin':
        data = self.storage.get_state_input_data(self.state_id)
        execution_context = data.get('executioncontext')
        if execution_context is not None:
          execution_context = json.loads(execution_context)
          result = execution_context.get('result')
          if not result:
            execution_context['current'] = -1
            execution_context['result'] = True
            data['executioncontext'] = execution_context
            event = 'end_stm'
            self._fsm.set_user_data("data", data)

            state_id = self.state_id
            self._fsm.dispatch(event)
            self.storage.set_state_output_data(state_id, data)
            self.output_from_state = state_id
            return
        else:
          # Assing pseudo link - link from the state's output to the state's input
          parts = self.state_id.split('-')
          idx = parts[0]
          exec = parts[1]
          refs = self.storage.get_state_input_refs(self.state_id)
          for ref in refs:
              ref.ext_ref = f'{idx}-glbstm.{exec}-executioncontext'
      if flow_item.name == 'glbstm.for_end':
        event = 'begin_stm'
      return self._dispatch_next(flow_item, event)
    if event == 'prev':
      if flow_item.name == 'glbstm.if_end' or flow_item.name == 'glbstm.while_end' or flow_item.name == 'glbstm.for_end':
        event = 'begin_stm'
      return self._dispatch_prev(flow_item, event)
    return self._dispatch_current(flow_item)
    

  def _dispatch_next(self, flow_item: FlowItemModel, event = 'next') -> None:
    if self.state_idx == self._frfsm.number_of_states-1:
      return
    self._fsm.set_user_data("params", flow_item.params)
    data = self.storage.get_state_input_data(self.state_id)
    self._fsm.set_user_data("data", data)
    
    # Remember current state for forward usage
    state_id = self.state_id
    # Perform the step
    self._fsm.dispatch(event)

    data = self._fsm.get_user_data("data")
    self.storage.set_state_output_data(state_id, data)
    self.output_from_state = state_id
    return

  def _dispatch_prev(self, flow_item: FlowItemModel, event = 'prev'):
    self.storage.clean_state_output_data(self.state_id)
    self._fsm.dispatch(event)
    self.output_from_state = self.state_id
    return

  def _dispatch_current(self, flow_item: FlowItemModel):
    event = 'current'
    self._fsm.set_user_data("params", flow_item.params)
    data = self.storage.get_state_input_data(self.state_id)
    self._fsm.set_user_data("data", data)

    # Perform the step
    self._fsm.dispatch(event)

    # Strore output data of the state
    data = self._fsm.get_user_data("data")
    self.storage.set_state_output_data(self.state_id, data)
    self.output_from_state = self.state_id
    return
