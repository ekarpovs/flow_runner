class Context:
  def __init__(self, step_meta, **kwargs):
    self.step_meta = step_meta
    self.kwargs_before = kwargs
    self.kwargs_after = None

  def set_after(self, **kwargs):
    self.kwargs_after = kwargs
