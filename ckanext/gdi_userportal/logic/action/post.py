# SPDX-FileCopyrightText: 2024 Stichting Health-RI
# SPDX-FileContributor: PNED G.I.E.
#
# SPDX-License-Identifier: Apache-2.0

import logging
from ckan.plugins import toolkit
from ckanext.gdi_userportal.logic.action.translation_utils import (
    collect_values_to_translate,
    get_translations,
    replace_package,
    replace_search_facets,
)
from typing import Dict

log = logging.getLogger(__name__)


@toolkit.side_effect_free
def enhanced_package_search(context, data_dict=None) -> Dict:
    if data_dict is None:
        if toolkit.request.json:
            data_dict = toolkit.request.json
        else:
            log.error("data_dict and request body cannot be both empty")
            raise toolkit.ValidationError(
                "data_dict and request body cannot be both empty"
            )

    try:
        result = toolkit.get_action("package_search")(context, data_dict)
    except toolkit.ObjectNotFound as e:
        log.error("Package search failed: %s", str(e))
        raise toolkit.ObjectNotFound("No results found for the provided query.")
    except Exception as e:
        log.error("Unexpected error during package search: %s", str(e))
        raise e("An error occurred during package search.")

    try:
        values_to_translate = collect_values_to_translate(result)
        translations = get_translations(values_to_translate)
    except Exception as e:
        log.error("Error during translation: %s", str(e))
        translations = {}

    result["results"] = [
        replace_package(package, translations) for package in result["results"]
    ]

    if "search_facets" in result.keys():
        try:
            result["search_facets"] = replace_search_facets(
                result["search_facets"], translations
            )
        except Exception as e:
            log.warning("Error processing search facets: %s", str(e))

    return result
