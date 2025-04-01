import xml.etree.ElementTree as ET


def get_upper_bound(upper_bound):
    if upper_bound == '-1':
        return '*'
    else:
        return upper_bound


def parse_domain_model(xml_file_path):
    # Parse the XML file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()

    # Extract namespaces
    namespaces = {
        'classdiagram': 'http://cs.mcgill.ca/sel/cdm/1.0',
        'xmi': 'http://www.omg.org/XMI',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }

    xsi_id = '{http://www.w3.org/2001/XMLSchema-instance}type'
    xmi_id = '{http://www.omg.org/XMI}id'

    class_attributes = {}
    associations = []
    inheritance = []
    compositions = []
    aggregations = []

    composition_ids_map = {}
    relationships_map = {}
    aggregation_ids_map = {}
    inheritance_map = {}
    attribute_types_map = {}
    class_id_map = {}
    enums = {}

    print("\nTypes:")
    for type_elem in root.findall('types', namespaces):
        type_name = type_elem.get(xsi_id).split(':')[-1]
        type_name = type_name.split("CD")[-1]
        type_id = type_elem.get(xmi_id)
        # print(f"Type: {type_name}, Type ID: {type_id}")
        attribute_types_map[type_id] = type_name

        if type_name == "Enum":
            name = type_elem.get('name')
            constants = []
            for enum_type_elem in type_elem.findall('literals'):
                constant = enum_type_elem.get('name')
                constants.append(constant)

            enums[name] = constants

    print(attribute_types_map)

    print("\nEnums:")
    print(enums)

    # Extract classes and their attributes and associations
    print("\nClasses and their attributes:")

    for class_elem in root.findall('classes', namespaces):
        class_name = class_elem.get('name')
        super_type = class_elem.get('superTypes')
        class_xmi_id = class_elem.get(xmi_id)
        class_id_map[class_xmi_id] = class_name

        if super_type is not None:
            if super_type in inheritance_map:
                subclasses = inheritance_map[super_type]
                subclasses.append(class_name)
            else:
                subclasses = [class_name]
                inheritance_map[super_type] = subclasses

        # print(f"Class: {class_name}")
        attributes_list = []
        for attr_elem in class_elem.findall('attributes', namespaces):
            attr_name = attr_elem.get('name')
            attr_type = attr_elem.get('type')
            # print(f"  Attribute: {attr_name}, Type: {attr_type}")
            # Without type:
            # attributes_list.append(attr_name)

            # With type: TODO Remove this if check, this was added for dates. As of now attribute with date datatype
            #  is not supported
            if attr_type in attribute_types_map:
                attributes_list.append(attr_name + ":" + attribute_types_map[attr_type])
        class_attributes[class_name] = attributes_list

        for assoc_end_elem in class_elem.findall('associationEnds', namespaces):
            assoc_name = assoc_end_elem.get('name')
            lower_bound = assoc_end_elem.get('lowerBound')
            upper_bound = assoc_end_elem.get('upperBound')
            assoc_id = assoc_end_elem.get(xmi_id)

            # For composition and aggregations
            referenceType = assoc_end_elem.get('referenceType')
            if referenceType is not None:
                assoc = assoc_end_elem.get('assoc')

                if referenceType == 'Composition':
                    composition_ids_map[assoc] = class_name
                elif referenceType == 'Aggregation':
                    aggregation_ids_map[assoc] = class_name

            # print(f"  Association: {assoc_name}, Association ID: {assoc_id}")

            if lower_bound is None and upper_bound is None:
                cardinality = ''
            elif lower_bound is not None:
                cardinality = lower_bound

                if upper_bound is not None:
                    cardinality += '..' + get_upper_bound(upper_bound)

                if int(lower_bound) == 0 and upper_bound is None:
                    cardinality += '..*'
            elif lower_bound is None:
                cardinality = '0..' + get_upper_bound(upper_bound)

            relationships_map[assoc_id] = {
                'assoc_name': assoc_name,
                'cardinality': cardinality
            }

    print(class_attributes)

    # Extract inheritance
    for key, value in inheritance_map.items():
        obj = {
            'parent_class': class_id_map[key],
            'child_classes': value
        }
        inheritance.append(obj)

    # Extract associations
    print("\nAssociations:")
    for assoc_elem in root.findall('associations', namespaces):
        assoc_name = assoc_elem.get('name')
        assoc_ends = assoc_elem.get('ends')
        assoc_xml_id = assoc_elem.get(xmi_id)

        # print(f"Association: {assoc_name}, Ends: {assoc_ends}")
        class_names = assoc_name.split("_")
        assoc_ends = assoc_ends.split(" ")

        if assoc_xml_id in composition_ids_map:
            parent_class = composition_ids_map[assoc_xml_id]
            cardinality1 = relationships_map[assoc_ends[1]]['cardinality']
            cardinality2 = relationships_map[assoc_ends[0]]['cardinality']

            role1 = relationships_map[assoc_ends[1]]['assoc_name']
            role2 = relationships_map[assoc_ends[0]]['assoc_name']

            composition = {
                    'parent_class': parent_class,
                    'child_class': class_names[0] if class_names[1] == parent_class else class_names[1],
                    'cardinality': cardinality1 if cardinality1 is not None else cardinality2,
                    'role': role1 if role1 is not None else role2
                }
            compositions.append(composition)

        elif assoc_xml_id in aggregation_ids_map:
            parent_class = aggregation_ids_map[assoc_xml_id]
            cardinality1 = relationships_map[assoc_ends[1]]['cardinality']
            cardinality2 = relationships_map[assoc_ends[0]]['cardinality']

            role1 = relationships_map[assoc_ends[1]]['assoc_name']
            role2 = relationships_map[assoc_ends[0]]['assoc_name']

            aggregation = {
                'parent_class': parent_class,
                'child_class': class_names[0] if class_names[1] == parent_class else class_names[1],
                'cardinality': cardinality1 if cardinality1 is not None else cardinality2,
                'role': role1 if role1 is not None else role2
            }
            aggregations.append(aggregation)

        else:
            association = {
                'class1': class_names[0],
                'class2': class_names[1],
                'role_class1': relationships_map[assoc_ends[1]]['assoc_name'],
                'role_class2': relationships_map[assoc_ends[0]]['assoc_name'],
                'cardinality_class1': relationships_map[assoc_ends[1]]['cardinality'],
                'cardinality_class2': relationships_map[assoc_ends[0]]['cardinality']
            }
            associations.append(association)

    print(associations)

    return class_attributes, associations, compositions, aggregations, inheritance, enums


# xml_file_path = '../tests/domain-models/cdm-models/production-cell-enum.cdm'
#
# parse_domain_model(xml_file_path)
