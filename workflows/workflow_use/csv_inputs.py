"""CSV input loading + per-field conversion for the `run-workflow-csv` command.

Kept out of cli.py (which imports browser_use) so this logic is unit-testable on its own.
"""

from __future__ import annotations

import pandas as pd


def load_workflow_csv(csv_path) -> pd.DataFrame:
	"""Load the run-workflow-csv input with every column as string, so string-typed inputs keep
	their exact text.

	`dtype=str` alone is not enough: pandas' default NA detection would still turn literal cells such
	as ``NA`` (e.g. the Namibia country code) or ``null`` into NaN. ``keep_default_na=False`` disables
	that, and ``na_values=['']`` keeps only a truly empty cell as missing (NaN) so the required-field
	``pd.isna()`` check in the caller is unchanged.
	"""
	return pd.read_csv(csv_path, dtype=str, keep_default_na=False, na_values=[''])


def convert_csv_value(raw_value, field_type: str):
	"""Convert one CSV cell to the workflow input's declared type.

	string/default keeps the exact text; ``number`` -> float; ``bool`` -> truthy parse.
	"""
	ft = field_type.lower()
	if ft == 'bool':
		return str(raw_value).lower() in ['true', '1', 'yes', 'on']
	if ft == 'number':
		return float(raw_value)
	return str(raw_value)
