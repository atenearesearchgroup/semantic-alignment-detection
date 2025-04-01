from functools import reduce

import pandas as pd


class AttributeMatcher:
    def create_attributes_map(self, attributes_description, concepts, actual_description):
        data = pd.DataFrame(columns=['class_name', 'attributes', 'generated_description', 'actual_description'])
        all_sentence_ids = set()
        for sdx in range(len(actual_description)):
            all_sentence_ids.add("S" + str(sdx))

        for index, row in attributes_description.iterrows():
            class_name = row['class'].lower()
            attribute_name = row['attribute'].lower()
            generated_sentence = row['sentence']
            actual_sentence_ids = set()

            attribute_presence_set = set()
            class_name_presence_set = set()

            attribute_name_separated = attribute_name.split(" ")
            attribute_presence_map = {}

            for i, token in concepts.iterrows():
                token_str = token['token'].lower_
                lemma_str = token['lemmatized_text'].lower()

                # if token_str in attribute_name or lemma_str in attribute_name.lower():
                #     attribute_presence_set.add(token['s_id'])

                for att in attribute_name_separated:
                    if token_str in att or lemma_str in att.lower():
                        if att not in attribute_presence_map:
                            attribute_presence_map[att] = []
                        attribute_presence_map[att].append(token['s_id'])

                if token_str in class_name.lower() or lemma_str in class_name.lower():
                    class_name_presence_set.add(token['s_id'])

            lists = attribute_presence_map.values()

            if not lists or all(len(lst) == 0 for lst in lists):
                attribute_presence_set = set([])
            else:
                attribute_presence_set = set(list(reduce(set.intersection, map(set, lists))))
                if not attribute_presence_set:
                    attribute_presence_set = set(list(set().union(*lists)))

            answer_set = attribute_presence_set & class_name_presence_set
            if len(answer_set) == 0:
                if len(attribute_presence_set) != 0:
                    answer_set = attribute_presence_set
                elif len(class_name_presence_set) != 0:
                    answer_set = class_name_presence_set
                else:
                    answer_set = all_sentence_ids

            actual_sentence_ids.update(answer_set)
            actual_sentences = [actual_description[int(idx.replace("S", ""))] for idx in actual_sentence_ids]
            for sentence in actual_sentences:
                data.loc[len(data)] = [class_name, attribute_name, generated_sentence, sentence]

            if len(actual_sentences) == 0:
                data.loc[len(data)] = [class_name, attribute_name, generated_sentence, ""]

        # print("Time for create attribute map ", (end-start)/60)
        return data

    def create_enum_map(self, enum_df, concepts, relationships, actual_description):
        data = pd.DataFrame(columns=['source', 'target', 'generated_description', 'actual_description'])
        all_sentence_ids = set()

        for sdx in range(len(actual_description)):
            all_sentence_ids.add("S" + str(sdx))

        for index, row in enum_df.iterrows():
            enum = row['enum'].lower()
            enum_member = row['enum_member'].lower()
            generated_sentence = row['sentence']
            actual_sentence_ids = set()

            enum_member_separated = enum_member.split(" ")
            enum_separated = enum.split(" ")

            enum_presence_map = {}
            enum_member_presence_map = {}

            for i, token in concepts.iterrows():
                token_str = token['token'].lower_
                lemma_str = token['lemmatized_text'].lower()

                # if token_str in attribute_name or lemma_str in attribute_name.lower():
                #     attribute_presence_set.add(token['s_id'])

                for att in enum_member_separated:

                    if token_str in att.lower() or lemma_str in att.lower():
                        if att not in enum_member_presence_map:
                            enum_member_presence_map[att] = []
                        enum_member_presence_map[att].append(token['s_id'])

                for att in enum_separated:
                    if token_str in att.lower() or lemma_str in att.lower():
                        if att not in enum_presence_map:
                            enum_presence_map[att] = []
                        enum_presence_map[att].append(token['s_id'])

            lists = enum_member_presence_map.values()
            if not lists or all(len(lst) == 0 for lst in lists):
                enum_member_presence_set = set([])
            else:
                enum_member_presence_set = set(list(reduce(set.intersection, map(set, lists))))
                if not enum_member_presence_set:
                    enum_member_presence_set = set(list(set().union(*lists)))

            lists = enum_presence_map.values()
            if not lists or all(len(lst) == 0 for lst in lists):
                enum_presence_set = set([])
            else:
                enum_presence_set = set(list(reduce(set.intersection, map(set, lists))))
                if not enum_presence_set:
                    enum_presence_set = set(list(set().union(*lists)))

            answer_set = enum_member_presence_set & enum_presence_set
            if len(answer_set) == 0:
                if len(enum_member_presence_set) != 0:
                    answer_set = enum_member_presence_set
                elif len(enum_presence_set) != 0:
                    answer_set = enum_presence_set
                else:
                    answer_set = all_sentence_ids

            actual_sentence_ids.update(answer_set)
            actual_sentences = [actual_description[int(idx.replace("S", ""))] for idx in actual_sentence_ids]
            for sentence in actual_sentences:
                data.loc[len(data)] = [enum, enum_member, generated_sentence, sentence]

            if len(actual_sentences) == 0:
                data.loc[len(data)] = [enum, enum_member, generated_sentence, ""]

        # print("Time for create attribute map ", (end-start)/60)
        return data
