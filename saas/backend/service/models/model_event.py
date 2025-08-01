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

from pydantic import BaseModel, Field


class ModelEvent(BaseModel):
    id: int = Field(alias="pk")
    type: str
    status: str
    system_id: str
    # 变更影响的模型，可能是action、policy、resource_type
    model_type: str
    model_id: str

    class Config:
        allow_population_by_field_name = True  # 支持alias字段同时传 id 与 pk
