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
from django.db import models

from backend.api.authorization.constants import AuthorizationAPIEnum


class AuthAPIAllowListConfigManager(models.Manager):
    def list_api_msg(self):
        auth_api = dict(AuthorizationAPIEnum.get_choices())
        api_msg = [{"api": api, "name": auth_api[api]} for api in auth_api]
        return api_msg
