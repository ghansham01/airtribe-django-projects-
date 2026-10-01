# Airtribe Projects

A running list of projects in this folder and the errors encountered while building them, including how each issue was resolved.

## Projects

| Project | Location | Description |
| --- | --- | --- |
| DevTrack | [`DevTrack/`](DevTrack/) | Django issue-tracking project. |

## Error Log

### DevTrack: Python metaclass conflict

**Error**

```text
TypeError: metaclass conflict: the metaclass of a derived class must be a (non-strict) subclass of the metaclasses of all its bases
```

**Cause**

`Issue` inherited from both an `ABC`-based class and `django.db.models.Model`. The ABC uses `ABCMeta`, while Django models use `ModelBase`; Python cannot combine these unrelated metaclasses for the derived class.

**Resolution**

Changed `BaseEntity` into a plain Python mixin instead of inheriting from `ABC` or declaring it as an abstract Django model. `Issue` remains a normal Django model and can inherit the mixin without a metaclass conflict. The mixin's default `validate()` raises `NotImplementedError`, and concrete models provide their own validation.

## Adding Entries

Add each new project to the Projects table. For an error, record the project, the full error message, its cause, and the change that resolved it under Error Log.

