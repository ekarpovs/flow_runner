import copy
from flow_runner.exec_cntx import Cntx

# Flow runner user action's wrapper
def flow_runner_action(oper_impl):
  def execute(context):
    def map_before():
      stack = context.get('stack')
      cntx = stack.peek()
      kwargs = copy.deepcopy(cntx.get_io())
      step = copy.deepcopy(cntx.get_meta())
      if 'params' in step:
        step = step['params']
        if 'useorig' in step and step['useorig']:
          kwargs['image'] = kwargs['orig'].copy()
      return step, kwargs

    def map_after(io):
      if not context.get('last-state-executed') or not context.get('current_step') :
        stack = context.get('stack')
        cntx = Cntx()
        cntx.put_io(io)
        stack.push(cntx)
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
  stack = context.get('stack')
  if stack.size() > 1:
    stack.pop()
  return context


def set_current_step(context):
  context.put('current_step', True)
  return context

def reset_current_step(context):
  context.put('current_step', False)
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

  context = last_state_not_executed(context)
  
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
