# Image Processing Workshop Engine

## It is the central part of the [Image Processing Workshop](https://github.com/ekarpovs/image-processing-workshop) project. The engine runs flows (worksheets) that implement different image-processing techniques

### File system structure

    Anywhere in a file system:
_____
    |__ /data/ __ original images files for processing
    |
    |
    |__ /modules/ __ Python scripts that implemented sets of simple image-processing operations
    |    |
    |    |__init__.py - the 'modules' package declaration
    |   
    |__ /worksheets/ __ set of a worksheet files with a sequences of operations, combined for perform a whole flow 
    |   
    

    |__ /flow_runner/ The project files
    |

## Local Installation

```bash
cd flow_runner
pip install -e . --use-feature=in-tree-build
```

## Usage

```bash
python run.py -w <worsheet full path> [-d <fsm def full path>] [-s 'no'] [-t 'no']
```
