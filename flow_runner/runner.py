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


  def run(self, flow_meta, one = False):
    if not one: 
      self.reset()

    image = None
    steps_meta = flow_meta['steps']    

    execute = True
    while(execute):
      if self.step_index >= len(steps_meta):
        print("no more steps")
        execute = False
      else:
        step_meta = steps_meta[self.step_index]
        if (step_meta is not None) and (self.step_index < len(steps_meta)):
          image = self.run_step(step_meta)
          self.calculate_next_step_index(step_meta)
          if one == True: 
            execute = False
        else:
          execute = False

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

