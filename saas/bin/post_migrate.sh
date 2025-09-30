#!/bin/bash

python manage.py init_tenant --tenant_id="system"
python manage.py update_periodic_permission_expire_remind_schedule --tenant_id="system" --role_id=1
