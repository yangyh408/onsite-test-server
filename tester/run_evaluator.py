import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), './evaluate'))

from test_status import listen
from evaluator import evaluating_multiple_scenarios
from evaluator import recording

class RunEvaluator():
    def __init__(self, save_record = True):
        self.save = save_record

    def evaluate(self, input_dir, output_dir, record_dir, test_status: object):
        test_status.update('evaluate')
        evaluate_listen, score = self._run_evaluate(input_dir, output_dir, record_dir)
        test_status.update('evaluate', evaluate_listen)
        if evaluate_listen['status'] == 'SUCCESS':
            return score
        else:
            return -1
    
    @listen
    def _run_evaluate(self, input_dir, output_dir, record_dir):
        result = evaluating_multiple_scenarios(output_dir, input_dir)
        if self.save:
            recording(result, output_dir, record_dir)
        return sum(result[4])/len(result[4])

if __name__ == '__main__':
    input_dir = os.path.join(os.path.dirname(__file__), '../scenes/A/test/inputs')
    output_dir = os.path.join(os.path.dirname(__file__), '../temp/test_outputs')
    record_dir = os.path.join(os.path.dirname(__file__), '../record/test_outputs')
    evaluator = RunEvaluator(save_record = True)
    print(evaluator._run_evaluate(input_dir, output_dir, record_dir))
    # result = evaluating_multiple_scenarios(output_dir, input_dir)