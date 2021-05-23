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

# CONTEXT STACK OPERATIONS
  def reset(self):
    self.context_stacks.reset()

    return

  def setup_new_stack(self):
    self.context_stacks.push(Stack())

    return

  def store_context(self, context):
    self.context_stacks.peek().push(context)

    return

  def get_last_step_context(self):
    return self.context_stacks.peek().peek()

  def get_output_of_last_step(self):
    return self.get_last_step_context().kwargs_after

  def get_input_of_last_step(self):
    return self.get_last_step_context().kwargs_before

  def get_meta_of_last_step(self):
    return self.get_last_step_context().step_meta

  def remove_last_step_context(self):
    self.context_stacks.peek().pop()

    return


# EXECUTION
  def init_step(self):
    if self.context_stacks.isEmpty():
      self.setup_new_stack()
      kwargs = {}
      kwargs['orig'] = self.cv2image
      kwargs['image'] = self.cv2image
    else:
      kwargs = self.get_output_of_last_step()

    return kwargs


  def run_step(self, step_meta):
    kwargs = self.init_step()
    # Craete the step context with input values 
    step_context = Context(step_meta, **kwargs)
    
    # load the step's function
    if 'exec' in step_meta:
      operation = self.get(step_meta['exec'])
      wrapped = flowoperation(operation)
      # Run the exec
      kwargs = wrapped(step_meta, **kwargs)  
    elif 'stm' in step_meta:
      operation = self.get(step_meta['stm'])

    # Set the result to the step context
    step_context.set_after(**kwargs)
    # Store the context
    self.store_context(step_context)

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
      image = self.run_step(step_meta)

      if one == True:
        break;

    return self.step_index(), image


# PLAYBACK
  def back(self):
    image = None
    if self.step_index() > 0:
      meta = self.get_meta_of_last_step()
      print("back", meta)
      image = self.get_input_of_last_step()['image']
      self.remove_last_step_context()
    else:
      self.top()

    return self.step_index(), image


  def top(self):
    print("top")
    self.reset()

    return
