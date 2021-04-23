# Description

This flake8 plugin enforces trailing commas in tuples and do few
other things. It hasn't settings so far. In near future it will be
renamed.

## New error messages:

* CMA100 trailing comma in tuple is missing

Examples

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
raise ValidationError(_('Error without dot'))
```

Valid
```
raise ValidationError(_('Error with dot.'))
```

* CMA201 message of ValidationError should be wrapped in `_`

Enforces all messages of ValidationError to be wrapped in call of function _ (it could be gettext or gettext_lazy)

Invalid
```
raise ValidationError('Not internationalized')
```

Valid
```
raise ValidationError(_('Internationalized'))
```

## Known bugs

* CMA100 incorrectly handles return/yield with multiple parameters
* CMA201 can't handle case of error message, defined outside ValidationError yet

