import copy
from .templates import Templates 

class StateType():
  EXEC, STM = range(2)

class StateOffset():
  REARWARD, NO, FORWARD = range(-1,2)

class StateOrder():
  REGULAR, LAST = range(2)


class StepConverter():
  def __init__(self, meta):
    self.meta = meta

  def convert(self):
    meta = self.meta
    templates = Templates()
    self.states_transitions = templates.get_transitions()

    def step_to_state_def(idx, offset=StateOffset.NO):
      step_meta = meta[idx+offset]
      if 'exec' in step_meta:
        step_name = step_meta['exec']
      else:
        step_name = step_meta['stm']
      return "{}-{}".format(idx+offset, step_name.split('.')[1]), step_name

    def converter(idx):
      def state_order(idx):
        if idx == len(meta)-1:
          return  StateOrder.LAST
        else:
          return StateOrder.REGULAR

      state_transitions = self.states_transitions[state_order(idx)]
      state_name, act_name = step_to_state_def(idx)
      trans_def = copy.deepcopy(state_transitions)
      for n, tr in enumerate(trans_def):
        tr['name'] = 'tr' + str(idx) + str(n) 
        tr['src'] = state_name
        event_name = trans_def[n]['event'] 
        if event_name == 'next':
          tr['action'] = act_name
          if idx < len(meta)-1:
            tr['target'], _ = step_to_state_def(idx, StateOffset.FORWARD)
          else:
            tr['target'] = state_name
        elif event_name == 'prev':
          if idx == 0:
            tr['target'], _ = step_to_state_def(idx)
          else:
            tr['target'], _ = step_to_state_def(idx, StateOffset.REARWARD)
        else:
          tr['action'] = act_name
          tr['target'] = state_name
      # add special transitions for stm
      # if 'stm' in meta[idx]:
      #   stmtrs_def = stm_transitions_def(meta[idx])
      #   trans_def.append(stmtrs_def)
      return state_name, trans_def
    return converter    
