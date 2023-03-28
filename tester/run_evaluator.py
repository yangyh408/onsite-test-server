import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), './evaluate'))

from logger import debugger, logger

from evaluator import evaluating_multiple_scenarios
from evaluator import recording

class RunEvaluator():
    def __init__(self, submitId, save_record = True):
        self.save = save_record
        self.submitId = submitId

    @debugger('cls')
    def evaluate(self, input_dir, output_dir):
        # print('  - [Evaluate] Evaluating:')
        try:
            result = evaluating_multiple_scenarios(output_dir, input_dir)
            if self.save:
                recording(result, output_dir)
            # print("  - [Evaluate] Done")
            return sum(result[-1])/len(result[-1])
        except Exception as e:
            logger.exception(f"[EVALUATE ERROR]:{repr(e)}", extra={'submitId': self.submitId})
            return -1

if __name__ == '__main__':
    input_dir = r"/home/ubuntu/onsite-develop/onsite-test-server/scenes/A/complex/inputs"
    output_dir = r"/home/ubuntu/onsite-develop/onsite-test-server/temp/s_20230320051500_20230316121333"
    evaluator = RunEvaluator(save_record = True)
    # evaluator.evaluate(input_dir, output_dir)
    result = evaluating_multiple_scenarios(output_dir, input_dir)