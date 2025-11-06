"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-权限中心(BlueKing-IAM) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from typing import List

from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from pydantic.tools import parse_obj_as
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from backend.api.authentication import ESBAuthentication
from backend.api.management.constants import ManagementAPIEnum, VerifyApiParamLocationEnum
from backend.api.management.v2.permissions import ManagementAPIPermission
from backend.api.management.v2.serializers import (
    BatchTemplateCreateSLZ,
    BatchTemplateGroupPreUpdateSLZ,
    BatchTemplatePreUpdateSLZ,
    BatchTemplateUpdateCommitSLZ,
    BatchTemplateUpdateSLZ,
    ManagementTemplateCreateSLZ,
    ManagementTemplateIdSLZ,
    ManagementTemplateListSchemaSLZ,
    ManagementTemplateListSLZ,
)
from backend.apps.organization.models import User
from backend.apps.role.models import Role
from backend.apps.template.audit import TemplateCreateAuditProvider
from backend.apps.template.filters import TemplateFilter
from backend.apps.template.models import PermTemplate, PermTemplatePreUpdateLock
from backend.apps.template.views import TemplateQueryMixin
from backend.audit.audit import audit_context_setter, view_audit_decorator
from backend.biz.action import ActionCheckBiz, ActionResourceGroupForCheck
from backend.biz.role import RoleAuthorizationScopeChecker, RoleListQuery
from backend.biz.template import (
    TemplateBiz,
    TemplateCheckBiz,
    TemplateCreateBean,
    TemplateGroupPreCommitBean,
    TemplatePolicyCloneBiz,
)
from backend.common import error_codes
from backend.common.lock import gen_template_upsert_lock
from backend.long_task.constants import TaskType
from backend.long_task.models import TaskDetail
from backend.long_task.tasks import TaskFactory
from backend.service.constants import RoleType


