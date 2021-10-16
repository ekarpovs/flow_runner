# Usage:
#   python run.py -i <input file> -o <output file> -m <worsheet full path> [-d <fsm def full path>] [-s 'no'] [-t 'no']
# 

import argparse
import json
import cv2

from flow_converter import FlowConverter
from flow_runner import Runner

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


def storeImage(input_ffn, out_path, image, idx):
  ffn = input_ffn.replace('\\', '/')
  fn, ext = ffn.split('/')[-1].split('.')
  ffn = "{}/result-{}-{}.{}".format(out_path, fn, idx, ext)
  cv2.imwrite(ffn, image)
  return


def run_by_step(runner, flow_meta, events):
  idx = 0
  while(True):
    print('q - quit')
    prompt = 'waits for an event {}:'.format(events)
    print(prompt)
    # print('waits for an event(next, prev, current):')
    event = input()
    if event == 'q':
      return
    if event not in events:
      continue
    step_meta = ''
    if idx < len(flow_meta):
      step_meta = flow_meta[idx]
    idx, cv2image = runner.run_step(event, step_meta)
    storeImage(kwargs["input"], kwargs["output"], cv2image, idx)
  return


def run_all(runner, flow_meta):
  runner.run_all(flow_meta)
  return


# Main function - the runner's client
def main(**kwargs): 
  fsm_conf = readConfig()
  image = readImage(kwargs["input"])
  flow_meta = readJson(kwargs['meta'])
  flow_meta.insert(0, {"stm": "glbstm.begin"})
  flow_meta.append({"stm": "glbstm.end"})
  for i, meta in enumerate(flow_meta):
    meta['id'] = i
  if kwargs['def']:
    fsm_def = readJson(kwargs['def'])
  else:
    fc = FlowConverter(flow_meta)
    fsm_def = fc.convert()
    # if kwargs['trace'] == 'yes':
    #   writeJson('../data/fsm-def/fsm-def-edge.json', fsm_def)
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
    run_by_step(rn, flow_meta, fsm_conf.get('events'))   
  return


# Entry point
if __name__ == "__main__":
    kwargs = parseArgs()
    main(**kwargs) 
