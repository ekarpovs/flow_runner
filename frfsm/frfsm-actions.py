
def flow_runner_action(oper_impl):
  '''
    Wrapper for any Flow Runner function (loaded from a module)
  '''
  
  def execute(context):
    def map_before():
      data = context.get_user_data('user_data')
      step = context.get_user_data('step')
      params = {}
      if 'params' in step:
        params = step.get('params')
      return params, data

    def map_after(data):
      context.set_user_data('user_data', data)
      return context

    __name__ = oper_impl.__name__
    __module__ = oper_impl.__module__
    print(f"executed: {__module__}.{__name__}")
    
    params, data = map_before()
    data = oper_impl(params, **data)
    context = map_after(data)
    
    return context
  return execute
