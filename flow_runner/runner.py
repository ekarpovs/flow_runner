from tkinter.constants import E
from .context import Context
from .stack import Stack
from .wrapper import flowoperation

class Runner():
  def __init__(self, operation_loader):
    self.get_operation = operation_loader.get
    self.cv2image = None
    self.context_stacks = []


# INITIALIZATION 
  def set_input_image(self, cv2image):
    self.cv2image = cv2image

    return

# CONTEXT STACKS OPERATIONS
  def reset(self):
    self.context_stacks = []

    return

  def setup_new_stack(self):
    self.context_stacks.append(Stack())
    return
 
  def get_current_level(self):
    return len(self.context_stacks) - 1

  def context_stacks_is_empty(self):
    return self.get_current_level() == -1

  def get_level_stack(self):
    level = self.get_current_level()
    if level < 0:
      return None
    return self.context_stacks[level]
       
# STEP CONTEXT OPERATIONS
  def store_step_context(self, context):
    stack = self.get_level_stack()
    stack.push(context)
    return

  def step_index(self):
    step_index = [0]

    number_of_stacks = len(self.context_stacks)
    if number_of_stacks >= 1:
      indexes = []
      for i in range(0, number_of_stacks, 1):
        indexes.append(self.context_stacks[i].size())

      if indexes is not None:
        step_index = [idx for idx in indexes]

    print('step_index: {}'.format(step_index))
    return step_index


# LAST STEP CONTEXT 
  def get_last_step_context(self):
    context = None
    stack = self.get_level_stack()
    if stack is not None:
      context = stack.peek()

    return context

  def remove_last_step_context(self):
    stack = self.get_level_stack() 
    if stack is not None:
      stack.pop()
      # remove empty stack from the stacks list
      if stack.isEmpty():
        self.context_stacks.pop()

    return

  def get_last_step_meta(self):
    meta = None
    context = self.get_last_step_context()
    if context is not None:
      meta = context.step_meta
    
    return meta

  def get_last_step_input(self):
    input = None
    context = self.get_last_step_context()
    if context is not None:
      input = context.kwargs_after
    
    return input

  def get_last_step_output(self):
    output = None
    context = self.get_last_step_context()
    if context is not None:
      output = context.kwargs_after
    
    return output


# EXECUTION
  def init_step(self, stm=False):
    if self.context_stacks_is_empty():
      self.setup_new_stack()
      kwargs = {}
      kwargs['orig'] = self.cv2image
      kwargs['image'] = self.cv2image
    else:
      kwargs = self.get_last_step_output()
      if stm:
        self.setup_new_stack()

    return kwargs


  def is_step_exec(self, step_meta):
    return 'exec' in step_meta

  def is_step_statement(self, step_meta):
    return 'stm' in step_meta

  

  def run_step(self, step_meta, kwargs, type):  
    # Craete the step context with input values 
    step_context = Context(step_meta, **kwargs)
    # load the step's function
    operation = self.get_operation(step_meta[type])
    wrapped = flowoperation(operation)
    # Run the exec
    kwargs = wrapped(step_meta, **kwargs)  
    # Set the result to the step context
    step_context.set_after(**kwargs)
    # Store the context
    self.store_step_context(step_context)

    return kwargs
    

  def continue_to_run(self, max_step):
    if self.context_stacks_is_empty():
      return True
    global_step_index = sum(self.step_index())
    if global_step_index >= max_step:
      print("bottom")      
      return False
    return True
    

  def run(self, flow_meta, one = False):
    if not one: 
      self.reset()

    kwargs = None
    steps_meta = flow_meta['steps']    

    while(self.continue_to_run(len(steps_meta))):
      
      step_meta = steps_meta[sum(self.step_index())]
      print("step", step_meta)
      
      is_exec = self.is_step_exec(step_meta)
      kwargs = self.init_step(not is_exec)

      type = 'exec'
      if not is_exec:
        type = 'stm'
      kwargs = self.run_step(step_meta, kwargs, type)

      if one == True:
        break;

    image = None
    if kwargs is not None:
      image = kwargs['image']

    return sum(self.step_index()), image


# PLAYBACK
  def back(self):
    image = None
    if self.step_index()[self.get_current_level()] > 0:
      meta = self.get_last_step_meta()
      print("back", meta)
      image = self.get_last_step_input()['image']
      self.remove_last_step_context()
    else:
      self.top()

    return self.step_index()[self.get_current_level()], image


  def top(self):
    print("top")
    self.reset()

    return
