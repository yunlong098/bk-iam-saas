# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云 - 权限中心 (BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django_celery_beat.models import CrontabSchedule, PeriodicTask

from backend.apps.role.models import RolePolicyExpiredNotificationConfig


class Command(BaseCommand):
    """
    权限续期提醒
    """

    def add_arguments(self, parser):
        parser.add_argument("--tenant_id", type=str, help="Tenant ID", required=True)
        parser.add_argument("--role_id", type=int, help="Role ID", required=True)

    def handle(self, *args, **options):
        tenant_id = options["tenant_id"]
        role_id = options["role_id"]

        name = f"periodic_permission_expire_remind_{tenant_id}"
        notification_config = RolePolicyExpiredNotificationConfig.objects.get(tenant_id=tenant_id, role_id=role_id)
        config = notification_config.config
        hour, minute = [int(i) for i in config["send_time"].split(":")]

        schedule, _ = CrontabSchedule.objects.get_or_create(
            minute=minute,
            hour=hour,
            day_of_week="*",
            day_of_month="*",
            month_of_year="*",
            timezone=timezone.get_current_timezone(),
        )
        PeriodicTask.objects.create(
            crontab=schedule,
            name=name,
            task="saas.tenant.tasks.permission_expire_remind",
            kwargs={"tenant_id": tenant_id},
        )
