from typing import List

import pandas as pd

from sentence_generator import util
from sentence_generator.abstractSentenceGenerator import AbstractSentenceGenerator


class SentenceFromEnums(AbstractSentenceGenerator):
    def __init__(self, enums, model):
        self.enums = enums
        self.language_model = model

        # TODO : Keep only one format either sentences list or 'attributes'  dataframe
        self.sentences = []
        self.enums_description = pd.DataFrame(columns=['enum', 'enum_member', 'sentence'])
        self.generate_sentences()

    def get_sentences(self) -> List[str]:
        return self.sentences

    def get_enums(self):
        return self.enums_description

    def generate_sentences(self):
        for enum, enum_members in self.enums.items():
            for enum_member in enum_members:
                # formatted_enum_member = util.format_concept(enum_member)
                # formatted_enum = util.split_camel_case(enum)
                #
                # sentence = formatted_enum_member + ' is one '
                # if formatted_enum[-1].lower() == 'kind':
                #     sentence += formatted_enum[-1].lower() + " of " + " ".join(formatted_enum[0:-1])
                # else:
                #     sentence += 'kind of ' + " ".join(formatted_enum)

                formatted_enum = util.format_concept(enum, self.language_model)
                formatted_enum_member = util.split_camel_case(enum_member)

                # formatted_enum_member = [item.lower() for item in formatted_enum_member]

                sentence = formatted_enum_member[0]
                for i in range(1, len(formatted_enum_member)):
                    sentence += " " + formatted_enum_member[i].lower()

                sentence += " is " + formatted_enum

                self.enums_description.loc[len(self.enums_description)] = [" ".join(util.split_camel_case(enum)),
                                                                           " ".join(util.split_camel_case(enum_member)),
                                                                           sentence]


prod_cell_enums = {
    'ProcessingUnitKind': ["Press", "Laser"],
    'TransportUnitKind': ['ConveyorBelt', 'RobotArm']
}

car_maint_enums = {
    'ServiceType': ['Maintenance', 'Repair']
}

insurance_enums = {
    'PaymentForm': ['Yearly', 'Monthly']
}

flight_res_enums = {
    'FlightClass': ['BusinessClass', 'FirstClass', 'EconomyClass'],
    'BookedFlightStatus': ['Booked', 'CheckedIn', 'Boarded']
}

hotel_system_enums = {
    'QualityLevel': ['Standard', 'StandardWithView', 'Superior', 'SuperiorWithView'],
    'SmokingStatus': ['Smoking', 'NonSmoking'],
    'BedType': ['Single', 'Double', 'Queen', 'King']
}

all_enums = {
    'ProcessingUnitKind': ["Press", "Laser"],
    'TransportUnitKind': ['ConveyorBelt', 'RobotArm'],
    'ServiceType': ['Maintenance', 'Repair'],
    'PaymentForm': ['Yearly', 'Monthly'],
    'FlightClass': ['BusinessClass', 'FirstClass', 'EconomyClass'],
    'BookedFlightStatus': ['Booked', 'CheckedIn', 'Boarded'],
    'QualityLevel': ['Standard', 'StandardWithView', 'Superior', 'SuperiorWithView'],
    'SmokingStatus': ['Smoking', 'NonSmoking'],
    'BedType': ['Single', 'Double', 'Queen', 'King'],
    'Alphabet': ['A', 'B', 'C', 'D']
}

# sfe = SentenceFromEnums(all_enums, language_model)
# print(sfe.get_enums())
