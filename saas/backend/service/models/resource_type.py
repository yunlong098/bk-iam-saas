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

from typing import Dict, Tuple

from pydantic import BaseModel


class ResourceType(BaseModel):
    id: str
    name: str
    name_en: str


class ResourceTypeDict(BaseModel):
    data: Dict[Tuple[str, str], Dict]

    def get_name(self, system_id: str, resource_type_id: str) -> Tuple[str, str]:
        rt = self.data.get((system_id, resource_type_id), None)
        return (rt["name"], rt["name_en"]) if rt else ("", "")
