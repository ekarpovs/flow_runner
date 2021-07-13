import copy

class StateType():
  EXEC, STM = range(2)

class StateOffset():
  REARWARD, NO, FORWARD = range(-1,2)

class StateOrder():
  FIRST, LAST, REGULAR = range(3)



class FlowConverter():
  def __init__(self, meta):
    self.meta = meta
    # Predefine transitions
    # TEMPLATE_TRANSITION = ["name", "src", "event", "target", "action", "start-action", "end-action"]
    self.states_transitions = [
      [
        self.def_transition(["", "", "next", "", "", "", ""]),
        self.def_transition(["", "", "current", "", "", "", ""])
      ],
      [
        self.def_transition(["", "", "next", "", "", "", "____frfsm-actions.last_state_executed"]),
        self.def_transition(["", "", "current", "", "", "", ""]),
        self.def_transition(["", "", "prev", "", "", "", "____frfsm-actions.last_state_not_executed"]),
      ],       
      [
        self.def_transition(["", "", "next", "", "", "", ""]),
        self.def_transition(["", "", "current", "", "", "", ""]),
        self.def_transition(["", "", "prev", "", "", "", ""]),
      ]
    ]

# Utilites
  @staticmethod
  def inst_template(keys, values):
    return dict(zip(keys, values))

  def def_fsm(self, values):
    TEMPLATE_FSM = ["info", "context-name", "init-action", "first-state", "states"]    
    return self.inst_template(TEMPLATE_FSM, values)

  def def_state(self, values):
    TEMPLATE_STATE = ["name", "entry-action", "exit-action", "transitions"]
    return self.inst_template(TEMPLATE_STATE, values)

  def def_transition(self, values):
    TEMPLATE_TRANSITION = ["name", "src", "event", "target", "action", "start-action", "end-action"]
    return self.inst_template(TEMPLATE_TRANSITION, values)
 
# Runtime
  def step_converter(self):
    meta = self.meta
    states_transitions = self.states_transitions

    def step_to_state_def(idx, offset=StateOffset.NO):
      step_meta = meta[idx+offset]
      if 'exec' in step_meta:
        step_name = step_meta['exec']
      else:
        step_name = step_meta['stm']
      return "{}-{}".format(idx+offset, step_name.split('.')[1]), step_name

    def converter(idx):
      def state_order(idx):
        if idx == 0:
          return  StateOrder.FIRST
        elif idx == len(self.meta)-1:
          return  StateOrder.LAST
        else:
          return StateOrder.REGULAR

      def stm_transitions_def(step_meta):
        return None

      state_transitions = states_transitions[state_order(idx)]
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

  def convert(self):
    states_def = []
    first_state_name = None
    for i, _ in enumerate(self.meta):
      state_entry_action = "" 
      state_exit_action = ""

      convert_step_meta = self.step_converter()
      state_name, trans_def = convert_step_meta(i)
      if i == 0:
        state_entry_action = '____frfsm-actions.reset_context' 
        first_state_name = state_name
      # TEMPLATE_STATE = ["name", "entry-action", "exit-action", "transitions"]
      state_def = self.def_state([state_name, state_entry_action, state_exit_action, trans_def])
      states_def.append(state_def)
    # TEMPLATE_FSM = ["info", "context-name", "init-action", "first-state", "states"]    
    fsm_def = self.def_fsm(['', '', '', first_state_name, states_def])
    return fsm_def
