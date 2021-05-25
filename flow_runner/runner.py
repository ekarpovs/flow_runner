from tkinter.constants import E
from .context import Context
from .stack import Stack
from .wrapper import flowoperation

class Runner():
  def __init__(self, operation_loader):
    self.get = operation_loader.get
    self.cv2image = None
    self.context_stacks = Stack()


# INITIALIZATION 
  def set_input_image(self, cv2image):
    self.cv2image = cv2image

    return

# CONTEXT STACKS OPERATIONS
  def reset(self):
    self.context_stacks.reset()

    return

  def setup_new_stack(self):
    self.context_stacks.push(Stack())
    return

  def get_last_stack(self):
    number_of_levels_in_stacks = self.context_stacks.size()
    if number_of_levels_in_stacks <= 0:
      return None
    for level in range(number_of_levels_in_stacks, 1, -1):
      self.context_stacks.peek()
    return self.context_stacks.peek()
  


# STEP CONTEXT OPERATIONS
  def store_step_context(self, context):
    stack = self.get_last_stack()
    stack.push(context)
    return

  def get_last_step_context(self):
    return self.get_last_stack().peek()

  def remove_last_step_context(self):
    self.get_last_stack().pop()
    return

  def get_last_step_meta(self):
    return self.get_last_step_context().step_meta

  def get_last_step_output(self):
    return self.get_last_step_context().kwargs_after

  def get_last_step_input(self):
    return self.get_last_step_context().kwargs_before

  def is_last_step_exec(self):
    if self.context_stacks.isEmpty():
      return True
    return 'exec' in self.get_last_step_meta()

  def is_last_step_statement(self):
    if self.context_stacks.isEmpty():
      return True
    return 'stm' in self.get_last_step_meta()


# EXECUTION
  def init_step(self):
    if self.context_stacks.isEmpty():
      self.setup_new_stack()
      kwargs = {}
      kwargs['orig'] = self.cv2image
      kwargs['image'] = self.cv2image
    else:
      kwargs = self.get_last_step_output()

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
    

  def step_index(self):  
    step_index = 0
    if not self.context_stacks.isEmpty():
      step_index = self.context_stacks.peek().size()

    return step_index


  def continue_to_run(self, max_step):
    if self.context_stacks.isEmpty():
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
          kwargs = self.get_last_step_input()
          self.setup_new_stack()
          # Craete the step context with input values 
          step_context = Context(step_meta, **kwargs)
          # operation = self.get(step_meta['stm'])
          # Set the result to the step context
          step_context.set_after(**kwargs)
          # Store the context
          self.store_step_context(step_context)
        else:
          # operation = self.get(step_meta['exec'])
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
