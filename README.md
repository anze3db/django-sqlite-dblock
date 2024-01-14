# Django SQLite

Default Django settings for SQLite don't allow concurrent writes from multiple threads/processes. This repo reproduces the problem and shows a potential fix it.

## Reproducing the problem

1. Clone this repo
2. Create a virtualenv and install the requirements
3. Run `python manage.py migrate`
4. Run `gunicorn djangosqlite.wsgi`

Now open a new terminal and run:

```
locust --headless -u 10 -t 10s --host http://localhost:8000/
```

You should see a number of requests fail:

```
Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /create_user/                                                                     28   14(50.00%) |    685     474    1640    630 |    3.17        1.59
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        28   14(50.00%) |    685     474    1640    630 |    3.17        1.59

Response time percentiles (approximated)
Type     Name                                                                                  50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|--------------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
GET      /create_user/                                                                         640    720    750    750    780    800   1600   1600   1600   1600   1600     28
--------|--------------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
         Aggregated                                                                            640    720    750    750    780    800   1600   1600   1600   1600   1600     28

Error report
# occurrences      Error
------------------|---------------------------------------------------------------------------------------------------------------------------------------------
14                 GET /create_user/: HTTPError('500 Server Error: Internal Server Error for url: /create_user/')
------------------|---------------------------------------------------------------------------------------------------------------------------------------------
```

The error:

```
Traceback (most recent call last):
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/backends/utils.py", line 105, in _execute
    return self.cursor.execute(sql, params)
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/backends/sqlite3/base.py", line 328, in execute
    return super().execute(query, params)
  File "/Users/anze/.pyenv/versions/pypy3.10-7.3.13/lib/pypy3.10/_sqlite3.py", line 834, in wrapper
    return func(self, *args, **kwargs)
  File "/Users/anze/.pyenv/versions/pypy3.10-7.3.13/lib/pypy3.10/_sqlite3.py", line 995, in execute
    return self.__execute(False, sql, [params])
  File "/Users/anze/.pyenv/versions/pypy3.10-7.3.13/lib/pypy3.10/_sqlite3.py", line 985, in __execute
    raise self.__connection._get_exception(ret)

The above exception (database is locked) was the direct cause of the following exception:
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/core/handlers/exception.py", line 55, in inner
    response = get_response(request)
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/core/handlers/base.py", line 197, in _get_response
    response = wrapped_callback(request, *callback_args, **callback_kwargs)
  File "/Users/anze/.pyenv/versions/pypy3.10-7.3.13/lib/pypy3.10/contextlib.py", line 79, in inner
    return func(*args, **kwds)
  File "/Users/anze/Coding/djangosqlite/djangosqlite/urls.py", line 30, in create_user
    User.objects.create_user(
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/contrib/auth/models.py", line 161, in create_user
    return self._create_user(username, email, password, **extra_fields)
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/contrib/auth/models.py", line 155, in _create_user
    user.save(using=self._db)
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/contrib/auth/base_user.py", line 77, in save
    super().save(*args, **kwargs)
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/models/base.py", line 822, in save
    self.save_base(
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/models/base.py", line 909, in save_base
    updated = self._save_table(
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/models/base.py", line 1067, in _save_table
    results = self._do_insert(
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/models/base.py", line 1108, in _do_insert
    return manager._insert(
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/models/manager.py", line 87, in manager_method
    return getattr(self.get_queryset(), name)(*args, **kwargs)
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/models/query.py", line 1845, in _insert
    return query.get_compiler(using=using).execute_sql(returning_fields)
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/models/sql/compiler.py", line 1823, in execute_sql
    cursor.execute(sql, params)
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/backends/utils.py", line 122, in execute
    return super().execute(sql, params)
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/backends/utils.py", line 79, in execute
    return self._execute_with_wrappers(
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/backends/utils.py", line 92, in _execute_with_wrappers
    return executor(sql, params, many, context)
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/backends/utils.py", line 100, in _execute
    with self.db.wrap_database_errors:
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/utils.py", line 91, in __exit__
    raise dj_exc_value.with_traceback(traceback) from exc_value
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/backends/utils.py", line 105, in _execute
    return self.cursor.execute(sql, params)
  File "/Users/anze/Coding/djangosqlite/.venv/lib/pypy3.10/site-packages/django/db/backends/sqlite3/base.py", line 328, in execute
    return super().execute(query, params)
  File "/Users/anze/.pyenv/versions/pypy3.10-7.3.13/lib/pypy3.10/_sqlite3.py", line 834, in wrapper
    return func(self, *args, **kwargs)
  File "/Users/anze/.pyenv/versions/pypy3.10-7.3.13/lib/pypy3.10/_sqlite3.py", line 995, in execute
    return self.__execute(False, sql, [params])
  File "/Users/anze/.pyenv/versions/pypy3.10-7.3.13/lib/pypy3.10/_sqlite3.py", line 985, in __execute
    raise self.__connection._get_exception(ret)

Exception Type: OperationalError at /create_user/
Exception Value: database is locked
```

## Fixing the problem

To fix the problem we need to do two things:

1. Set the `timeout` parameter in the `DATABASES` setting to a value greater than 0.
2. Use `BEGIN IMMEDIATE` when creating a transaction - the easiest way to demonstrate this is to remove the `atomic` decorator from the `create_user` view and create the transaction manually.

Checkout the `fix` branch to see the changes and run the same test again. This time there should be no errors:

```bash
locust --headless -u 10 -t 10s --host http://localhost:8000/
```

Results:
```
Type     Name                                                                          # reqs      # fails |    Avg     Min     Max    Med |   req/s  failures/s
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
GET      /create_user/                                                                     19     0(0.00%) |    603     465    2065    480 |    2.09        0.00
--------|----------------------------------------------------------------------------|-------|-------------|-------|-------|-------|-------|--------|-----------
         Aggregated                                                                        19     0(0.00%) |    603     465    2065    480 |    2.09        0.00

Response time percentiles (approximated)
Type     Name                                                                                  50%    66%    75%    80%    90%    95%    98%    99%  99.9% 99.99%   100% # reqs
--------|--------------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
GET      /create_user/                                                                         480    480    490    490   1300   2100   2100   2100   2100   2100   2100     19
--------|--------------------------------------------------------------------------------|--------|------|------|------|------|------|------|------|------|------|------|------
         Aggregated                                                                            480    480    490    490   1300   2100   2100   2100   2100   2100   2100     19

```


