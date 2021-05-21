from tkinter.constants import E
from .context import Context
from .stack import Stack
from .wrapper import flowoperation

class Runner():
  def __init__(self, operation_loader):
    self.get = operation_loader.get
    self.cv2image = None
    self.context_stack = Stack()
    self.step_index = 0


# INITIALIZATION 
  def reset(self):
    self.context_stack.reset()
    self.step_index = 0

    return

  def set_input_image(self, cv2image):
    self.cv2image = cv2image

    return


# EXECUTION
  def init_step(self):
    if self.context_stack.isEmpty():
      # self.state.reset()
      kwargs = {}
      kwargs['orig'] = self.cv2image
      kwargs['image'] = self.cv2image
    else:
      kwargs = self.context_stack.peek().kwargs_after

    return kwargs


  def run_step(self, steps_meta):
    kwargs = self.init_step()
    # Craete the step context with input values 
    step_context = Context(steps_meta, **kwargs)
    # load the step's function
    if 'exec' in steps_meta:
      operation = self.get(steps_meta['exec'])
      wrapped = flowoperation(operation)

      # Run the step
      kwargs = wrapped(steps_meta, **kwargs)    
    # Set result to step context
    step_context.set_after(**kwargs)
    # Store the context
    self.context_stack.push(step_context)

    return kwargs['image']
    

  def calculate_next_step_index(self, step_meta):
    
    self.step_index += 1

    return


  def calculate_prev_step_index(self, step_meta):
    
    self.step_index -= 1

    return

  def continue_to_run(self, max_step):
    if self.step_index >= max_step:
      print("no more steps")
      return False
    return True
    

  def run(self, flow_meta, one = False):
    if not one: 
      self.reset()

    image = None
    steps_meta = flow_meta['steps']    

    while(self.continue_to_run(len(steps_meta))):
      step_meta = steps_meta[self.step_index]
      print("step", step_meta)
      image = self.run_step(step_meta)
      self.calculate_next_step_index(step_meta)
      if one == True: 
        break;

    return self.step_index, image


# PLAYBACK
  def back(self):
    image = None

    if self.step_index > 0:
      image = self.context_stack.peek().kwargs_before['image']
      step_meta = self.context_stack.peek().step_meta
      self.context_stack.pop()

      self.calculate_prev_step_index(step_meta)

    return self.step_index, image


  def top(self):
    print("top")

    return self.reset()

