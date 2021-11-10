from typing import List

from flow_storage import FlowStorage
from flow_storage import FlowStateStorage
from flow_storage import FlowDataRef
from flow_storage import FlowStateIOData

def flow_runner_action(oper_impl):
  '''
    Wrapper for any Flow Runner function (loaded from a module)
  '''
  
  def execute(context):
    __name__ = oper_impl.__name__
    __module__ = oper_impl.__module__
    print(f"executed: {__module__}.{__name__}")
    
    params = context.get_user_data('params')   
    data = context.get_user_data('data')   

    data = oper_impl(params, **data)

    context.set_user_data('params', {})   
    context.set_user_data('data', data)   
    return context
  return execute
