import pandas as pd

from preprocessor import util


class RelationshipMatcher:
    def flatten_list(self, nested_list):
        flat_list = []
        for element in nested_list:
            if isinstance(element, list):
                flat_list.extend(self.flatten_list(element))
            else:
                flat_list.append(element)
        return flat_list

    def create_relationships_map(self, attributes_description, relationship_description, relationships,
                                 sentences,
                                 concepts, language_model):
        data = pd.DataFrame(
            columns=['source', 'target', 'role', 'multiplicity', 'generated_description', 'actual_description'])

        all_sentence_ids = set()
        for sdx in range(len(sentences)):
            all_sentence_ids.add("S" + str(sdx))

        for index, row in relationship_description.iterrows():
            source = row['source'].lower()
            target = row['target'].lower()
            role = row['role']
            multiplicity = row.get('multiplicity', '')
            actual_sentence_ids = util.find_matching_description(source, target, row['source_role'], role,
                                                                 relationships, concepts, sentences, language_model)
            # for i, relationship in relationships.iterrows():
            #     # TODO add check for role
            #     rel_source = relationship['source'].lower()
            #     rel_target = relationship['target'].lower()
            #
            #     if rel_source in source and rel_target in target:
            #         # or (rel_target in source and rel_source in target)):
            #         # sdx = relationship['sdx'].replace("S", '')
            #         actual_sentence_ids.add(relationship['sdx'])
            #
            #     elif rel_source in source and rel_target in role:
            #         # or (rel_target in source and rel_source in role)):
            #         actual_sentence_ids.add(relationship['sdx'])
            #
            # if len(actual_sentence_ids) == 0:
            #     source_presence_set = set()
            #     target_presence_set = set()
            #     # res = language_model(source)
            #     # for token in res:
            #     #     if token.head == token:
            #     #         source_head = token.text.lower()
            #     #         break
            #     #
            #     # res = language_model(target)
            #     # for token in res:
            #     #     if token.head == token:
            #     #         target_head = token.text.lower()
            #     #         break
            #     #
            #
            #     # for i, token in concepts.iterrows():
            #     #     token_str = token['token'].lower_
            #     #     lemma_str = token['lemmatized_text'].lower()
            #     #
            #     #     if (token_str == source or lemma_str == source or
            #     #             token_str == source_head or lemma_str == source_head):
            #     #         source_presence_set.add(token['s_id'])
            #     #
            #     #     elif (token_str == target or lemma_str == target
            #     #           or token_str == target_head or lemma_str == target_head or
            #     #           token_str == role or lemma_str == role):
            #     #         target_presence_set.add(token['s_id'])
            #
            #     for i, sent in enumerate(sentences):
            #         sent_doc = language_model(sent)
            #         for chunks in sent_doc.noun_chunks:
            #             if source in chunks.lemma_:
            #                 source_presence_set.add("S" + str(i))
            #
            #             if target in chunks.lemma_:
            #                 target_presence_set.add("S" + str(i))
            #
            #         # if source in sent:
            #         #     source_presence_set.add("S" + str(i))
            #         #
            #         # if target in sent:
            #         #     target_presence_set.add("S" + str(i))
            #
            #     answer_set = source_presence_set & target_presence_set
            #
            #     if len(answer_set) == 0:
            #         answer_set = source_presence_set | target_presence_set
            #     actual_sentence_ids.update(answer_set)

            if len(actual_sentence_ids) == 0:
                actual_sentence_ids = all_sentence_ids

            actual_sentences = [sentences[int(idx.replace("S", ""))] for idx in actual_sentence_ids]
            for sentence in actual_sentences:
                data.loc[len(data)] = [source, target, role, multiplicity, row['sentence'], sentence]

            if len(actual_sentences) == 0:
                data.loc[len(data)] = [source, target, role, multiplicity, row['sentence'], ""]

        return data
