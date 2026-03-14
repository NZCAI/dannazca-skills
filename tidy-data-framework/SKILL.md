# Skill: Tidy Data Framework

## Purpose

Transforms "messy" datasets into Tidy Data format, where:
1. Each variable forms a column.
2. Each observation forms a row.
3. Each type of observational unit forms a table.

This skill is designed to be compatible with pandas and can be used to clean data from CSV, Excel, or SQL sources.

## When to use this skill

- You have a dataset where column headers are values, not variable names.
- You have multiple variables stored in one column.
- You have variables stored in both rows and columns.
- You need to prepare data for analysis, visualization, or machine learning.
- You want to standardize data processing workflows.

## Key capabilities

- **Melting**: converting wide data to long format.
- **Pivoting**: converting long data to wide format (if needed for specific outputs).
- **Splitting**: separating multiple variables in a single column.
- **Extracting**: pulling variables out of complex strings.
- **Standardizing**: ensuring consistent column naming and types.

## Inputs

- **Data source**: Path to a CSV/Excel file or a SQL query.
- **Tidying operations**: Description of the messiness (e.g., "Columns 2-5 are year values").
- **Output path**: Where to save the tidy dataset.

## Implementation checklist

- [ ] Load data into a pandas DataFrame.
- [ ] Identify variables, observations, and values.
- [ ] Apply melting, pivoting, or splitting operations.
- [ ] Validate the tidy structure.
- [ ] Save the result.

## Example Usage

```python
from tidy_data import make_tidy

# Load messy data
df = pd.read_csv('messy_data.csv')

# Transform
tidy_df = make_tidy(df, 
                    id_vars=['Name'], 
                    value_vars=['Treatment A', 'Treatment B'], 
                    var_name='Treatment', 
                    value_name='Result')

# Save
tidy_df.to_csv('tidy_data.csv', index=False)
```
