# Usage:
#   python run.py -f <worksheet name> -i <input file name> 
# 

import argparse
import sys
import json

from flow_runner.runner import Runner  


# Construct the argument parser and parse the arguments
def parseArgs():
  ap = argparse.ArgumentParser(description="WorkShop")
  ap.add_argument("-f", "--flow", required = True,
	help = "name of a worksheet without extension.")
  ap.add_argument("-i", "--input", required = True,
	help = "path to the input file(s)")
  ap.add_argument("-o", "--output", required = False,
	help = "path to the output file(s)")
  
  args = ap.parse_args()   
  kwargs = dict((k,v) for k,v in vars(args).items() if k!="message_type")
  
  return kwargs


# Reads the string from the file, parses the JSON data, 
# populates a Python dict with the data
def readJson(ffn):
  with open(ffn, 'rt') as f:
    data = json.load(f)
  return data

# Read configuration file
def readConfig():
  config = readJson('./config.json')

  return config


def run():
  config = readConfig()

  # set paths to external modules located outside the package
  for m in config['modules']:
    sys.path.append(m)

  # The first step will always "start" for get the flow input
  image_file_name = "{}/{}".format(config['images'], kwargs["input"])
  first_step = [{"exec": "common.start", "ffn": image_file_name}]

  # The last step will always - store to store the flow output
  result_file_name = "{}/result-{}".format(config['results'], kwargs["input"])
  last_step = [{"exec": "common.store", "ffn": result_file_name}]

  # get the flow worksheet
  worksheet_file_name = "{}/{}.json".format(config['worksheets'], kwargs['flow'])
  flow_meta = readJson(worksheet_file_name)
  steps = flow_meta['steps']
  # Add first/last steps for input/output
  steps = [*first_step, *steps, *last_step]
  flow_meta['steps'] = steps

  # import factory for loading modules outside of the package 
  sys.path.append(config['factory'])
  import factory

  # init runner
  runner = Runner(factory)

  # execute the flow
  runner.run(flow_meta) 

# Main function
def main(**kwargs): 

  run()


# Entry point
if __name__ == "__main__":
    kwargs = parseArgs()
    main(**kwargs) 
