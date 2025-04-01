import os

import pandas as pd

from evaluation.AttributeResultAggregator import aggregate_attribute_results
from evaluation.RelationshipResultAggregator import aggregate_relationship_results


def find_stats(actual, predicted):
    correct_correct = 0
    correct_incorrect = 0
    correct_noMatch = 0
    correct_inconclusive = 0

    incorrect_correct = 0
    incorrect_incorrect = 0
    incorrect_noMatch = 0
    incorrect_inconclusive = 0

    extra_correct = 0
    extra_incorrect = 0
    extra_noMatch = 0
    extra_inconclusive = 0

    for a, p in zip(actual, predicted):
        if a == 'correct':
            if p == 'wrong':
                correct_incorrect += 1
            elif p == 'no_match':
                correct_noMatch += 1
            elif p == 'inconclusive':
                correct_inconclusive += 1
            elif p == 'correct':
                correct_correct += 1
        elif a == 'wrong':
            if p == 'wrong':
                incorrect_incorrect += 1
            elif p == 'no_match':
                incorrect_noMatch += 1
            elif p == 'inconclusive':
                incorrect_inconclusive += 1
            elif p == 'correct':
                incorrect_correct += 1
        elif a == 'extra':
            if p == 'wrong':
                extra_incorrect += 1
            elif p == 'no_match':
                extra_noMatch += 1
            elif p == 'inconclusive':
                extra_inconclusive += 1
            elif p == 'correct':
                extra_correct += 1

    return {
        'correct_and_correct': correct_correct,
        'correct_and_incorrect': correct_incorrect,
        'correct_and_noMatch': correct_noMatch,
        'correct_and_inconclusive': correct_inconclusive,
        'incorrect_and_correct': incorrect_correct,
        'incorrect_and_incorrect': incorrect_incorrect,
        'incorrect_and_noMatch': incorrect_noMatch,
        'incorrect_and_inconclusive': incorrect_inconclusive,
        'extra_and_correct': extra_correct,
        'extra_and_incorrect': extra_incorrect,
        'extra_and_noMatch': extra_noMatch,
        'extra_and_inconclusive': extra_inconclusive
    }


def divide(dividend, divisor):
    if divisor == 0 and dividend == 0:
        return 1
    elif divisor == 0:
        return 0
    else:
        return dividend / divisor


