from ckan.plugins import toolkit
from ckanext.gdi_userportal.logic.action.translation_utils import (
    collect_values_to_translate,
    get_translations,
    replace_package,
    replace_search_facets,
)
from typing import Dict


@toolkit.side_effect_free
def enhanced_package_search(context, data_dict=None) -> Dict:
    if data_dict is None:
        data_dict = toolkit.request.json

    result = toolkit.get_action("package_search")(context, data_dict)

    values_to_translate = collect_values_to_translate(result)
    translations = get_translations(values_to_translate)

    result["results"] = [
        replace_package(package, translations) for package in result["results"]
    ]

    if "search_facets" in result.keys():
        result["search_facets"] = replace_search_facets(
            result["search_facets"], translations
        )

    return result
