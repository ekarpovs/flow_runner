from typing import Dict, Tuple

from flow_storage import FlowStorage, FlowStorageConfig
from gfsm.fsm import FSM
from gfsm.context import Context
from flow_model import FlowModel, FlowItemModel
from flow_converter import FlowConverter
from gfsm.fsm_builder.fsm_builder import FsmBuilder


class Runner():
  def __init__(self):
    self._storage: FlowStorage = None
    self._model: FlowModel = None
    self._fsm_impl = None
    self._context = None
    self._first_state_name = ''
    self._output_from_state = None
    return

  # Properties
  @property
  def storage(self) -> FlowStorage:
    return self._storage

  @property
  def initialized(self) -> bool:
    return self._fsm_impl is not None

  # Runtime
  @property
  def state_idx(self) -> int:
     parts = self._context.current_state_name.split('-')
     return int(parts[0])

  @property
  def state_id(self) -> int:
     return self._context.current_state_name

  @property
  def output_from_state(self) -> str:
    return self._output_from_state

  @output_from_state.setter
  def output_from_state(self, value: str) -> None:
    self._output_from_state = value
    return

  # Methods
  # the runner's life cycle
  def build(self, cfg_fsm: Dict, model: FlowModel) -> None:
    if self.storage is not None:
      self.storage.close()
    self._model = model
    cfg = FlowStorageConfig(cfg_fsm.get('storage'))
    self._storage = FlowStorage(cfg, model.get_as_ws())
    flow_converter = FlowConverter(model)
    fsm_def = flow_converter.convert()
    self._create_fsm(cfg_fsm, fsm_def)
    return

  def reset(self) -> None:
    self._storage.reset()
    self._context.current_state_name = self._first_state_name
    self._start()
    return

  # create FSM
  def _create_fsm(self, fsm_conf: Dict, fsm_def: Dict) -> None:
    fsm_builder = FsmBuilder(fsm_conf, fsm_def)
    self._fsm_impl = FSM(fsm_builder)
    self._context = Context('wf-runner')
    self._first_state_name = fsm_builder.first_state_name
    self._context.current_state_name = self._first_state_name
    return

  def _start(self) -> None:
    self._fsm_impl.start()
    return

  # Execute requests
  def run_all(self) -> None:
    n = self._fsm_impl.number_of_states
    last_sate_id = self._fsm_impl.state_names[n - 1]
    while (self.state_id != last_sate_id):
      self.run_step('next', self.state_idx)
    return

  def run_step(self, event, idx: int):
    flow_item = self._model.get_item(idx)
    if event == 'next':
      return self._next(flow_item)
    if event == 'prev':
      return self._prev(flow_item)
    return self._current(flow_item)

  @staticmethod
  def _init_stm_context() -> Dict:
    execution_context = {}
    execution_context['init'] = True
    execution_context['result'] = True
    return execution_context

  def _restore_stm_context(self,
                           state_id: str,
                           data: Dict) -> Tuple[str, Dict]:
    event = 'next'
    cache = self.storage.get_state_cache_data(state_id)
    execution_context = cache.get('stmselfcache')
    if execution_context is None:
      execution_context = self._init_stm_context()
    else:
      result = execution_context.get('result')
      if not result:
        execution_context = self._init_stm_context()
        event = 'end_stm'
    data['executioncontext'] = execution_context
    return event, data

  def _store_stm_context(self, state_id: str, data: Dict) -> Dict:
    execution_context = data.get('executioncontext')
    cache = {}
    cache['stmselfcache'] = execution_context
    self.storage.set_state_cache_data(state_id, cache)
    del data['executioncontext']
    return data

  def _next(self, flow_item: FlowItemModel) -> None:
    if self.state_idx == self._fsm_impl.number_of_states - 1:
      return
    self._context.set_user_data("params", flow_item.params)
    data = self.storage.get_state_input_data(self.state_id)
    event = 'next'
    name = flow_item.name
    if (name == 'glbstm.for_begin' or name == 'glbstm.while_begin'):
      event, data = self._restore_stm_context(self.state_id, data)
    if(name == 'glbstm.for_end' or name == 'glbstm.while_end'):
      event = 'begin_stm'

    # Remember current state for future usage
    state_id = self.state_id
    self._context.set_user_data("data", data)
    # Perform the step
    self._fsm_impl.dispatch(event, self._context)

    data = self._context.get_user_data("data")
    if (name == 'glbstm.for_begin' or name == 'glbstm.while_begin'):
      data = self._store_stm_context(state_id, data)
    self.storage.set_state_output_data(state_id, data)
    self.output_from_state = state_id
    return

  def _prev(self, flow_item: FlowItemModel):
    self.storage.clean_state_output_data(self.state_id)
    event = 'prev'
    name = flow_item.name
    if (name == 'glbstm.if_end' or
        name == 'glbstm.while_end' or
        name == 'glbstm.for_end'):
      event = 'begin_stm'
    self._fsm_impl.dispatch(event, self._context)
    self.output_from_state = self.state_id
    return

  def _current(self, flow_item: FlowItemModel):
    event = 'current'
    self._context.set_user_data("params", flow_item.params)
    data = self.storage.get_state_input_data(self.state_id)
    self._context.set_user_data("data", data)

    # Perform the step
    self._fsm_impl.dispatch(event, self._context)

    # Strore output data of the state
    data = self._context.get_user_data("data")
    self.storage.set_state_output_data(self.state_id, data)
    self.output_from_state = self.state_id
    return
