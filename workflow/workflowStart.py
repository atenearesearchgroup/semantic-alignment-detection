import os

import pandas as pd
from src import util

from workflow.equalityChecker import EqualityChecker
from workflow.contradictionChecker import ContradictionChecker
from workflow.containmentChecker import ContainmentChecker


def get_prompts(file_name, model_element):
    dirname = util.get_project_directory()
    file_path = os.path.join(dirname, f'src/resources/prompts/{file_name}')
    with open(file_path, 'r') as file:
        content = file.read()

    local_vars = {}

    exec(content, local_vars)

    if file_name == 'contradiction':
        attribute_prompts = local_vars['attribute_prompts']
        association_prompts = local_vars['association_prompts']
        inheritance_prompt = local_vars['inheritance_prompt']
        enum_prompt = local_vars['enum_prompt']

        if model_element == 'associations' or model_element == 'aggregations':
            return association_prompts
        elif model_element == 'inheritance':
            return inheritance_prompt
        elif model_element == 'enums':
            return enum_prompt
        else:
            return attribute_prompts

    return local_vars['prompts']


class WorkflowStart:
    def __init__(self, individual_maps, domain, results_dir):
        self.individual_maps = individual_maps
        self.results_dir = f"{results_dir}/predictions"
        self.equality_checker = EqualityChecker()
        self.contradiction_checker = ContradictionChecker()
        self.containment_checker = ContainmentChecker()
        # self.difference_finder = DifferenceFinder()
        self.domain = domain
        self.checks = ['equality', 'contradiction', 'inclusion']
        self.checkers = {}
        self.check_results = {}

        self.elements = ['attributes', 'associations', 'aggregations', 'compositions', 'inheritance', 'enums']

        for check in self.checks:
            for element in self.elements:
                prompts = ['actual_description', 'generated_description']
                prompts.extend(get_prompts(check, element))
                self.check_results[(check, element)] = pd.DataFrame(columns=prompts)
            self.checkers[check] = self.get_checker(check)

    def get_checker(self, check):
        if check == 'equality':
            return self.equality_checker
        elif check == 'contradiction':
            return self.contradiction_checker
        else:
            return self.containment_checker

    def add_dummy_values(self, check_index, pred_map, i):
        for index in range(check_index + 1, len(self.checks)):
            check = self.checks[index]
            pred_map.at[i, check] = False

    def run(self):
        # Take actual and generated sentence Run all the checkers one by one. if result of any checker is true then
        # accordingly add it in warnings or errors array, Run next checker only if result of previous checker is false

        errors = []

        if not os.path.exists(rf"{self.results_dir}"):
            os.makedirs(f"{self.results_dir}")

        if not os.path.exists(rf"{self.results_dir}//{self.domain}"):
            os.makedirs(f"{self.results_dir}//{self.domain}")

        # For each category of model element
        for index in range(len(self.individual_maps)):
            pred_map = self.individual_maps[index]

            # For each model element
            for i, row in pred_map.iterrows():
                actual_description = row['actual_description']
                generated_description = row['generated_description']
                source = row.get('source', '')
                target = row.get('target', '')
                multiplicity = row.get('multiplicity', '')

                # each check
                for check_index, check in enumerate(self.checks):
                    checker = self.checkers[check]
                    check_res = self.check_results[(check, self.elements[index])]

                    if check not in pred_map.columns or pred_map.at[i, check] is None or pd.isna(pred_map.at[i, check]):
                        results, res = checker.run(actual_description, generated_description, source, target,
                                                   self.elements[index], multiplicity)
                        pred_map.at[i, check] = res
                        result = [actual_description, generated_description]
                        result.extend(results)
                        check_res.loc[len(check_res)] = result

                        if isinstance(res, bool):
                            if res:
                                if check == 'contradiction':
                                    errors.append({
                                        'actual_description': actual_description,
                                        'generated_description': generated_description
                                    })

                                    # This function add False value for remaining checks, this is done to avoid code
                                    # break in next steps
                                self.add_dummy_values(check_index, pred_map, i)
                                break

            pred_map.to_csv(f"{self.results_dir}/{self.domain}/{self.elements[index]}_pred_map.csv", index=False)
        for check in self.checks:
            for element in self.elements:
                check_res = self.check_results[(check, element)]
                check_res.to_excel(f"{self.results_dir}/{self.domain}/{element}_{check}_check.xlsx", index=False)

        return errors


# domain_name, results_dir = "R19-airport", "../final_evaluation_misalignment"
# attributes_map = pd.read_csv(f"{results_dir}/predictions/{domain_name}/attributes_pred_map.csv")
# associations_map = pd.read_csv(f"{results_dir}/predictions/{domain_name}/associations_pred_map.csv")
# aggregations_map = pd.read_csv(f"{results_dir}/predictions/{domain_name}/aggregations_pred_map.csv")
# compositions_map = pd.read_csv(f"{results_dir}/predictions/{domain_name}/compositions_pred_map.csv")
# inheritance_map = pd.read_csv(f"{results_dir}/predictions/{domain_name}/inheritance_pred_map.csv")
# enum_map = pd.read_csv(f"{results_dir}/predictions/{domain_name}/enums_pred_map.csv")
# workflow = WorkflowStart(
#     [attributes_map, associations_map, aggregations_map, compositions_map,
#      inheritance_map, enum_map], domain_name, results_dir)
# errors = workflow.run()
