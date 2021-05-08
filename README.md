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
    

    |__ /engine/ The project files
    |

## Installation

```bash
cd engine
pip install opencv-python
```

## Run

```bash
cd project
python driver.py -f <worksheet name> -i <input file name>
```
