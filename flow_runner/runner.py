import json # temporary!!!
from gfsm.fsm import FSM
from frfsm.frfsm import Frfsm
from flow_converter import FlowConverter
from .exec_cntx import Cntx
from .exec_cntx import Stack

class Runner():
  def __init__(self):
    self.fsm = FSM('cntx_test')
    self.engine = None
    # io storage
    # self.execution_stack = Stack()

  # the runner's life cycle
  # converts flow defenition into fsm definition 
  # and create fsm engine  
  def init_fsm_engine(self, fsm_conf, fsm_def):
    self.engine = Frfsm(fsm_conf, fsm_def)
   
  # getters
  def get_number_of_states(self):
    return self.engine.get_number_of_states()

  # runtime
  #  
  def get_step_io(self):
    io = self.fsm.context.get('output')
    return io

  def get_step_id(self):
     return self.fsm.context.get_current_state_id()


  def start(self):
    # start fsm from first state
    stack = Stack()
    self.fsm.context.put('stack', stack)
    self.fsm.start(self.engine.fsm_impl)   
    return

  def init_io(self, cv2image):
    stack = self.fsm.context.get('stack')
    if stack and not stack.isEmpty():
      stack.reset()
    # Create init input object
    io = {}
    io['image'] = cv2image.copy()
    io['orig'] = cv2image.copy()
    # Store it into fsm context object
    self.fsm.context.put('input', io)

  def put_step_meta(self, step_meta):
    self.fsm.context.put('step', step_meta)

  def map_event_name(self, event):
    if event == 'next':
      name = self.fsm.context.get_current_state_name()
      last_stm = self.fsm.context.get('last_stm')
      if last_stm and last_stm['name'] == name and last_stm['params']['end']:
        event = 'next_end'
    self.fsm.context.put('event', event)
    return event

  def dispatch_event(self, event, step_meta=None):
    self.put_step_meta(step_meta)
    event = self.map_event_name(event)
    self.fsm.dispatch(event)
    idx = self.get_step_id()
    io = self.get_step_io()
    return idx, io['image']
