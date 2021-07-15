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
    # self.execution_stack = Stack()

  # the runner's life cycle
  # converts flow defenition into fsm definition 
  # and create fsm engine  
  def init_fsm_engine(self, fsm_conf, flow_meta):
    fc = FlowConverter(flow_meta)
    fsm_def = fc.convert()
    # with open('../data/fsm-def/edge-fsm.json', 'w') as fp:
    #   json.dump(fsm_def, fp)
    # with open('../data/fsm-def/edge-fsm.json') as F:
    #   fsm_def = json.load(F)
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

  def put_event(self, event, step_meta=None):
    if event == 'next':
      return self.next(step_meta)
    if event == 'prev':
      return self.prev()
    if event == 'current':
      return self.current(step_meta)

  def next(self, step_meta):
    self.put_step_meta(step_meta)
    self.fsm.dispatch('next')
    idx = self.get_step_id()
    io = self.get_step_io()
    return idx, io['image']

  def current(self, step_meta):
    self.put_step_meta(step_meta)
    self.fsm.dispatch('current')
    idx = self.get_step_id()
    io = self.get_step_io()
    return idx, io['image']

  def prev(self):
    self.fsm.dispatch('prev')
    idx = self.get_step_id()
    io = self.get_step_io()
    return idx, io['image']
