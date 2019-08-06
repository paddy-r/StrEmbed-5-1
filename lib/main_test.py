#TH: step_parse module test

import step_parse

step_filename = 'C:/Users/prctha/Desktop/Torch Assembly.STEP'

step = step_parse.StepParse()

step.load_step(step_filename)

step.show_values()