import copy

def flow_runner_action(oper_impl):
  def execute(context):
    def map_before():
      data = {}    
      io = context.get_user_data('io')
      data['image'] = io.get('input')
      step = context.get_user_data('step')
      params = {}
      if 'params' in step:
        params = step.get('params')
      return params, data

    def map_after(data):
      io = {}
      io['output'] = data.get('image')  
      context.set_user_data('io', io)
      return context

    __name__ = oper_impl.__name__
    __module__ = oper_impl.__module__
    print(f"executed: {__module__}.{__name__}")
    
    params, data = map_before()
    data = oper_impl(params, **data)
    context = map_after(data)
    
    return context
  return execute
