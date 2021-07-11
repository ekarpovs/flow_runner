import copy
# Flow runner user action's wrapper
def flow_runner_action(oper_impl):
  def execute(context):
    def map_context(context):
      kwargs = copy.deepcopy(context.get('kwargs', {}))
      step = context.get("step", {})
      if 'params' in step:
        step = step['params']
        if 'useorig' in step and step['useorig']:
          kwargs['image'] = kwargs['orig'].copy()
      return step, kwargs

    __name__ = oper_impl.__name__
    __module__ = oper_impl.__module__
    print("executed: {}.{}".format(__module__, __name__))
    step, kwargs = map_context(context)
    kwargs = copy.deepcopy(oper_impl(step, **kwargs))
    context.put('kwargs', kwargs)
    return context

  return execute


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


