import copy
from flow_runner.exec_cntx import Cntx


def flow_runner_action(oper_impl):
  def execute(context):
    def map_before():
      io = context.get('input')
      data = io
      step = context.get('step')
      params = {}
      if 'params' in step:
        params = step.get('params')
      return params, data

    def map_after(io):
      context.put('output', io)
      return context

    __name__ = oper_impl.__name__
    __module__ = oper_impl.__module__
    print("executed: {}.{}".format(__module__, __name__))
    
    params, data = map_before()
    data = oper_impl(params, **data)
    context = map_after(data)
    return context
  return execute


