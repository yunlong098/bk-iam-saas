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

from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from .serializers import VersionLogSLZ
from .utils import get_version_list


class VersionLogViewSet(GenericViewSet):
    authentication_classes = []  # type: ignore
    permission_classes = []  # type: ignore
    pagination_class = None  # 去掉swagger中的limit offset参数

    @swagger_auto_schema(
        operation_description="版本信息",
        responses={status.HTTP_200_OK: VersionLogSLZ(label="版本信息", many=True)},
        tags=["version_log"],
    )
    def list(self, request, *args, **kwargs):
        data = get_version_list()
        return Response(data)
