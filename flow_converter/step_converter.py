import copy
from .templates import Templates 

class StateType():
  EXEC, STM_END, STM_FORINRANGE, STM_WHILE = range(4)

class StateOffset():
  REARWARD, NO, FORWARD = range(-1,2)

# class StateOrder():
#   REGULAR, LAST = range(2)


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
      step_meta = meta[idx]
      def state_type(idx):
        if 'exec' in step_meta:
          return StateType.EXEC
        else:
          stm = step_meta['stm']
          if stm == 'glbstm.end':
            return StateType.STM_END
          if stm == 'glbstm.forinrangestm':
            return StateType.STM_FORINRANGE
          if stm == 'glbstm.whilestm':
            return StateType.STM_WHILE
      
      state_entry_action = ''
      state_exit_action = ''
      state_type = state_type(idx)
      state_transitions = []
      # for all stms - begin
      # if state_type == StateType.STM_FORINRANGE:
      if state_type > StateType.STM_END:
        step_params = step_meta.get('params')
        incl = step_params.get('include')
      # for all stms - end
        state_transitions = self.states_transitions[StateType.STM_FORINRANGE]
      else:
        state_transitions = self.states_transitions[state_type]
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
        elif event_name == 'next_end':
          tr['action'] = act_name
          if idx < len(meta)-1:
            tr['target'], _ = step_to_state_def(idx, StateOffset.FORWARD+incl)
          else:
            tr['target'] = state_name
        elif event_name == 'prev':
          if idx == 0:
            tr['target'], _ = step_to_state_def(idx)
          else:
            tr['target'], _ = step_to_state_def(idx, StateOffset.REARWARD)
        else: # 'current'
          tr['action'] = act_name
          tr['target'] = state_name
      return state_name, trans_def, state_entry_action, state_exit_action
    return converter    
