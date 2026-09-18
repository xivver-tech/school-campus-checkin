# Role-Based Access Control (RBAC)

File: `rbac.py`

## Roles
`student` · `teacher` · `staff` · `busdriver` · `host` · `admin` · `appdev`

`admin` and `appdev` have **all** permissions.

## Permission matrix

| Permission | student | teacher | staff | busdriver | host | admin/appdev |
|------------|:-------:|:-------:|:-----:|:---------:|:----:|:------------:|
| checkin.self | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| history.self | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| history.all | | ✓ | ✓ | | ✓ | ✓ |
| campus.board | | ✓ | ✓ | | ✓ | ✓ |
| report.view | | ✓ | ✓ | | ✓ | ✓ |
| checkin.manual | | ✓ | ✓ | | ✓ | ✓ |
| announce.read | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| announce.post | | ✓ | ✓ | | ✓ | ✓ |
| channel.read | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| channel.create | | ✓ | | | | ✓ |
| channel.post | | ✓* | | | | ✓ |
| channel.members | | ✓* | | | | ✓ |
| admin.* | | | | | | ✓ |

\* Teacher can only post / manage members on **channels they own**. Students only **see channels they are members of**.

## Usage in code
```python
from rbac import require, has_perm

@app.route("/absent")
@login_required
@require("report.view")
def absent_today():
    ...

if has_perm("announce.post"):
    # show post form
```

## Decorators
- `@require("perm")` — need this permission
- `@require_any("a", "b")` — need one of them
- `@require_role("teacher", "admin")` — need one of these roles
