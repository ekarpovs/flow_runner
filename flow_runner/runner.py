from tkinter.constants import E, S
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

  def setup_new_stack(self, max_size=200):
    self.context_stacks.append(Stack(max_size))
    return
 
  def get_current_level(self):
    return len(self.context_stacks) - 1

  def context_stacks_is_empty(self):
    return self.get_current_level() == -1

  def get_level_stack(self, level=-1):
    if level == -1:
      level = self.get_current_level()
    if level < 0:
      return None
    return self.context_stacks[level]
       
# STEP CONTEXT OPERATIONS
  def store_step_context(self, context):
    stack = self.get_level_stack()
    stack.push(context)
    return

  def step_indexes(self):
    step_indexes = [0]

    number_of_stacks = len(self.context_stacks)
    if number_of_stacks >= 1:
      indexes = []
      for i in range(0, number_of_stacks, 1):
        indexes.append(self.context_stacks[i].size())

      if indexes is not None:
        step_indexes = [idx for idx in indexes]

    print('step_indexes: {}'.format(step_indexes))
    return step_indexes


# LAST STEP CONTEXT 
  def get_last_step_context(self):
    context = None
    stack = self.get_level_stack()
    if stack is not None and stack.isEmpty() is not True:
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

  def update_last_step_output(self, kwargs):
    level = self.get_current_level()
    if level > 0:
      level -= 1
      stack = self.get_level_stack(level)
      if stack is not None and stack.isEmpty() is not True:
        context = stack.peek()
        if context is not None:
          context.kwargs_after = kwargs   
    return

  def is_last_step_stm(self):
    ret = False
    if self.get_last_step_meta() is not None:
      ret = 'stm' in self.get_last_step_meta()
    return ret


# EXECUTION
  def init_step(self, stm=False, max_size = 200):
    if self.context_stacks_is_empty():
      self.setup_new_stack()
      kwargs = {}
      kwargs['orig'] = self.cv2image
      kwargs['image'] = self.cv2image
    else:
      kwargs = self.get_last_step_output()
      if stm:
        kwargs['idx'] = sum(self.step_indexes())
        kwargs['include'] = max_size
        print("idx {}, include {}".format(kwargs['idx'], kwargs['include']))

        self.setup_new_stack(max_size)

    return kwargs


  def is_step_exec(self, step_meta):
    return 'exec' in step_meta


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
    

  def get_include_value(self, step_meta):
    include = 0
    if 'include' in step_meta:
      include = step_meta['include']
    return include


  def update_step_meta(self, step_meta, **kwargs):
    # Temporary!!!
    # TODO: must find common solution.
    print("kwargs angle", kwargs['angle'])
    step_meta['angle'] = kwargs['angle']
    return step_meta


  def continue_to_run(self, max_step):
    if self.context_stacks_is_empty():
      return True
    step_indexes = sum(self.step_indexes())
    if step_indexes >= max_step:
      print("bottom")      
      return False
    return True
    

  def run(self, flow_meta, one = False):
    if not one: 
      self.reset()

    kwargs = None
    steps_meta = flow_meta['steps']    

    while(self.continue_to_run(len(steps_meta))):     
      step_meta = steps_meta[sum(self.step_indexes())]
      print("step", step_meta)     

      if self.is_step_exec(step_meta):
        # Chek last step type is stm          
        kwargs = self.init_step()
        if self.is_last_step_stm():
          # update the step meta from stm state
          step_meta = self.update_step_meta(step_meta, **kwargs)
        kwargs = self.run_step(step_meta, kwargs, 'exec')
      else:
        # Init statement state
        # Get from the current statement 'include' parameter
        max_size = self.get_include_value(step_meta)
        kwargs = self.init_step(stm=True, max_size=max_size)
        kwargs = self.run_step(step_meta, kwargs, 'stm')
        # Reset the stm input for the future usage
        self.update_last_step_output(kwargs)

      # Check stack level and the stack overflow for level > 0
      stack = self.get_level_stack()
      if stack is not None and stack.isFull():
        print("stack for level {} is full".format(self.get_current_level()))
        # change step number regarding current statment type and its 'include' parameter
        if  kwargs['end'] is not True:
          # move the last step state to the above statement 
          self.context_stacks.pop()

      if one == True:
        break;
      
    return self.step_indexes(), kwargs


# PLAYBACK
  def back(self):
    kwargs = None
    if self.step_indexes()[self.get_current_level()] > 0:
      meta = self.get_last_step_meta()
      print("back", meta)
      kwargs = self.get_last_step_input()
      self.remove_last_step_context()
    else:
      self.top()

    return self.step_indexes(), kwargs


  def top(self):
    print("top")
    self.reset()

    return
