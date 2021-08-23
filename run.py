# Usage:
#   python run.py -i <input file> -o <output file> [-t True]
# 

import argparse
import json
from os import pathsep
import cv2

from flow_runner import Runner
from flow_converter import FlowConverter

# Construct the argument parser and parse the arguments
def parseArgs():
  ap = argparse.ArgumentParser(description="flow runner fsm")
  ap.add_argument("-m", "--meta", required = True,
	help = "full path to the meta data file")
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

# Read configuration files
def readConfig():
  return readJson('./cfg/fsm-cfg.json')

def storeFsmDef(fsm_def):
  out_path = '../data/fsm-def'
  ffn = "{}/fsm-def.json".format(out_path)
  json_object = json.dumps(fsm_def, indent = 2) 
  with open(ffn, "w") as outfile: 
    outfile.write(json_object)
  return

def readImage(ffn):
  image = cv2.imread(ffn)
  return image

def storeImage(input_ffn, out_path, image, idx):
  ffn = input_ffn.replace('\\', '/')
  fn, ext = ffn.split('/')[-1].split('.')
  ffn = "{}/result-{}-{}.{}".format(out_path, fn, idx, ext)
  cv2.imwrite(ffn, image)

def run_by_step(runner, flow_meta):
  idx = 0
  while(True):
    print('q - quit, r - run all')
    print('waits for an event(next, prev, current):')
    event = input()
    if event == 'q':
      return

    step_meta = ''
    if idx < len(flow_meta):
      step_meta = flow_meta[idx]
    idx = run_step(runner, event, step_meta)

def run_all(runner, flow_meta):
    n = runner.get_number_of_states()
    idx = 0
    while (idx < n-1):
      step_meta = flow_meta[idx]
      idx = run_step(runner, 'next', step_meta)
    run_step(runner, 'next', step_meta)


def run_step(runner, event, step_meta):
  idx, cv2image = runner.dispatch_event(event, step_meta)
  storeImage(kwargs["input"], kwargs["output"], cv2image, idx)
  return idx


# Main function - the runner's client
def main(**kwargs): 
  fsm_conf = readConfig()
  image = readImage(kwargs["input"])
  flow_meta = readJson(kwargs['meta'])
  flow_meta.append({"stm": "glbstm.end"})
  for i, meta in enumerate(flow_meta):
    meta['id'] = i
  if kwargs['def']:
    fsm_def = readJson(kwargs['def'])
  else:
    fc = FlowConverter(flow_meta)
    fsm_def = fc.convert()
    if kwargs['trace'] == 'yes':
      storeFsmDef(fsm_def)

  # Create the runner
  rn = Runner()
  # Recreate engine when a flow meta changed
  rn.init_fsm_engine(fsm_conf, fsm_def)
  # Restart when a new image was passed 
  rn.start()
  rn.init_io(image)

  if kwargs["step"] == "no":
    run_all(rn, flow_meta)
  else:
    run_by_step(rn, flow_meta)   

# Entry point
if __name__ == "__main__":
    kwargs = parseArgs()
    main(**kwargs) 
