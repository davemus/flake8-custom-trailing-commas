# Description

This flake8 plugin enforces trailing commas in tuples. It hasn't settings so far.

It adds new error message: CMA100 trailing comma in tuple is missing

# Examples

Code below is invalid:
```python
a = (
    1, 2, 3
)
```

And this is a valid version:
```python
a = (
    1, 2, 3,
)
```