class ManagementTemplateViewSet(TemplateQueryMixin, GenericViewSet):
    """模板"""

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "list": (
            VerifyApiParamLocationEnum.ROLE_IN_PATH.value,
            ManagementAPIEnum.V2_GRADE_MANAGER_TEMPLATE_LIST.value,
        ),
        "create": (
            VerifyApiParamLocationEnum.ROLE_IN_PATH.value,
            ManagementAPIEnum.V2_GRADE_MANAGER_TEMPLATE_CREATE.value,
        ),
    }
    queryset = PermTemplate.objects.all()
    lookup_field = "id"
    template_biz = TemplateBiz()
    template_check_biz = TemplateCheckBiz()
    filterset_class = TemplateFilter

    @swagger_auto_schema(
        operation_description="模板列表",
        responses={status.HTTP_200_OK: ManagementTemplateListSchemaSLZ(label="模板", many=True)},
        tags=["management.role.template"],
    )
    def list(self, request, *args, **kwargs):
        role = get_object_or_404(Role, type=RoleType.GRADE_MANAGER.value, id=kwargs["id"])
        # 用户校验，默认用admin
        user = User.objects.get(username="admin")
        queryset = self.filter_queryset(RoleListQuery(role, user).query_template())
        # 查询 role 的 system-actions set
        role_system_actions = RoleListQuery(role).get_scope_system_actions()

        # 强制分页
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request, view=self)

        if page is None:
            return Response(
                {"detail": "Pagination is required, but no valid page parameters were provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ManagementTemplateListSLZ(page, many=True, role_system_actions=role_system_actions)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        operation_description="分级管理员创建模板",
        request_body=ManagementTemplateCreateSLZ(label="模板"),
        responses={status.HTTP_201_CREATED: ManagementTemplateIdSLZ(label="模板ID")},
        tags=["management.role.template"],
    )
    @view_audit_decorator(TemplateCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        """
        分管创建模板
        """
        role_id = kwargs["id"]
        request.data["system_id"] = request.data.pop("system")
        serializer = ManagementTemplateCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = request.user.username
        data = serializer.validated_data
        role = get_object_or_404(Role, type=RoleType.GRADE_MANAGER.value, id=role_id)

        # 检查模板的授权是否满足管理员的授权范围
        scope_checker = RoleAuthorizationScopeChecker(role)
        scope_checker.check_actions(data["system_id"], data["action_ids"])

        with gen_template_upsert_lock(role.id, data["name"]):
            # 检查权限模板是否在角色内唯一
            self.template_check_biz.check_role_template_name_exists(role.id, data["name"])

            template = self.template_biz.create(role.id, TemplateCreateBean.parse_obj(data), user_id)

        audit_context_setter(template=template)

        return Response({})


class BatchTemplateViewSet(GenericViewSet):
    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "create": (
            VerifyApiParamLocationEnum.SYSTEM_IN_PATH.value,
            ManagementAPIEnum.V2_BATCH_TEMPLATE_CREATE.value,
        ),
        "partial_update": (
            VerifyApiParamLocationEnum.SYSTEM_IN_PATH.value,
            ManagementAPIEnum.V2_BATCH_TEMPLATE_UPDATE.value,
        ),
    }

    template_biz = TemplateBiz()
    template_check_biz = TemplateCheckBiz()

    @swagger_auto_schema(
        operation_description="创建模板",
        request_body=BatchTemplateCreateSLZ(label="模板"),
        responses={status.HTTP_201_CREATED: ManagementTemplateIdSLZ(label="模板ID")},
        tags=["management.role.template"],
    )
    @view_audit_decorator(TemplateCreateAuditProvider)
    def create(self, request, *args, **kwargs):
        """
        创建模板
        """

        request.data["system_id"] = request.data.pop("system_id")
        serializer = BatchTemplateCreateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = request.user.username
        data = serializer.validated_data
        role_ids = data["role_ids"]
        for role_id in role_ids:
            role = get_object_or_404(Role, type=RoleType.GRADE_MANAGER.value, id=role_id)

            # 检查模板的授权是否满足管理员的授权范围
            scope_checker = RoleAuthorizationScopeChecker(role)
            scope_checker.check_actions(data["system_id"], data["action_ids"])

            with gen_template_upsert_lock(role_ids[0], data["name"]):
                # 检查权限模板是否在角色内唯一
                self.template_check_biz.check_role_template_name_exists(role_id, data["name"])

                template = self.template_biz.create(role_id, TemplateCreateBean.parse_obj(data), user_id)

            audit_context_setter(template=template)

        return Response({})

    @swagger_auto_schema(
        operation_description="权限模板基本信息更新",
        request_body=BatchTemplateUpdateSLZ(label="更新权限模板基本信息"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.template"],
    )
    def partial_update(self, request, *args, **kwargs):
        """仅做基本信息更新"""
        serializer = BatchTemplateUpdateSLZ(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_id = request.user.username
        templates = serializer.validated_data["templates"]

        for template in templates:
            with gen_template_upsert_lock(template["role_id"], template["name"]):
                # 检查权限模板是否在角色内唯一
                self.template_check_biz.check_role_template_name_exists(
                    template["role_id"], template["name"], template_id=template["template_id"]
                )
                PermTemplate.objects.filter(id=template["template_id"]).update(
                    updater=user_id, name=template["name"], description=template["description"]
                )

            audit_context_setter(template=template)

        return Response({})


class BatchTemplatePreUpdateViewSet(GenericViewSet):
    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "create": (
            VerifyApiParamLocationEnum.SYSTEM_IN_PATH.value,
            ManagementAPIEnum.V2_BATCH_TEMPLATE_PRE_UPDATE.value,
        ),
    }

    template_biz = TemplateBiz()
    template_check_biz = TemplateCheckBiz()
    template_policy_clone_biz = TemplatePolicyCloneBiz()

    @swagger_auto_schema(
        operation_description="预更新",
        request_body=BatchTemplatePreUpdateSLZ(label="新增操作"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.template"],
    )
    def create(self, request, *args, **kwargs):

        slz = BatchTemplatePreUpdateSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        template_ids = slz.validated_data["template_ids"]
        for template_id in template_ids:
            template = get_object_or_404(PermTemplate, id=template_id)

            lock = self.template_biz.create_template_update_lock(template, slz.validated_data["action_ids"])

            audit_context_setter(template=template)

            add_action_ids = list(set(lock.action_ids) - set(template.action_ids))
            if not add_action_ids:
                return Response([])

            self.template_policy_clone_biz.gen_system_action_clone_config(
                template.system_id, add_action_ids, template.action_ids
            )
        return Response()


class BatchTemplatePreGroupSyncViewSet(GenericViewSet):

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "create": (
            VerifyApiParamLocationEnum.SYSTEM_IN_PATH.value,
            ManagementAPIEnum.V2_BATCH_TEMPLATE_PRE_GROUP_SYNC.value,
        ),
    }

    template_biz = TemplateBiz()
    template_check_biz = TemplateCheckBiz()
    action_check_biz = ActionCheckBiz()

    @swagger_auto_schema(
        operation_description="用户组同步预提交",
        request_body=BatchTemplateGroupPreUpdateSLZ(label="用户组同步预提交"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.template"],
    )
    def create(self, request, *args, **kwargs):

        slz = BatchTemplateGroupPreUpdateSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data

        for template_group in data["template_groups"]:
            template = get_object_or_404(PermTemplate, id=template_group["template_id"])
            add_action_ids = self.template_biz.list_template_update_add_action_id(template)

            for group in template_group["groups"]:
                self.action_check_biz.check_action_resource_group(
                    template.system_id, parse_obj_as(List[ActionResourceGroupForCheck], group["actions"])
                )
            # 检查数据
            pre_commits = parse_obj_as(List[TemplateGroupPreCommitBean], template_group["groups"])
            self.template_check_biz.check_group_update_pre_commit(template.id, pre_commits, add_action_ids)

            # 新增获取更新
            self.template_biz.create_or_update_group_pre_commit(template.id, pre_commits)

        return Response({})


class BatchTemplateUpdateCommitViewSet(GenericViewSet):

    authentication_classes = [ESBAuthentication]
    permission_classes = [ManagementAPIPermission]

    management_api_permission = {
        "create": (
            VerifyApiParamLocationEnum.SYSTEM_IN_PATH.value,
            ManagementAPIEnum.V2_BATCH_TEMPLATE_UPDATE_COMMIT.value,
        ),
    }

    template_biz = TemplateBiz()
    template_check_biz = TemplateCheckBiz()

    @swagger_auto_schema(
        operation_description="批量权限模板更新提交",
        request_body=BatchTemplateUpdateCommitSLZ(label="批量权限模板更新提交"),
        responses={status.HTTP_200_OK: serializers.Serializer()},
        tags=["management.role.template"],
    )
    def create(self, request, *args, **kwargs):
        slz = BatchTemplateUpdateCommitSLZ(data=request.data)
        slz.is_valid(raise_exception=True)
        data = slz.validated_data
        template_ids = data["template_ids"]
        for template_id in template_ids:

            template = get_object_or_404(PermTemplate, id=template_id)
            add_action_ids = self.template_biz.list_template_update_add_action_id(template)
            # 只有有新增的操作的时候需要校验
            if add_action_ids:
                self.template_check_biz.check_group_pre_commit_complete(template.id)

            if not PermTemplatePreUpdateLock.objects.update_waiting_to_running(template.id):
                # 任务已经开始运行了
                raise error_codes.VALIDATE_ERROR.format(_("预提交的任务不存在, 禁止提交!"))

            # 使用长时任务实现用户组授权更新
            task = TaskDetail.create(TaskType.TEMPLATE_UPDATE.value, [template.id])
            TaskFactory().run(task.id)

            audit_context_setter(template=template)

        return Response({})
