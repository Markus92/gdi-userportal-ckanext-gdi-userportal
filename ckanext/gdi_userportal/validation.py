# SPDX-FileCopyrightText: His Majesty the King in Right of Canada, His Majesty the King in Right of Canada, represented by the President of the Treasury Board
# SPDX-FileContributor: Stichting Health-RI
#
# SPDX-License-Identifier: MIT

import datetime

import pytz
from ckanext.scheming.validation import register_validator, scheming_validator
from ckantoolkit import Invalid, _, get_validator
from dateutil.parser import ParserError, parse

not_empty = get_validator("not_empty")


def validate_datetime_flex_inputs(
    field, key, data, extras, errors, context
) -> datetime.datetime:
    """This function validates datetime inputs with a timezone accordng to ISO 8601

    If timezone is not set, will localize the datetime object to add the timezone."""
    date_error = _("Date format incorrect")
    time_error = _("Time format incorrect")

    date = None

    def get_input(suffix):
        inpt = key[0] + "_" + suffix
        new_key = (inpt,) + tuple(x for x in key if x != key[0])
        key_value = extras.get(inpt)
        data[new_key] = key_value
        errors[new_key] = []

        if key_value:
            del extras[inpt]

        if field.get("required"):
            not_empty(new_key, data, errors, context)

        return new_key, key_value

    date_key, date_value = get_input("date")

    if date_value:
        try:
            date = parse(date_value)
        except (TypeError, ValueError) as e:
            errors[date_key].append(date_error)

    time_key, time_value = get_input("time")
    if time_value:
        if not date_value:
            errors[date_key].append(_("Date is required when a time is provided"))
        else:
            try:
                value_full = f"{date_value}T{time_value}"
                date = parse(value_full)
            except (TypeError, ValueError) as e:
                errors[time_key].append(time_error)

    tz_key, tz_value = get_input("tz")
    if tz_value:
        if tz_value not in pytz.all_timezones:
            errors[tz_key].append("Invalid timezone")
        else:
            if isinstance(date, datetime.datetime):
                date = pytz.timezone(tz_value).localize(date)

    return date


@register_validator
@scheming_validator
def scheming_isodatetime_flex(field, schema):
    """This scheming validator is very similar to the upstream one, but uses the parser from
    dateutil, which is a bit more robust and can also handle missing timestamps from inputs.
    """

    def validator(key, data, errors, context):
        value = data[key]
        date = None

        # If we get a value for the key, check if it's a datetime else make it one
        if value:
            if isinstance(value, datetime.datetime):
                date = value
            else:
                try:
                    date = parse(value)
                except (ValueError, TypeError):
                    raise Invalid(_("Datetime format incorrect"))
        else:
            # Else try to combine existing fields (extras date and time) into a datetime object
            extras = data.get(("__extras",))
            if not extras or (
                f"{key[0]}_date" not in extras and f"{key[0]}_time" not in extras
            ):
                if field.get("required"):
                    not_empty(key, data, errors, context)
            else:
                date = validate_datetime_flex_inputs(
                    field, key, data, extras, errors, context
                )

        data[key] = date

    return validator
