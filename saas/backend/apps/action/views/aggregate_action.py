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
from rest_framework import status, views
from rest_framework.response import Response

from backend.biz.aggregate_action import AggregateActionsBiz

from ..serializers import AggregateActionsSLZ, SystemsSLZ


class AggregateActionView(views.APIView):
    """
    聚合操作
    """

    biz = AggregateActionsBiz()

    @swagger_auto_schema(
        operation_description="获取操作聚合信息",
        query_serializer=SystemsSLZ(),
        responses={status.HTTP_200_OK: AggregateActionsSLZ(label="聚合操作")},
        tags=["action"],
    )
    def get(self, request):
        serializer = SystemsSLZ(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        system_ids = serializer.validated_data["system_ids"].split(",")

        aggregations = self.biz.list(system_ids)

        return Response({"aggregations": [one.dict() for one in aggregations]})
