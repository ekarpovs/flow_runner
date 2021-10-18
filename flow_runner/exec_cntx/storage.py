'''
  Flow runner data sorage
'''

from typing import List

from .state_cntx import StateContext


class Storage:
  def __init__(self):
    self._storage = {}

  def get_item(self, id):
    return self._storage.get(id, None)

  def put_item(self, id, item: StateContext):
    self._storage[id] = item
    return
