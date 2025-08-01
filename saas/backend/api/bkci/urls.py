# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("task/", views.MigrateTaskView.as_view({"get": "list", "post": "create"}), name="bkci.migrate_task"),
    path("data/", views.MigrateDataView.as_view({"get": "list"}), name="bkci.migrate_data"),
    path("legacy_task/", views.MigrateLegacyTaskView.as_view({"post": "create"}), name="bkci.migrate_legacy_task"),
    path(
        "legacy_task/<int:id>/",
        views.MigrateLegacyTaskView.as_view({"get": "retrieve"}),
        name="bkci.migrate_legacy_task_detail",
    ),
]
