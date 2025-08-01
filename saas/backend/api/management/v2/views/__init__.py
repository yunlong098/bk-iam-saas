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

from .application import (
    ManagementApplicationCancelView,
    ManagementGradeManagerApplicationViewSet,
    ManagementGradeManagerUpdatedApplicationViewSet,
    ManagementGroupApplicationViewSet,
    ManagementGroupBatchExpiredAtRenewApplicationViewSet,
    ManagementGroupRenewApplicationViewSet,
)
from .approval import ManagementApplicationApprovalView
from .grade_manager import ManagementGradeManagerViewSet
from .group import (
    ManagementGradeManagerGroupViewSet,
    ManagementGroupActionPolicyViewSet,
    ManagementGroupMemberBatchExpiredAtViewSet,
    ManagementGroupMemberExpiredAtViewSet,
    ManagementGroupMemberViewSet,
    ManagementGroupPolicyActionViewSet,
    ManagementGroupPolicyTemplateViewSet,
    ManagementGroupPolicyViewSet,
    ManagementGroupSubjectTemplateViewSet,
    ManagementGroupViewSet,
    ManagementSystemManagerGroupViewSet,
)
from .subject import (
    ManagementDepartmentGroupBelongViewSet,
    ManagementMemberGroupDetailViewSet,
    ManagementUserGroupBelongViewSet,
)
from .subject_template import ManagementGradeManagerSubjectTemplateViewSet
from .subset_manager import ManagementSubsetManagerCreateListViewSet, ManagementSubsetManagerViewSet
from .template import ManagementTemplateViewSet

__all__ = [
    "ManagementSystemManagerGroupViewSet",
    "ManagementGradeManagerGroupViewSet",
    "ManagementGroupViewSet",
    "ManagementGroupMemberViewSet",
    "ManagementGroupMemberExpiredAtViewSet",
    "ManagementGroupSubjectTemplateViewSet",
    "ManagementGroupPolicyViewSet",
    "ManagementGroupApplicationViewSet",
    "ManagementGroupRenewApplicationViewSet",
    "ManagementGroupActionPolicyViewSet",
    "ManagementGroupPolicyActionViewSet",
    "ManagementUserGroupBelongViewSet",
    "ManagementDepartmentGroupBelongViewSet",
    "ManagementGradeManagerApplicationViewSet",
    "ManagementGradeManagerUpdatedApplicationViewSet",
    "ManagementApplicationApprovalView",
    "ManagementSubsetManagerCreateListViewSet",
    "ManagementApplicationCancelView",
    "ManagementGradeManagerViewSet",
    "ManagementSubsetManagerViewSet",
    "ManagementGradeManagerSubjectTemplateViewSet",
    "ManagementMemberGroupDetailViewSet",
    "ManagementGroupPolicyTemplateViewSet",
    "ManagementTemplateViewSet",
    "ManagementGroupMemberBatchExpiredAtViewSet",
    "ManagementGroupBatchExpiredAtRenewApplicationViewSet",
]