def find_metrics_values(detailed_results):
    results = pd.DataFrame(
        columns=['model_element', 'alignments_identified_and_correct', 'alignments_predicted_correct',
                 'misalignments_identified_and_correct', 'misalignments_predicted_correct',
                 'alignments', 'misalignments', 'precision_alignment', 'precision_misalignment',
                 'overall_precision', 'recall_alignment', 'recall_misalignment', 'overall_recall'])

    for i, row in detailed_results.iterrows():
        model_element = row['model_element']

        # Precision for alignment
        alignments_identified_and_correct = row['correct_and_correct']
        alignments_predicted_correct = (row['correct_and_correct'] + row['incorrect_and_correct'])
        precision_alignment = divide(alignments_identified_and_correct, alignments_predicted_correct)

        # Precision for misalignment
        misalignments_identified_and_correct = row['incorrect_and_incorrect']
        misalignments_predicted_correct = (row['correct_and_incorrect'] + row['incorrect_and_incorrect'])
        precision_misalignment = divide(misalignments_identified_and_correct, misalignments_predicted_correct)

        # Overall precision
        overall_precision = divide((alignments_identified_and_correct + misalignments_identified_and_correct),
                                   (alignments_predicted_correct + misalignments_predicted_correct))

        # Recall for alignment
        alignments = (row['correct_and_correct'] + row['correct_and_incorrect'] + row['correct_and_noMatch'] +
                      row['correct_and_inconclusive'])
        recall_alignment = divide(alignments_identified_and_correct, alignments)

        # Recall for misalignment
        misalignments = (row['incorrect_and_correct'] + row['incorrect_and_incorrect'] + row['incorrect_and_noMatch'] +
                         row['incorrect_and_inconclusive'])
        recall_misalignment = divide(misalignments_identified_and_correct, misalignments)

        # Overall recall
        overall_recall = divide((alignments_identified_and_correct + misalignments_identified_and_correct),
                                (alignments + misalignments))

        results.loc[len(results)] = [model_element, alignments_identified_and_correct, alignments_predicted_correct,
                                     misalignments_identified_and_correct, misalignments_predicted_correct,
                                     alignments, misalignments, precision_alignment, precision_misalignment,
                                     overall_precision, recall_alignment, recall_misalignment, overall_recall]

    # Precision for all model elements together
    alignments_identified_and_correct = sum(results['alignments_identified_and_correct'])
    alignments_predicted_correct = sum(results['alignments_predicted_correct'])
    misalignments_identified_and_correct = sum(results['misalignments_identified_and_correct'])
    misalignments_predicted_correct = sum(results['misalignments_predicted_correct'])
    alignments = sum(results['alignments'])
    misalignments = sum(results['misalignments'])
    precision_alignment = divide(alignments_identified_and_correct, alignments_predicted_correct)
    precision_misalignment = divide(misalignments_identified_and_correct, misalignments_predicted_correct)
    overall_precision = divide((alignments_identified_and_correct + misalignments_identified_and_correct),
                               (alignments_predicted_correct + misalignments_predicted_correct))

    # Recall for all model elements together
    recall_alignment = divide(alignments_identified_and_correct, alignments)
    recall_misalignment = divide(misalignments_identified_and_correct, misalignments)
    overall_recall = divide((alignments_identified_and_correct + misalignments_identified_and_correct),
                            (alignments + misalignments))

    results.loc[len(results)] = ['all', alignments_identified_and_correct, alignments_predicted_correct,
                                 misalignments_identified_and_correct, misalignments_predicted_correct,
                                 alignments, misalignments, precision_alignment, precision_misalignment,
                                 overall_precision, recall_alignment, recall_misalignment, overall_recall]

    return results
    # total_elements = 0
    # for ele in row.values():
    #     if isinstance(ele, int):
    #         total_elements += ele
    #
    # no_prediction = (row['correct_and_noMatch'] + row['correct_and_inconclusive'] +
    #                  row['incorrect_and_noMatch'] + row['incorrect_and_inconclusive'] +
    #                  row['extra_and_noMatch'] + row['extra_and_inconclusive'])
    #
    # have_prediction = total_elements - no_prediction
    #
    # if have_prediction == 0:
    #     predicted_right = 0
    #     predicted_wrong = 0
    # else:
    #     predicted_right = (row['correct_and_correct'] + row['incorrect_and_incorrect']) / have_prediction
    #     predicted_wrong = (row['correct_and_incorrect'] + row['incorrect_and_correct']) / have_prediction
    #
    # correct = (row['correct_and_correct'] + row['correct_and_incorrect'] +
    #            row['correct_and_noMatch'] + row['correct_and_inconclusive'])
    #
    # if correct == 0:
    #     correct_not_classified = 0
    # else:
    #     correct_not_classified = (row['correct_and_noMatch'] + row['correct_and_inconclusive']) / correct
    #
    # incorrect = (row['incorrect_and_correct'] + row['incorrect_and_incorrect'] +
    #              row['incorrect_and_noMatch'] + row['incorrect_and_inconclusive'])
    #
    # if incorrect == 0:
    #     incorrect_not_classified = 0
    # else:
    #     incorrect_not_classified = (row['incorrect_and_noMatch'] + row['incorrect_and_inconclusive']) / incorrect
    #
    # return {
    #     'domain': row['domain'],
    #     'model_element': row['model_element'],
    #     'have_prediction': have_prediction / total_elements,
    #     'no_prediction': no_prediction / total_elements,
    #     'predicted_right': predicted_right,
    #     'predicted_wrong': predicted_wrong,
    #     'correct_not_classified': correct_not_classified,
    #     'incorrect_not_classified': incorrect_not_classified
    # }


def format_result(result):
    for i, row in result.iterrows():
        if row['contradiction'] == True:
            result.at[i,'answer'] = 'wrong'
        elif row['equality'] == True or row['inclusion'] == True:
            result.at[i,'answer'] = 'correct'
        elif row['actual_sentence'] == '':
            result.at[i,'answer'] = 'no match'
        else:
            result.at[i,'answer'] = 'inconclusive'

    return result


