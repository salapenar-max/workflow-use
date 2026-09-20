"""Regression test for run-workflow-csv string inputs (leading-zero / numeric-looking values).

Before the fix, `pd.read_csv(csv_path)` inferred numeric dtypes, so a string-typed input like a zip
code "01234" was read as int 1234 and then `str()`-ed to "1234" (leading zero lost); a mixed column
became floats ("1002" -> "1002.0"). The value is substituted into the workflow, so form fields were
filled with corrupted identifiers. The fix reads with `dtype=str`.

This mirrors the per-field conversion in `run_workflow_csv_command._execute_single_workflow`.
"""
import io

import pandas as pd


def _convert(raw_value, field_type: str):
    """Same per-field conversion _execute_single_workflow applies to each CSV cell."""
    if field_type.lower() == 'bool':
        return str(raw_value).lower() in ['true', '1', 'yes', 'on']
    if field_type.lower() == 'number':
        return float(raw_value)
    return str(raw_value)  # string or default


CSV = "zip,count,flag,note\n01234,1002,true,hello\n00089,7,false,world\n"


def test_string_field_keeps_leading_zeros():
    df = pd.read_csv(io.StringIO(CSV), dtype=str)  # the fix
    assert _convert(df.iloc[0]['zip'], 'string') == '01234'
    assert _convert(df.iloc[1]['zip'], 'string') == '00089'
    assert _convert(df.iloc[0]['note'], 'string') == 'hello'


def test_number_and_bool_fields_still_convert():
    df = pd.read_csv(io.StringIO(CSV), dtype=str)
    assert _convert(df.iloc[0]['count'], 'number') == 1002.0
    assert _convert(df.iloc[0]['flag'], 'bool') is True
    assert _convert(df.iloc[1]['flag'], 'bool') is False


def test_empty_required_cell_still_detected_as_missing():
    # dtype=str must not defeat the pd.isna() required-field check.
    df = pd.read_csv(io.StringIO("zip,count\n,5\n"), dtype=str)
    assert pd.isna(df.iloc[0]['zip'])
