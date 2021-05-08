
# Decorator for an operation
def flowoperation(executor):
  def executorWrapper(step, **kwargs):
    __name__ = executor.__name__

    # If True use the original image as input for the operation, otherwise
    # use the prev operation output image as input for the operation
    useorig = step.get('useorig', False)
    if useorig == True:
      kwargs['image'] = kwargs['orig'].copy()
    
    kwargs = executor(step, **kwargs)

    return kwargs

  return executorWrapper
