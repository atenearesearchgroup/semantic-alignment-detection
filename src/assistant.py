# nltk.download('averaged_perceptron_tagger_eng')

import os
import sys

from evaluation.ResultAggregator import calculate_metrics
from preprocessor.attribute_matcher import AttributeMatcher
from preprocessor.relationship_matcher import RelationshipMatcher

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from preprocessor import coreferenceResolution as coref
from src.descriptionReader import DescriptionReader
from extractor.RelationshipExtractor import RelationshipsExtractor
from extractor.conceptsExtractor import ConceptsExtractor
from sentence_generator.descriptionGenerator import DescriptionGenerator
from workflow.workflowStart import WorkflowStart
import spacy

from contextlib import contextmanager
import time


@contextmanager
def timer(label, file_path):
    start_time = time.perf_counter()
    yield
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"{label} took {elapsed_time:.6f} seconds")
    log_entry = f"{label} took {elapsed_time:.6f} seconds\n"

    # Append execution time to file
    with open(file_path, "a") as f:
        f.write(log_entry)


class Assistant:
    def __init__(self, domain_name, results_dir):
        self.enum_map = None
        self.compositions_map = None
        self.aggregations_map = None
        self.associations_map = None
        self.attributes_map = None
        self.inheritance_map = None
        self.errors = []
        self.warnings = []
        self.language_model = spacy.load("en_core_web_trf")
        self.results_dir = results_dir
        self.description_reader = DescriptionReader(domain_name)

        # TODO Redundant part
        self.domain_name = domain_name

        self.log_file_path = f"{results_dir}//predictions//{self.domain_name}//domain_logs.txt"
        if not os.path.exists(rf"{results_dir}//predictions//{self.domain_name}"):
            os.makedirs(f"{results_dir}//predictions//{self.domain_name}")

        if not os.path.exists(self.log_file_path):
            with open(self.log_file_path, "w") as f:
                f.write("Execution Time Log\n")

        with timer("Sentence Generation", self.log_file_path):
            self.description_generator = DescriptionGenerator(domain_name, self.language_model)

        self.concepts_extractor = ConceptsExtractor()
        self.relationships_extractor = RelationshipsExtractor()

        # Tokenizer treats 'id' as I'd and that's why it gets split as 'I' and 'd'.
        # but here I want it to be a single word, hence removing that rule.
        self.language_model.tokenizer.rules = {key: value for key, value in self.language_model.tokenizer.rules.items()
                                               if key != "id"}

        self.attribute_matcher = AttributeMatcher()
        self.relationships_matcher = RelationshipMatcher()

    def get_errors(self):
        return self.errors

    def get_warnings(self):
        return self.warnings

    def run(self):
        with timer("Concept and Relationship extraction", self.log_file_path):
            actual_description = self.description_reader.get_actual_description()
            sentences = [sent.strip() for sent in actual_description.split(".")]

            actual_description = actual_description.replace("e.g.", "")
            actual_description = actual_description.replace("i.e.", "")
            actual_description = actual_description.replace("etc.", "")

            original_description, sentences = coref.get_preprocessed_text(actual_description)

            for sdx, sent in enumerate(sentences):
                sdx = "S" + str(sdx)
                preprocessed_sent = sent.replace(".", "")
                self.concepts_extractor.extract_candidate_concepts(
                    self.language_model(preprocessed_sent), sdx
                )
                self.relationships_extractor.extract_candidate_relationships(
                    self.concepts_extractor.df_chunks,
                    self.concepts_extractor.df_concepts,
                    self.language_model,
                    self.language_model(preprocessed_sent),
                    sdx,
                )

        with timer("Semantic matching", self.log_file_path):
            self.attributes_map = self.attribute_matcher.create_attributes_map(
                self.description_generator.get_attributes(),
                self.concepts_extractor.df_concepts,
                original_description)

            self.associations_map = self.relationships_matcher.create_relationships_map(
                self.description_generator.get_attributes(),
                self.description_generator.get_associations(),
                self.relationships_extractor.df_class_associations,
                original_description, self.concepts_extractor.df_concepts,
                self.language_model)

            self.aggregations_map = self.relationships_matcher.create_relationships_map(
                self.description_generator.get_attributes(),
                self.description_generator.get_aggregations(),
                self.relationships_extractor.df_class_associations,
                original_description, self.concepts_extractor.df_concepts,
                self.language_model)

            self.compositions_map = self.relationships_matcher.create_relationships_map(
                self.description_generator.get_attributes(),
                self.description_generator.get_compositions(),
                self.relationships_extractor.df_class_associations,
                original_description, self.concepts_extractor.df_concepts,
                self.language_model)

            self.inheritance_map = self.relationships_matcher.create_relationships_map(
                self.description_generator.get_attributes(),
                self.description_generator.get_inheritance(),
                self.relationships_extractor.df_class_associations,
                original_description, self.concepts_extractor.df_concepts,
                self.language_model)

            self.enum_map = self.attribute_matcher.create_enum_map(
                self.description_generator.get_enums(),
                self.concepts_extractor.df_concepts,
                self.relationships_extractor.df_class_associations,
                original_description)

        with timer("LLM ", self.log_file_path):
            workflow = WorkflowStart(
                [self.attributes_map, self.associations_map, self.aggregations_map, self.compositions_map,
                 self.inheritance_map, self.enum_map], self.domain_name, self.results_dir)
            errors = workflow.run()

        with timer("Result calculation", self.log_file_path):
            calculate_metrics(self.domain_name, self.results_dir)

        print(errors)
        print("Done")


assistant = Assistant("R4-computer-game1", "../final_evaluation_misalignment")
assistant.run()
