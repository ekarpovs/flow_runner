import copy
from flow_runner.exec_cntx import Cntx

# Flow runner user action's wrapper
def flow_runner_action(oper_impl):
  def execute(context):
    def map_before():
      stack = context.get('stack')
      if stack.isEmpty():
        io = context.get('input')
        kwargs = copy.deepcopy(io)
      else:
        if context.get('current_state_executed'):
          _pop(context)
        cntx = stack.peek()
        kwargs = copy.deepcopy(cntx.get_io())
      step = context.get('step')
      if 'params' in step:
        step = step['params']
        if 'useorig' in step and step['useorig']:
          kwargs['image'] = copy.deepcopy(kwargs['orig'])
      return step, kwargs

    def map_after(io):
      if not context.get('last-state-executed') and not context.get('current_state_executed'):
        stack = context.get('stack')
        cntx = Cntx()
        cntx.put_io(io)
        stack.push(cntx)
        print("put:", stack.size())
      return

    __name__ = oper_impl.__name__
    __module__ = oper_impl.__module__
    print("executed: {}.{}".format(__module__, __name__))
    
    step, kwargs = map_before()
    kwargs = copy.deepcopy(oper_impl(step, **kwargs))   
    map_after(kwargs)
    return context

  return execute



# FRFsm actions
def flow_back_step(context):
  context = _pop(context)
  return context

def _pop(context):
  stack = context.get('stack')
  stack.pop()
  print("pop:", stack.size())
  return context

def current_state_executed(context):
  context.put('current_state_executed', True)
  return context

def current_state_not_executed(context):
  context.put('current_state_executed', False)
  return context

def last_state_executed(context):
  '''
  Sets flag - last state next/current event was executed

  arguments:
  - context

  Returns:
  - the context['last-state-executed'].
  '''
  context.put('last-state-executed', True)
  
  return context


def last_state_not_executed(context):
  '''
  Resets flag - last state next/current event was executed

  arguments:
  - context

  Returns:
  - the context['last-state-executed'].
  '''
  context.put('last-state-executed', False)
  
  return context


def reset_context(context):
  '''
  Resets all flags

  arguments:
  - context

  Returns:
  - the context.
  '''
  context = current_state_not_executed(context)
  context = last_state_not_executed(context)
  # stack = context.get('stack')
  # size = stack.size()
  # for i in range(size):
  #   _pop(context)
  return context


def forinrange_entry(context):
  '''
  Check forinrage condition
  '''
  print("forinrange_entry", context)

  return context


def forinrange_exit(context):
  '''
  Change forinrage condition
  '''
  print("forinrange_exit", context)

  return context
