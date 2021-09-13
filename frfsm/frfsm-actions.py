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
        step = step.get('params')
        if 'useorig' in step and step.get('useorig'):
          kwargs['image'] = kwargs.get('orig').copy()
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
# Move to stm exit actions??? Need to know meta.
def stm_included(context):
  '''
  Is used as exit action for the first, inside forinrange stm, state
  '''
  event = context.get('event')
  if event == 'next':
    last_stm = context.get('last_stm')
    if last_stm is not None:
      stm_params = last_stm.get('params')
      name = stm_params.get('name')
      value = stm_params.get('value')
      # prepare input for an included states
      step = context.get('step')
      params = step.get('params')
      # map 'i' 
      params[name] = value
  return context

def forinrange_exit(context):
  '''
  Change forinrage condition
  '''
  state_stm = context.get('last_stm')
  event = context.get('event')
  if event == 'next':
    step = context.get('step')
    # "params":{"start": 0, "stop": 60, "step": 15, "i": "angle", "include": 1}
    params = step.get('params')
    start = params.get('start')
    stop = params.get('stop')
    step = params.get('step')
    name = params.get('map')
    include = params.get('include')

    state_name = context.get_current_state_name()
    if state_stm:
      # remove from stack previous result (all states under the stm)
      count = state_stm.get('params').get('count')
      end = state_stm.get('params').get('end')
      if count > 0:
        stack = context.get('stack')
        for i in range(include+1):
          # print('forinrange exit - stack size - before:', stack.size())
          stack.pop()
          # print('forinrange exit - stack size - after:', stack.size())
    else:
      # the first time
      end = False
      count = 0
    value = start + step*count
    if value >= stop:
      end = True
    count += 1 
      # create/change current context for the stm
    state_stm = {'name': state_name, 'params': {'count': count, 'end': end, 'name': name, 'value': value}}
    context.put('last_stm', state_stm)
  elif event == 'prev' or event == 'next_end':
    if state_stm:
      # stack = context.get('stack')
      # stack.pop()
      # remove current context for the stm
      context.put('last_stm', None)
  return context

def while_exit(context):
  '''
  Change forinrage condition
  '''
  state_stm = context.get('last_stm')
  event = context.get('event')
  if event == 'next':
    step = context.get('step')
    # "params":{"start": 0, "stop": 60, "step": 15, "i": "angle", "include": 1}
    params = step.get('params')
    condition = params.get('cond')
    include = params.get('include')

    state_name = context.get_current_state_name()
    if state_stm:
      # remove from stack previous result (all states above the stm)
      end = state_stm.get('params').get('end')
      if condition:
        stack = context.get('stack')
        for i in range(include+1):
          # print('forinrange exit - stack size - before:', stack.size())
          stack.pop()
          # print('forinrange exit - stack size - after:', stack.size())
    else:
      # the first time
      end = False
      condition = True

    if not condition:
      end = True
      # create/change current context for the stm
    state_stm = {'name': state_name, 'params': {'cond': condition, 'end': end}}
    context.put('last_stm', state_stm)

  elif event == 'prev' or event == 'next_end':
    if state_stm:
      stack = context.get('stack')
      stack.pop()
      # remove current context for the stm
      context.put('last_stm', None)

  return context

