"""
validation module
"""

from typing import List

from config import Config
from exceptions import InvalidConfigException
from file import File
from validation_functions import execute_mapped_validation_function
from validation_functions import execute_mapped_defining_validation_function


def validate_file(file_validations: dict, file: File) -> int:
    """
    function for validating a file, for every file validation, call
    the mapped validation function and process it
    :return:
    """
    file_validations_fail_count: int = 0

    for validation, validation_value in file_validations.items():
        file_validations_fail_count += execute_mapped_validation_function(
            validation,
            **{
                "file_name": file.file_name,
                "file_header": file.file_header,
                "file_row_count": file.file_data_row_count,
                "file_size": file.file_size,
                "validation_value": validation_value,
            },
        )

    return file_validations_fail_count


def check_column_validation_rules_align_with_file_content(
    config: Config, file: File
) -> None:
    """
    function checking column validation rules align with the file content
    :param config:
    :param file:
    :return:
    """
    column_names_in_file: List[str] = []
    column_indexes_in_file: List[str] = []

    if file.file_header:
        column_names_in_file = file.file_header
    else:
        column_indexes_in_file = [
            str(index) for index in range(0, file.get_first_row_column_count())
        ]

    column_identifiers_in_file: List[
        str
    ] = column_names_in_file + column_indexes_in_file

    column_validation_rules_names_in_config: List = list(
        config.column_validation_rules.keys()
    )

    if not column_identifiers_in_file:
        raise InvalidConfigException(
            "Column validations set in the config, "
            "but none of the expected columns found in the file"
        )

    if not all(
        item in column_identifiers_in_file
        for item in column_validation_rules_names_in_config
    ):
        raise InvalidConfigException(
            "Column validations set in the config, "
            "but not all expected columns found in the file"
        )


def validate_line_values(column_validations: dict, line: dict, idx: int) -> int:
    """
    function for validating a line in a file, for every column validation, call
    the mapped validation function and process it
    :param column_validations:
    :param line:
    :param idx:
    :return:
    """
    column_validations_fail_count: int = 0

    # looping through column names and column values in the line items
    for column_name, column_value in line.items():
        if column_name in column_validations:
            # looping through validation items
            for validation, validation_value in column_validations[column_name].items():
                ret_value = execute_mapped_defining_validation_function(
                    validation,
                    **{
                        "column": column_name,
                        "validation_value": validation_value,
                        "column_value": column_value,
                        "row_number": idx,
                    },
                )
                if ret_value == 2:
                    column_validations_fail_count += execute_mapped_validation_function(
                        validation,
                        **{
                            "column": column_name,
                            "validation_value": validation_value,
                            "column_value": column_value,
                            "row_number": idx,
                        },
                    )
                elif ret_value == 1:
                    column_validations_fail_count += 1
                elif ret_value == 0:
                    break

    return column_validations_fail_count
