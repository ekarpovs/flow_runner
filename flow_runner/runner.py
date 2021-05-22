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
  def reset(self):
    self.context_stacks.reset()

    return


  def set_input_image(self, cv2image):
    self.cv2image = cv2image

    return


# EXECUTION
  def init_step(self):
    if self.context_stacks.isEmpty():
      self.context_stacks.push(Stack())
      kwargs = {}
      kwargs['orig'] = self.cv2image
      kwargs['image'] = self.cv2image
    else:
      kwargs = self.context_stacks.peek().peek().kwargs_after

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

    # Set result to step context
    step_context.set_after(**kwargs)
    # Store the context
    self.context_stacks.peek().push(step_context)

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
      self.context_stacks.peek().peek().step_meta
      image = self.context_stacks.peek().peek().kwargs_before['image']
      self.context_stacks.peek().pop()
    else:
      self.top()

    return self.step_index(), image


  def top(self):
    print("top")
    self.reset()

    return
