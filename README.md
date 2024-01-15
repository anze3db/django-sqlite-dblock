# Django SQLite

This repo demonstrates a problem with Django and SQLite when using the `transaction.atomic` decorator/context manager.

## Reproducing the problem

1. Clone this repo
2. Create a virtualenv and install the requirements
3. Run `python manage.py migrate`
4. Run `gunicorn djangosqlite.wsgi,` but the problem also occurs when using `python manage.py runserver` or anywhere where there are at least 2 web worker threads serving requests

Now open a new terminal and run:

```
locust --headless -u 10 -t 10s --host http://localhost:8000/
```

You should see one of the endpoints experiencing errors:

```
Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /read/                                                                           669     0(0.00%) |      4       1     149      3 |   69.37        0.00
GET      /read_write/                                                                     677     0(0.00%) |     10       2     253      5 |   70.20        0.00
GET      /read_write_transaction/                                                         704  199(28.27%) |     18       2     123      5 |   73.00       20.64
GET      /read_write_transaction_immediate/                                               671     0(0.00%) |      8       2     253      5 |   69.58        0.00
GET      /write/                                                                          670     0(0.00%) |      9       2     204      4 |   69.48        0.00
GET      /write_read/                                                                     690     0(0.00%) |     11       2     982      5 |   71.55        0.00
GET      /write_read_transaction/                                                         647     0(0.00%) |     11       2    1276      5 |   67.09        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                      4728   199(4.21%) |     10       1    1276      4 |  490.28       20.64

Response time percentiles (approximated)
Type     Name                                                                                  50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|--------------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
GET      /read/                                                                                  3      4      4      4      6      7     13     23    150    150    150    669
GET      /read_write/                                                                            5      6      8      9     15     28     66    130    250    250    250    677
GET      /read_write_transaction/                                                                5      7     42     45     51     61     74     87    120    120    120    704
GET      /read_write_transaction_immediate/                                                      5      5      6      6      9     23     42    110    250    250    250    671
GET      /write/                                                                                 4      5      6      7     13     26     68    120    200    200    200    670
GET      /write_read/                                                                            5      5      6      7     10     27     93    120    980    980    980    690
GET      /write_read_transaction/                                                                5      5      6      7     10     33     93    120   1300   1300   1300    647
--------|--------------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
         Aggregated                                                                              4      5      6      7     15     45     68    110    360   1300   1300   4728

Error report
# occurrences      Error
------------------|---------------------------------------------------------------------------------------------------------------------------------------------
199                GET /read_write_transaction/: HTTPError('500 Server Error: Internal Server Error for url: /read_write_transaction/')
------------------|---------------------------------------------------------------------------------------------------------------------------------------------
```

The error:

```
Internal Server Error: /read_write_transaction/
Traceback (most recent call last):
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/backends/utils.py", line 105, in _execute
    return self.cursor.execute(sql, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/backends/sqlite3/base.py", line 328, in execute
    return super().execute(query, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sqlite3.OperationalError: database is locked

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/core/handlers/exception.py", line 55, in inner
    response = get_response(request)
               ^^^^^^^^^^^^^^^^^^^^^
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/core/handlers/base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/anze/.pyenv/versions/3.12.0/lib/python3.12/contextlib.py", line 81, in inner
    return func(*args, **kwds)
           ^^^^^^^^^^^^^^^^^^^
  File "/Users/anze/Coding/djangosqlite/djangosqlite/urls.py", line 64, in read_write_transaction
    write_to_db()
  File "/Users/anze/Coding/djangosqlite/djangosqlite/urls.py", line 25, in write_to_db
    A.objects.create()
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/models/manager.py", line 87, in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/models/query.py", line 677, in create
    obj.save(force_insert=True, using=self.db)
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/models/base.py", line 822, in save
    self.save_base(
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/models/base.py", line 909, in save_base
    updated = self._save_table(
              ^^^^^^^^^^^^^^^^^
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/models/base.py", line 1067, in _save_table
    results = self._do_insert(
              ^^^^^^^^^^^^^^^^
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/models/base.py", line 1108, in _do_insert
    return manager._insert(
           ^^^^^^^^^^^^^^^^
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/models/manager.py", line 87, in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/models/query.py", line 1845, in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/models/sql/compiler.py", line 1823, in execute_sql
    cursor.execute(sql, params)
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/backends/utils.py", line 122, in execute
    return super().execute(sql, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/backends/utils.py", line 79, in execute
    return self._execute_with_wrappers(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/backends/utils.py", line 92, in _execute_with_wrappers
    return executor(sql, params, many, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/backends/utils.py", line 100, in _execute
    with self.db.wrap_database_errors:
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/utils.py", line 91, in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/backends/utils.py", line 105, in _execute
    return self.cursor.execute(sql, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/anze/Coding/djangosqlite/.venv/lib/python3.12/site-packages/django/db/backends/sqlite3/base.py", line 328, in execute
    return super().execute(query, params)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
django.db.utils.OperationalError: database is locked
```

## Workaround

To avoid this issue we have to make sure to start the transaction in immediate mode by using `BEGIN IMMEDIATE TRANSACTION` as is done in the `read_write_transaction_immediate` view:

```python
def read_write_transaction_immediate(_):
    connection.cursor().execute("BEGIN IMMEDIATE")
    read_from_db()
    write_to_db()
    connection.cursor().execute("COMMIT")
    return HttpResponse("OK")
```

Unfortunately, there is no way to accomplish this with `transaction.atomic()` without monkeypatching it.

Read the [blog post](https://blog.pecar.me/django-sqlite-dblock) for more details.
