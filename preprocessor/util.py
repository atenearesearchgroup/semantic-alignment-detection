from collections import Counter

import pandas as pd

from sentence_generator import util

noun_tags = ["JJ", "JJR", "JJS", "NN", "NNS", "NNP"]


def is_role_included(role, lemma, language_model):
    if pd.isna(role):
        return False

    role = " ".join([item.lower() for item in util.split_camel_case(role)])
    role_lm = language_model(role)
    for token in role_lm:
        if token.tag_ not in noun_tags:
            return False

    if role in lemma:
        return True

    return False


def find_intersection_or_most_common(data):
    # Get the intersection of all sets
    sets = list(data.values())
    intersection = set.intersection(*sets) if sets else set()

    if intersection:
        return intersection  # Return intersection if not empty

    # Flatten all values into a single list
    all_values = [val for s in sets for val in s]

    if len(all_values) != 0:
        # Find the most common value
        counter = Counter(all_values)
        max_frequency = max(counter.values())  # Find the highest frequency
        most_common_values = {key for key, value in counter.items() if value == max_frequency}
        return set(most_common_values)  # Return as a set

    return set()


def find_combinations_of_noun(noun):
    combinations_of_noun = {}

    parts = util.split_camel_case(noun)

    if len(parts) == 1:
        combinations_of_noun[noun] = set()
        return combinations_of_noun

    for i in range(0, len(parts) - 1):
        for j in range(i + 1, len(parts)):
            combinations_of_noun[parts[i] + " " + parts[j]] = set()

    return combinations_of_noun


def find_matching_description(source, target, source_role, target_role, associations, concepts, sentences,
                              language_model, is_inheritance=True):
    extracted_sentence_ids = set()

    if is_inheritance:
        parent_class_parts = util.split_camel_case(source)
        child_class_parts = util.split_camel_case(target)

        if len(parent_class_parts) > 1 and parent_class_parts[-1] == child_class_parts[-1]:
            source = " ".join(parent_class_parts[0:-1])
            target = " ".join(child_class_parts[0:-1])

    for i, relationship in associations.iterrows():
        rel_source = relationship['source'].lower()
        rel_target = relationship['target'].lower()

        if rel_source in source and rel_target in target:
            extracted_sentence_ids.add(relationship['sdx'])

        elif rel_source in source and pd.notna(target_role) and rel_target in target_role:
            extracted_sentence_ids.add(relationship['sdx'])

        elif rel_target in target and pd.notna(source_role) and rel_source in source_role:
            extracted_sentence_ids.add(relationship['sdx'])

        elif (pd.notna(target_role) and rel_target in target_role and
              pd.notna(source_role) and rel_source in source_role):
            extracted_sentence_ids.add(relationship['sdx'])

    if len(extracted_sentence_ids) == 0:
        source_presence_set = set()
        target_presence_set = set()

        # TODO Following part of code tries to make different combinations of source or target noun and find relevant
        #  sentences. e.g. for LifeInsuranceContract, it will make 3 chunks, life insurance, insurance contract and
        #  life contract. Find relevant sentences for each chunk and take most common form them.
        #  source_parts_dict = find_combinations_of_noun(source)
        #  target_parts_dict = find_combinations_of_noun(target)

        for i, sent in enumerate(sentences):
            sent_doc = language_model(sent)
            for chunks in sent_doc.noun_chunks:
                if source in chunks.lemma_ or is_role_included(source_role, chunks.lemma_, language_model):
                    source_presence_set.add("S" + str(i))

                if target in chunks.lemma_ or is_role_included(target_role, chunks.lemma_, language_model):
                    target_presence_set.add("S" + str(i))

                # for key in source_parts_dict.keys():
                #     if key in chunks.lemma_:
                #         source_parts_dict[key].add("S" + str(i))
                #
                # for key in target_parts_dict.keys():
                #     if key in chunks.lemma_:
                #         target_parts_dict[key].add("S" + str(i))

        # if len(source_presence_set) == 0 and len(source_parts_dict) > 1:
        #     source_presence_set = find_intersection_or_most_common(source_parts_dict)
        #
        # if len(target_presence_set) == 0 and len(target_parts_dict) > 1:
        #     target_presence_set = find_intersection_or_most_common(target_parts_dict)

        if len(source_presence_set) == 0:
            res = language_model(source)
            nouns_in_source = {}
            for token in res:
                if token.tag_ in noun_tags:
                    nouns_in_source[token.text.lower()] = set()

            for i, token in concepts.iterrows():
                token_str = token['token'].lower_
                lemma_str = token['lemmatized_text'].lower()

                for key in nouns_in_source.keys():
                    if token_str == key or lemma_str == key:
                        nouns_in_source[key].add(token['s_id'])

                if token_str == source_role or lemma_str == source_role:
                    source_presence_set.add(token['s_id'])

            if len(source_presence_set) == 0:
                source_presence_set = find_intersection_or_most_common(nouns_in_source)

            # for token in res:
            #     if token.head == token:
            #         source_head = token.text.lower()
            #         break

            # for i, token in concepts.iterrows():
            #     token_str = token['token'].lower_
            #     lemma_str = token['lemmatized_text'].lower()
            #
            #     if (token_str == source or lemma_str == source or
            #             token_str == source_head or lemma_str == source_head or
            #             token_str == source_role or lemma_str == source_role):
            #         source_presence_set.add(token['s_id'])

        if len(target_presence_set) == 0:
            res = language_model(target)
            nouns_in_target = {}
            for token in res:
                if token.tag_ in noun_tags:
                    nouns_in_target[token.text.lower()] = set()

            for i, token in concepts.iterrows():
                token_str = token['token'].lower_
                lemma_str = token['lemmatized_text'].lower()

                for key in nouns_in_target.keys():
                    if token_str == key or lemma_str == key:
                        nouns_in_target[key].add(token['s_id'])

                if token_str == target_role or lemma_str == target_role:
                    target_presence_set.add(token['s_id'])

            if len(target_presence_set) == 0:
                target_presence_set = find_intersection_or_most_common(nouns_in_target)

            # res = language_model(target)
            # for token in res:
            #     if token.head == token:
            #         target_head = token.text.lower()
            #         break
            #
            # for i, token in concepts.iterrows():
            #     token_str = token['token'].lower_
            #     lemma_str = token['lemmatized_text'].lower()
            #
            #     if (token_str == target or lemma_str == target
            #             or token_str == target_head or lemma_str == target_head or
            #             token_str == target_role or lemma_str == target_role):
            #         target_presence_set.add(token['s_id'])

        answer_set = source_presence_set & target_presence_set

        if len(answer_set) == 0:
            answer_set = source_presence_set | target_presence_set
        extracted_sentence_ids.update(answer_set)

    return extracted_sentence_ids
