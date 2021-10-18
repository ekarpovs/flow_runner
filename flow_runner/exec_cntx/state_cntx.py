'''
  FRFSM State data sorage
'''

class StateContext:
  def __init__(self, io={'input': None, 'output': None}):
    self._io = io

  @property
  def io(self):
    return self._io

  @io.setter
  def io(self, value):
    self._io = value
    return

  @property
  def input_(self):
    return self.io.get('input')

  @input_.setter
  def input_(self, value):
    self.io['input'] = value
    return
  
  @property
  def output_(self):
    return self._io.get('output')

  @output_.setter
  def output_(self, value):
    self._io['output'] = value
    return
