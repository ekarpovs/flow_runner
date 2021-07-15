import copy
from flow_runner.exec_cntx import Cntx

# Flow user action's wrapper
def flow_runner_action(oper_impl):
  def execute(context):
    def map_before():
      stack = context.get('stack')
      if stack.isEmpty():
        io = context.get('input')
      else:
        cntx = stack.peek()
        io = cntx.get_io()
      kwargs = copy.deepcopy(io)
      step = context.get('step')
      if 'params' in step:
        step = step['params']
        if 'useorig' in step and step['useorig']:
          kwargs['image'] = kwargs['orig'].copy()
      return step, kwargs

    def map_after(io):
      if context.get('store-state'):
        stack = context.get('stack')
        cntx = Cntx()
        cntx.put_io(copy.deepcopy(io))
        stack.push(cntx)
        print("put:", stack.size())
        #  current output
      io = copy.deepcopy(kwargs)
      context.put('output', io)
      return context

    __name__ = oper_impl.__name__
    __module__ = oper_impl.__module__
    print("executed: {}.{}".format(__module__, __name__))
    
    step, kwargs = map_before()
    kwargs = copy.deepcopy(oper_impl(step, **kwargs))   
    context = map_after(kwargs)
    return context

  return execute



# FRFsm actions
def not_store(context):
  context.put('store-state', False)
  return context

def store(context):
  context.put('store-state', True)
  return context

def back(context):
  context = _pop(context)
  return context

def _pop(context):
  stack = context.get('stack')
  stack.pop()
  print("pop:", stack.size())
  if stack.isEmpty():
    io = context.get('input')
  else:
    cntx = stack.peek()
    io = cntx.get_io()
  context.put('output', copy.deepcopy(io))
  return context

# STM actions

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
