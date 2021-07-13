class Cntx:
  def __init__(self):
    self.meta = None
    self.io = None

  def put_meta(self, meta):
    self.meta = meta

  def put_io(self, io):
    self.io = io

  def get_meta(self):
    return self.meta

  def get_io(self):
    return self.io
