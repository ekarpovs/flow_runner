'''
  Flow runner data sorage
'''


class Storage:
  def __init__(self):
    self._storage = {}

  @property
  def storage(self):
    return self._storage

  @storage.setter
  def storage(self, value):
    self._storage = value
    return

  def get_state_data(self, id):
    return self.storage.get(id, None)

  def put_state_data(self, id, data):
    self.storage[id] = data
    return
