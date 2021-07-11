class Cntx:
  def __init__(self):
    self.step_meta = None
    self.kwargs = None

  def set_step_meta(self, step_meta):
    self.step_meta = step_meta

  def set_kwargs(self, kwargs):
    self.kwargs = kwargs

  def get_step_meta(self):
    return self.step_meta

  def get_kwargs(self):
    return self.kwargs
