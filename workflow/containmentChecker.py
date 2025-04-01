from abc import ABC

import workflow.apiCaller as apiCaller
import os
from src import util
from workflow.abstractChecker import AbstractChecker

dirname = util.get_project_directory()
file_path = os.path.join(dirname, 'src/resources/prompts/inclusion')


class ContainmentChecker(AbstractChecker):
    def __init__(self):
        with open(file_path, 'r') as file:
            content = file.read()

        local_vars = {}

        exec(content, local_vars)
        self.prompts = local_vars['prompts']

    def get_prompts(self, model_element):
        return self.prompts

    def process_response(self, response, model_element):
        return response

    # def run(self, actual_sentence, generated_sentence):
    #     positive_count = 0
    #     negative_count = 0
    #     results = []
    #     for prompt in self.prompts:
    #         result = apiCaller.call_api(actual_sentence, generated_sentence, prompt)
    #         results.append(result)
    #         print("Prompt:", prompt)
    #         print("Actual sentence:", actual_sentence)
    #         print("Generated sentence:", generated_sentence)
    #         print("Result:", result)
    #         print()
    #         if result.startswith("Yes") or result.startswith("yes"):
    #             positive_count = positive_count + 1
    #
    #         if result.startswith("No") or result.startswith("no"):
    #             negative_count = negative_count + 1
    #
    #     return results, positive_count >= negative_count
