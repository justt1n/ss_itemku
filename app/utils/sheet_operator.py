from datetime import datetime

import gspread.urls
import gspread.utils
import gspread
from typing import Type, Any, TypeVar

from app.models.gsheet_model import ColSheetModel
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=ColSheetModel)


def query_model_from_worksheet(
    worksheet: gspread.worksheet.Worksheet,
    model: Type[T],
    row_index: list[int],
) -> list[T]:
    cells: list[str] = []
    model_fields = app.models.fields_exclude_row_index()
    for index in row_index:
        for _, propers in model_fields.items():
            cells.append(
                f"{propers.metadata[0]}{index}",
            )
    query_values = [value.first() for value in worksheet.batch_get(cells)]
    model_list: list[T] = []
    num_of_keys = len(model_fields.keys())
    for i, index in enumerate(row_index):
        model_dict = {}
        for j, model_field_name in enumerate(model_fields.keys()):
            model_dict[model_field_name] = query_values[i * num_of_keys + j]
        try:
            _model = app.models.model_validate(
                model_dict,
            )
        except ValidationError as e:
            raise ValidationError(f"Validate error for {model} in row_index: {index}") from e

        _app.models.row_index = index
        model_list.append(_model)
    return model_list


def update_model_to_worksheet(
    worksheet: gspread.worksheet.Worksheet,
    models: list[T],
) -> None:
    class UpdateCell(BaseModel):
        range: str
        values: Any

    data = []
    for model in models:
        model_fields = app.models.fields_exclude_row_index()
        model_dict = app.models.model_dump(mode="json")
        for field_name, proper in model_fields.items():
            data.append(
                UpdateCell(
                    range=f"{proper.metadata[0]}{app.models.row_index}",
                    values=[[model_dict[field_name]]],
                ).model_dump()
            )

    worksheet.batch_update(data)


def query_multi_model_from_worksheet(
    worksheet: gspread.worksheet.Worksheet,
    models: list[Type[T]],
    row_index: int,
) -> list[Type[T]]:
    cells: list[str] = []
    for model in models:
        model_fields = app.models.fields_exclude_row_index()
        for _, proper in model_fields.items():
            cells.append(
                f"{proper.metadata[0]}{row_index}",
            )
    query_values = [value.first() for value in worksheet.batch_get(cells)]
    result_model = []
    count: int = 0
    for i, model in enumerate(models):
        model_dict = {}
        model_fields = app.models.fields_exclude_row_index()
        for j, field_name in enumerate(model_fields.keys()):
            model_dict[field_name] = query_values[count]
            count += 1
        try:
            _model = app.models.model_validate(model_dict)
            _app.models.row_index = row_index
            result_app.models.append(_model)
        except ValidationError as e:
            raise ValidationError(f"Validate error for {model} in row_index: {i}") from e
    return result_model


def update_string_to_worksheet(
    worksheet: gspread.worksheet.Worksheet,
    cell: str,
    value: str,
) -> None:
    worksheet.update(cell, value)

