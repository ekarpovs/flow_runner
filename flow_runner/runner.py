import json # temporary!!!
from gfsm.fsm import FSM
from frfsm.frfsm import Frfsm
from .flow_converter import FlowConverter
from .exec_cntx import Cntx
from .exec_cntx import Stack

class Runner():
  def __init__(self):
    self.fsm = FSM('cntx_test')
    self.engine = None
    # io storage
    self.execution_stack = Stack()

  # the runner's life cycle
  # converts flow defenition into fsm definition 
  # and create fsm engine  
  def init_fsm_engine(self, fsm_conf, flow_meta):
    fc = FlowConverter(flow_meta)
    fsm_def = fc.convert()
    self.engine = Frfsm(fsm_conf, fsm_def)
   
  # getters
  def get_number_of_states(self):
    return self.engine.get_number_of_states()


  # runtime
  #  
  def start(self, cv2image):
    # Reset io storage
    self.execution_stack.reset()
    # Init io storage for first state
    kwargs = {}
    kwargs['image'] = None 
    kwargs['orig'] = None
    if cv2image is not None:
      kwargs['image'] = cv2image.copy()
      kwargs['orig'] = cv2image.copy()

    cntx = Cntx()
    cntx.set_kwargs(kwargs)
    self.execution_stack.push(cntx)
    # start fsm from first state
    self.fsm.start(self.engine.fsm_impl)   
    return

  def put_event(self, event, step_meta=None):
    if event == 'next':
      return self.next(step_meta)
    if event == 'prev':
      return self.prev()
    if event == 'current':
      return self.current(step_meta)

  def next(self, step_meta):
    # get data from previous step
    cntx = self.execution_stack.peek()
    kwargs = cntx.get_kwargs()
    if self.fsm.context.get('last-state-executed'):
      idx = self.fsm.context.get_current_state_id()
      return idx, kwargs['image']

    # set the 
    self.fsm.context.put('step', step_meta)
    self.fsm.context.put('kwargs', kwargs)

    self.fsm.dispatch('next')

    idx = self.fsm.context.get_current_state_id()
    kwargs = self.fsm.context.get('kwargs')
    cntx = Cntx()
    cntx.set_kwargs(kwargs)
    self.execution_stack.push(cntx)
    return idx, kwargs['image']

  def current(self, step_meta):
    # get data from previous step
    cntx = self.execution_stack.peek()
    kwargs = cntx.get_kwargs()
    # set the 
    self.fsm.context.put('step', step_meta)
    self.fsm.context.put('kwargs', kwargs)

    self.fsm.dispatch('current')

    kwargs = self.fsm.context.get('kwargs')
    idx = self.fsm.context.get_current_state_id()

    return idx, kwargs['image']


  def prev(self):
    if self.execution_stack.isEmpty():
      return 0, None
    cntx = self.execution_stack.pop()
    kwargs = cntx.get_kwargs()
    self.fsm.dispatch('prev')   
    idx = self.fsm.context.get_current_state_id()

    if not self.execution_stack.isEmpty():
      cntx = self.execution_stack.peek()
      kwargs = cntx.get_kwargs()
    else:
      kwargs['image'] = None
    return idx, kwargs['image']