def calculate_metrics(domain_name, results_dir):
    ground_truth_dir = f'{results_dir}/ground-truth/{domain_name}/'
    predictions_dir = f'{results_dir}/predictions/{domain_name}/'
    model_elements = ['attribute', 'association', 'aggregation', 'composition', 'inheritance', 'enum']

    combined_results_csv = f"{results_dir}/results.csv"
    if not os.path.exists(combined_results_csv):
        combined_results_csv = pd.DataFrame(
            columns=['model', 'alignments_identified_and_correct', 'alignments_predicted_correct',
                     'misalignments_identified_and_correct', 'misalignments_predicted_correct',
                     'alignments', 'misalignments', 'precision_alignment', 'precision_misalignment',
                     'overall_precision', 'recall_alignment', 'recall_misalignment', 'overall_recall'])
    else:
        combined_results_csv = pd.read_csv(f"{combined_results_csv}")

    # attributes, enums = aggregate_attribute_results(predictions_dir)
    # associations, aggregations, compositions, inheritance = aggregate_relationship_results(predictions_dir)

    attributes = pd.read_csv(f"{predictions_dir}/attributes_pred_map.csv")
    associations = pd.read_csv(f"{predictions_dir}/associations_pred_map.csv")
    aggregations = pd.read_csv(f"{predictions_dir}/aggregations_pred_map.csv")
    compositions = pd.read_csv(f"{predictions_dir}/compositions_pred_map.csv")
    inheritance = pd.read_csv(f"{predictions_dir}/inheritance_pred_map.csv")
    enums = pd.read_csv(f"{predictions_dir}/enums_pred_map.csv")

    attributes = format_result(attributes)
    associations = format_result(associations)
    aggregations = format_result(aggregations)
    compositions = format_result(compositions)
    inheritance= format_result(inheritance)
    enums = format_result(enums)

    predictions = [attributes, associations, aggregations, compositions, inheritance, enums]
    detailed_results = pd.DataFrame(
        columns=['domain', 'model_element', 'correct_and_correct', 'correct_and_incorrect', 'correct_and_noMatch',
                 'correct_and_inconclusive', 'incorrect_and_correct',
                 'incorrect_and_incorrect', 'incorrect_and_noMatch',
                 'incorrect_and_inconclusive', 'extra_and_correct',
                 'extra_and_incorrect', 'extra_and_noMatch', 'extra_and_inconclusive'])

    if os.path.isdir(ground_truth_dir):

        ground_truth_attributes = pd.read_csv(f"{ground_truth_dir}/attributes_results.csv")
        ground_truth_associations = pd.read_csv(f"{ground_truth_dir}/associations_results.csv")
        ground_truth_aggregations = pd.read_csv(f"{ground_truth_dir}/aggregations_results.csv")
        ground_truth_compositions = pd.read_csv(f"{ground_truth_dir}/compositions_results.csv")
        ground_truth_inheritance = pd.read_csv(f"{ground_truth_dir}/inheritance_results.csv")
        ground_truth_enums = pd.read_csv(f"{ground_truth_dir}/enums_results.csv")

        ground_truth = [ground_truth_attributes, ground_truth_associations, ground_truth_aggregations,
                        ground_truth_compositions, ground_truth_inheritance, ground_truth_enums]
        for model_element, actual, pred in zip(model_elements, ground_truth, predictions):
            stats = find_stats(list(actual['answer']), list(pred['answer']))
            stats['domain'] = domain_name
            stats['model_element'] = model_element
            detailed_results = pd.concat([detailed_results, pd.DataFrame([stats])])

        results = find_metrics_values(detailed_results)
        last_row = results.iloc[-1]
        last_row['model_element'] = domain_name
        combined_results_csv.loc[len(combined_results_csv)] = list(last_row)

        detailed_results.to_csv(f"{predictions_dir}/detailed_results_{domain_name}.csv", index=False)
        results.to_csv(f"{predictions_dir}/results_{domain_name}.csv", index=False)
        combined_results_csv.to_csv(f"{results_dir}/results.csv", index=False)


domains = ["R1-restaurant", "R2-employee-management-system", "R3-library", "R4-computer-game1",
           "R6-academic-program", "R7-supermarket", "R8-hotel-reservation", "R9-be-well-app",
           "R10-file-manager", "R11-football-team", "R12-car-gallery-management", "R13-course-enrollment",
           "R14-atm", "R15-video-rental", "R16-cinema", "R17-timbered-house",
           "R18-musical-store", "R19-airport", "R20-monitoring-pressure", "R21-savings-account",
           "R22-IPO-application", "R23-set-pin", "R25-apple-pay", "R26-block-card",
           "R27-biometric-login", "R28-donation", ]


for domain in domains:
    calculate_metrics(domain, "../final_evaluation_misalignment")
