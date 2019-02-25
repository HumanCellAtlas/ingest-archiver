from flatten_json import flatten

ONTOLOGY_10x = "EFO:0009310"


def is_10x(library_preparation_protocol):
    content = library_preparation_protocol.get("content", {})
    library_const_approach_obj = content.get("library_construction_approach", {})
    library_const_approach = library_const_approach_obj.get('ontology')

    if library_const_approach and library_const_approach == ONTOLOGY_10x:
        return True

    return False


def flatten_metadata(obj):
    return flatten(obj, '__')
