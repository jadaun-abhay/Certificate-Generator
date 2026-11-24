import csv
import json
import io

import openpyxl

from modules.drive.models import File


def parse_rows(data_file: File) -> list[dict[str, str]]:
    """Parse an uploaded data file (csv/json/xlsx) into a list of
    `{field_name: value}` rows, one per certificate to generate."""
    extension = data_file.name.rsplit(".", 1)[-1].lower()
    data_file.file.open("rb")
    try:
        raw = data_file.file.read()
    finally:
        data_file.file.close()

    if extension == "csv":
        text = raw.decode("utf-8-sig")
        return [dict(row) for row in csv.DictReader(io.StringIO(text))]

    if extension == "json":
        payload = json.loads(raw)
        rows = payload["data"] if isinstance(payload, dict) else payload
        return [{str(k): str(v) for k, v in row.items()} for row in rows]

    if extension in ("xlsx", "xls"):
        workbook = openpyxl.load_workbook(io.BytesIO(raw), read_only=True)
        sheet = workbook.active
        header, *data_rows = sheet.iter_rows(values_only=True)
        return [
            {
                str(header[i]): ("" if value is None else str(value))
                for i, value in enumerate(row)
            }
            for row in data_rows
        ]

    raise ValueError(f"Unsupported data file extension: .{extension}")
