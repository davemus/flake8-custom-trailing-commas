# Description

This flake8 plugin enforces trailing commas in tuples and do few
other things. It hasn't settings so far. In near future it will be
renamed.

It adds new error messages:

* CMA100 trailing comma in tuple is missing

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

* CMA200 message of ValidationError should end with dot

Enforces ValidationError (both rest_framework and django) to have
dot in the end of message/messages:

Invalid:
```
raise ValidationError('Error without dot')
```

Valid
```
raise ValidationError('Error with dot.')
```

