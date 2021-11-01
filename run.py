# Usage:
#   python run.py -i <input file> -o <output file> -m <worsheet full path> [-d <fsm def full path>] [-s 'no'] [-t 'no']
# 

import argparse
import json
import os
import cv2

from flow_converter import FlowConverter
from flow_model.flowmodel import FlowModel
from flow_runner import Runner

# Construct the argument parser and parse the arguments
def parseArgs():
  ap = argparse.ArgumentParser(description="flow runner fsm")
  ap.add_argument("-w", "--ws", required = True,
	help = "full path to the worksheet file")
  ap.add_argument("-d", "--def", required = False,
	help = "full path to the fsm definition file")
  ap.add_argument("-i", "--input", required = True,
	help = "full path to the input file(s)")
  ap.add_argument("-o", "--output", required = False,
	help = "full path to the output file(s)")
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


def readImage(ffn):
  image = cv2.imread(ffn)
  return image


def store_image(input_ffn, out_path, image, idx, event):
  ffn = input_ffn.replace('\\', '/')
  fn, ext = ffn.split('/')[-1].split('.')
  ffn = f"{out_path}/result-{fn}-{idx}-{event}.{ext}"
  cv2.imwrite(ffn, image)
  return


def run_by_step(runner, model, events):
  idx = 0
  while(True):
    print('q - quit')
    prompt = f"waits for an event {events}:"
    print(prompt)
    # print('waits for an event(next, prev, current):')
    event = input()
    if event == 'q':
      return
    if event not in events:
      continue
    step_meta = model.get_item(idx)
    idx, cv2image = runner.run_step(event, step_meta)
    store_image(kwargs.get("input"), kwargs.get("output"), cv2image, idx, event)
  return


def run_all(runner, model):
  runner.run_all(model)
  return

# Main function - the runner's client
def main(**kwargs): 
  fsm_conf = readConfig()
  image = readImage(kwargs.get("input"))
  ffn = kwargs.get("ws")
  ws = readJson(ffn)
  # Get FRFSM defintion
  if kwargs.get("def"):
    # directly, from fsm def
    fsm_def = readJson(kwargs.get("def"))
  else:
    # by convert the meta
    # pn = os.path.split(ffn)    
    # path = pn[0]
    # name = pn[1]
    model = FlowModel(ws)
    fc = FlowConverter(model)
    fsm_def = fc.convert()
    # if kwargs['trace'] == 'yes':
    #   writeJson('../data/fsm-def/fsm-def-edge.json', fsm_def)
  # Create the runner
  rn = Runner()
  # Recreate engine when a flow meta changed
  rn.create_frfsm(fsm_conf, fsm_def)
  # Restart when a new image was passed 
  rn.start()
  rn.init_storage(image)

  if kwargs.get("step") == "no":
    run_all(rn, model)
  else:
    run_by_step(rn, model, fsm_conf.get('events'))   
  return


# Entry point
if __name__ == "__main__":
    kwargs = parseArgs()
    main(**kwargs) 
