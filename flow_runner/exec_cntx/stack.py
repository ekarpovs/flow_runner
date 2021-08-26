# import maxsize from sys module
# Used to return -infinite when stack is empty
from sys import maxsize

class Stack:
  def __init__(self, max_size=200):
    self.max_size = max_size
    self.stack = []


  def isEmpty(self):
    return len(self.stack) == 0

  def isFull(self):
    return len(self.stack) > self.max_size

  # Function to add an item to stack. It increases size by 1
  def push(self, item):
    self.stack.append(item)

  # Function to remove an item from stack. It decreases size by 1
  def pop(self):
    if (self.isEmpty()):
        return str(-maxsize -1) # return minus infinite
    return self.stack.pop()


  # Function to return the top from stack without removing it
  def peek(self):
    if (self.isEmpty()):
        return str(-maxsize -1) # return minus infinite
    return self.stack[-1]


  def size(self):
    return len(self.stack)

  def reset(self):
    self.stack = []
    return