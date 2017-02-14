## Authentication and Authorization

We use cloud.gov/Cloud Foundry's User Account and Authentication (UAA)
server to authenticate users. When a user logs in via UAA, their email
address is looked up in Django's user database; if a matching email is
found, the user is logged in. If not, however, the user is *not* logged in,
and will be shown an error message.

Running `manage.py initgroups` will initialize all Django groups for CALC.
Currently, authorization is set up as follows:

* **Non-staff users** in the **Contract Officers** group can upload individual
  price lists for approval.
* **Staff users** in the **Data Administrators** group can
  * create and edit users and assign them to groups,
  * review submitted price lists and approve/reject/retire them,
  * bulk upload data exports (only Region 10 data for now).
* **Superusers** can do anything, but only infrastructure/operational
  engineers should be given this capability.

An initial superuser can be created via e.g.:

```
python manage.py createsuperuser --noinput --username foo --email foo@localhost
```

This will create a user without a password, which is fine since CALC doesn't
use password authentication.
