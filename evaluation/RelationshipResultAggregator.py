import os

import numpy as np
import pandas as pd


def find_common_answer(lst):
    ans = False
    for ele in lst:
        if isinstance(ele, bool):
            ans = ans | ele

    return ans


def change_col(val):
    if val == 'TRUE' or val == 'True':
        return True
    elif val == 'FALSE' or val == 'False':
        return False
    return val


def process_group_rel(group):
    result = {
        'source': group['source'].iloc[0],
        'target': group['target'].iloc[0],
        'role': group['role'].iloc[0],
        'generated_sentence': group['generated_description'].iloc[0],
        'actual_sentence': group['actual_description'].iloc[0],
        'equality': find_common_answer(list(group['equality'])),
        'contradiction': find_common_answer(list(group['contradiction'])),
        'inclusion': find_common_answer(list(group['inclusion']))
    }

    # Choosing the actual sentence
    # valid_sentences = group[is_valid((group['equality']) , (group['contradiction']) , (group['inclusion']))]
    # result['actual_sentence'] = valid_sentences['actual_description'].iloc[0] if not valid_sentences.empty else 'no match'

    # Determining the answer column value
    if result['contradiction'] == True:
        result['answer'] = 'wrong'
    elif result['equality'] == True or result['inclusion'] == True:
        result['answer'] = 'correct'
    elif result['actual_sentence'] == '':
        result['answer'] = 'no match'
    else:
        result['answer'] = 'inconclusive'

    return pd.DataFrame([result])


def group_results_rel(df, col1, col2, col3='role'):
    result = []
    unique_keys = df[[col1, col2, col3]].drop_duplicates()

    for _, keys in unique_keys.iterrows():
        group = df[(df[col1] == keys[col1]) &
                   (df[col2] == keys[col2]) &
                   ((df[col3] == keys[col3]) | (df[col3].isna() & pd.isna(keys[col3])))].copy()
        processed_group = process_group_rel(group)
        result.append(processed_group)

    new_df = pd.concat(result, ignore_index=False)
    return new_df


def aggregate_relationship_results(folder_path):
    new_columns = ['equality', 'contradiction', 'inclusion', 'answer']
    try:
        if os.path.isdir(folder_path):

            df = pd.read_csv(f"{folder_path}/associations_pred_map.csv")
            if not df.empty:
                df['equality'] = df['equality'].apply(change_col)
                df['contradiction'] = df['contradiction'].apply(change_col)
                df['inclusion'] = df['inclusion'].apply(change_col)
                associations = group_results_rel(df, 'source', 'target')
                associations['kind'] = 'association'
            else:
                associations = pd.DataFrame(columns=list(df.columns)+new_columns)

            df = pd.read_csv(f"{folder_path}/aggregations_pred_map.csv")
            if not df.empty:
                df['equality'] = df['equality'].apply(change_col)
                df['contradiction'] = df['contradiction'].apply(change_col)
                df['inclusion'] = df['inclusion'].apply(change_col)
                aggregations = group_results_rel(df, 'source', 'target')
                aggregations['kind'] = 'aggregation'
            else:
                aggregations = pd.DataFrame(columns=list(df.columns) + new_columns)

            df = pd.read_csv(f"{folder_path}/compositions_pred_map.csv")
            if not df.empty:
                df['equality'] = df['equality'].apply(change_col)
                df['contradiction'] = df['contradiction'].apply(change_col)
                df['inclusion'] = df['inclusion'].apply(change_col)
                compositions = group_results_rel(df, 'source', 'target')
                compositions['kind'] = 'composition'
            else:
                compositions = pd.DataFrame(columns=list(df.columns) + new_columns)

            df = pd.read_csv(f"{folder_path}/inheritance_pred_map.csv")
            if not df.empty:
                df['equality'] = df['equality'].apply(change_col)
                df['contradiction'] = df['contradiction'].apply(change_col)
                df['inclusion'] = df['inclusion'].apply(change_col)
                inheritance = group_results_rel(df, 'source', 'target')
                inheritance['kind'] = 'inheritance'
            else:
                inheritance = pd.DataFrame(columns=list(df.columns) + new_columns)

            return associations, aggregations, compositions, inheritance

    except Exception as e:
        raise Exception(e)
    # try:
    #     for folder_name in os.listdir(parent_folder):
    #         folder_path = os.path.join(parent_folder, folder_name)
    #         if os.path.isdir(folder_path):
    #             answer = pd.DataFrame(
    #                 columns=['source', 'target', 'role', 'kind', 'generated_sentence', 'actual_sentence', 'equality',
    #                          'contradiction', 'inclusion', 'answer'])
    #
    #             df = pd.read_csv(f"{parent_folder}/{folder_name}/associations_pred_map.csv")
    #             if not df.empty:
    #                 df['equality'] = df['equality'].apply(change_col)
    #                 df['contradiction'] = df['contradiction'].apply(change_col)
    #                 df['inclusion'] = df['inclusion'].apply(change_col)
    #                 processed_df = group_results_rel(df, 'source', 'target')
    #                 processed_df['kind'] = 'association'
    #                 answer = pd.concat([answer, processed_df])
    #
    #             df = pd.read_csv(f"{parent_folder}/{folder_name}/aggregations_pred_map.csv")
    #             if not df.empty:
    #                 df['equality'] = df['equality'].apply(change_col)
    #                 df['contradiction'] = df['contradiction'].apply(change_col)
    #                 df['inclusion'] = df['inclusion'].apply(change_col)
    #                 processed_df = group_results_rel(df, 'source', 'target')
    #                 processed_df['kind'] = 'aggregation'
    #                 answer = pd.concat([answer, processed_df])
    #
    #             df = pd.read_csv(f"{parent_folder}/{folder_name}/compositions_pred_map.csv")
    #             if not df.empty:
    #                 df['equality'] = df['equality'].apply(change_col)
    #                 df['contradiction'] = df['contradiction'].apply(change_col)
    #                 df['inclusion'] = df['inclusion'].apply(change_col)
    #                 processed_df = group_results_rel(df, 'source', 'target')
    #                 processed_df['kind'] = 'composition'
    #                 answer = pd.concat([answer, processed_df])
    #
    #             df = pd.read_csv(f"{parent_folder}/{folder_name}/inheritance_pred_map.csv")
    #             if not df.empty:
    #                 df['equality'] = df['equality'].apply(change_col)
    #                 df['contradiction'] = df['contradiction'].apply(change_col)
    #                 df['inclusion'] = df['inclusion'].apply(change_col)
    #                 processed_df = group_results_rel(df, 'source', 'target')
    #                 processed_df['kind'] = 'inheritance'
    #                 answer = pd.concat([answer, processed_df])
    #
    #             if not os.path.exists(rf"{results_folder}/predictions/{folder_name}"):
    #                 os.makedirs(f"{results_folder}/predictions/{folder_name}")
    #
    #             answer.to_csv(f"{results_folder}/predictions/{folder_name}/relationship_results.csv", index=False)
    # except Exception as e:
    #     raise Exception(e)

# aggregate_relationship_results()
