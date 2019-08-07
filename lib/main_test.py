#TH: step_parse module test

from step_parse import StepParse

#step_filename = '../examples/models/Torch Assembly.STEP'
step_filename = '../examples/models/as1-oc-214.stp'

step = StepParse()

step.load_step(step_filename)

step.print_tree()