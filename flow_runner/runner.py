from tkinter.constants import E
from .context import Context
from .stack import Stack
from .wrapper import flowoperation

class Runner():
  def __init__(self, operation_loader):
    self.get = operation_loader.get
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
 
  def get_level_stack(self, level=0):
    number_of_levels_in_stacks = len(self.context_stacks)
    if number_of_levels_in_stacks < 1:
      return None
    return self.context_stacks[level]
    
  def stacks_indexes(self):
    number_of_levels_in_stacks = len(self.context_stacks)
    if number_of_levels_in_stacks < 1:
      return None
    indexes = []
    for i in range(0, number_of_levels_in_stacks, 1):
      indexes.append(self.context_stacks[i].size())

    print("indexes", indexes)
    return indexes

  
  def context_stacks_is_empty(self):
    return len(self.context_stacks) == 0

# STEP CONTEXT OPERATIONS
  def store_step_context(self, context):
    stack = self.get_level_stack()
    stack.push(context)
    return

  def step_index(self, level=0):
    step_index = 0
    indexes = self.stacks_indexes()

    if indexes is not None:
      step_index = sum(indexes[0:level+1])
    
    print("step_index", step_index)

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

    return

  def get_last_step_meta(self):
    meta = None
    context = self.get_last_step_context()
    if context is not None:
      meta = context.step_meta
    
    return meta

  def get_last_step_output(self):
    output = None
    context = self.get_last_step_context()
    if context is not None:
      output = context.kwargs_after
    
    return output

  def get_last_step_input(self):
    input = None
    context = self.get_last_step_context()
    if context is not None:
      input = context.kwargs_after
    
    return input

  def is_last_step_exec(self):
    if self.context_stacks_is_empty:
      return True
    return 'exec' in self.get_last_step_meta()

  def is_last_step_statement(self):
    if self.context_stacks_is_empty():
      return True
    return 'stm' in self.get_last_step_meta()


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


  def run_step(self, step_meta):  
    kwargs = self.init_step()
    # Craete the step context with input values 
    step_context = Context(step_meta, **kwargs)
    # load the step's function
    operation = self.get(step_meta['exec'])
    wrapped = flowoperation(operation)
    # Run the exec
    kwargs = wrapped(step_meta, **kwargs)  
    # Set the result to the step context
    step_context.set_after(**kwargs)
    # Store the context
    self.store_step_context(step_context)

    return kwargs['image']
    

  def run_stm(self, step_meta):  
    kwargs = self.init_step(True)
    # Craete the step context with input values 
    step_context = Context(step_meta, **kwargs)
    # load the step's function
    operation = self.get(step_meta['stm'])
    # Run the staement
    kwargs = operation(step_meta, **kwargs)  
    # Set the result to the step context
    step_context.set_after(**kwargs)
    # Store the context
    self.store_step_context(step_context)

    return kwargs['image']



  def continue_to_run(self, max_step):
    if self.context_stacks_is_empty():
      return True
    if self.step_index() >= max_step:
      print("bottom")      
      return False
    return True
    

  def run(self, flow_meta, one = False):
    if not one: 
      self.reset()

    image = None
    steps_meta = flow_meta['steps']    

    while(self.continue_to_run(len(steps_meta))):
      
      step_meta = steps_meta[self.step_index()]

      print("step", step_meta)
      if self.is_step_exec(step_meta) and self.is_last_step_exec():
        image = self.run_step(step_meta)
      elif self.is_step_statement(step_meta) or (self.is_last_step_statement() and self.is_step_exec(step_meta)):
        if self.is_step_statement(step_meta):
          image = self.run_stm(step_meta)
        else:
          image = self.run_step(step_meta)

      if one == True:
        break;

    return self.step_index(), image


# PLAYBACK
  def back(self):
    image = None
    if self.step_index() > 0:
      meta = self.get_last_step_meta()
      print("back", meta)
      image = self.get_last_step_input()['image']
      self.remove_last_step_context()
    else:
      self.top()

    return self.step_index(), image


  def top(self):
    print("top")
    self.reset()

    return
