# Usage:
#   python run.py -w <worsheet full path> [-d <fsm def full path>] [-o 'no'] [-s 'no'] [-t 'no'] 
# 

import argparse
import json
import sys
import cv2

from flow_converter import FlowConverter
from flow_model import FlowModel
from flow_runner import Runner
from flow_storage import FlowStorage, FlowStorageConfig

# Construct the argument parser and parse the arguments
def parseArgs():
  ap = argparse.ArgumentParser(description="flow runner fsm")
  ap.add_argument("-w", "--ws", required = True,
	help = "full path to the worksheet file")
  ap.add_argument("-d", "--def", required = False,
	help = "full path to the fsm definition file")
  ap.add_argument("-s", "--step", required = False,
  default="no", 
	help = "step mode")
  ap.add_argument("-t", "--trace", required = False,
  default="no",
	help = "print output")
  
  args = ap.parse_args()   
  kwargs = dict((k,v) for k,v in vars(args).items() if k!="message_type")
  return kwargs

# Reads the string from the file, parses the JSON data, 
# populates a Python dict with the data
def readJson(ffn):
  with open(ffn, 'rt') as f:
    data = json.load(f)
  return data

def writeJson(ffn, data):
  with open(ffn, 'w') as fp:
    json.dump(data, fp, indent=2)
  return

# Read configuration files
def readConfig():
  return readJson('./cfg/fsm-cfg.json')

def set_runtime_environment(cfg):
  actions_paths = cfg.get('user-actions-paths')
  for path in actions_paths:
    sys.path.append(path)

def run_by_step(runner: Runner, model, events):
  while(True):
    print('q - quit')
    prompt = f"waits for an event {events}:"
    print(prompt)
    event = input()
    if event == 'q':
      return
    if event not in events:
      continue
    idx = runner.state_idx
    step_meta = model.get_item(idx)
    runner.run_step(event, step_meta)
  return


def run_all(runner, model):
  runner.run_all(model)
  return

# Main function - the runner's client example
def main(**kwargs): 
  fsm_conf = readConfig()
  set_runtime_environment(fsm_conf)
  ffn = kwargs.get("ws")
  ws = readJson(ffn)
 
  # Get FRFSM defintion
  if kwargs.get("def"):
    # directly, from fsm def
    fsm_def = readJson(kwargs.get("def"))
  else:
    # by convert the ws
    model = FlowModel(ws)
    fc = FlowConverter(model)
    fsm_def = fc.convert()
    # if kwargs['trace'] == 'yes':
    #   writeJson('../data/fsm-def/fsm-def-test.json', fsm_def)

  # Create Flow Storage
  storage_cfg = fsm_conf.get('storage', '.')
  config = FlowStorageConfig(storage_cfg)
  storage = FlowStorage(config, model.get_as_ws())

  # Create the runner
  rn = Runner()
  # Recreate context, when a flow meta changed
  rn.storage = storage
  rn.create_frfsm(fsm_conf, fsm_def)
  rn.start()
  # rn.init_storage(image)

  if kwargs.get("step") == "no":
    run_all(rn, model)
  else:
    run_by_step(rn, model, fsm_conf.get('events'))   
  return

# Entry point
if __name__ == "__main__":
    kwargs = parseArgs()
    main(**kwargs) 
