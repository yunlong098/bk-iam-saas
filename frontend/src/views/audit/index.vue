<template>
  <div class="iam-audit-wrapper">
    <render-search>
      <bk-date-picker
        v-model="initDateTime"
        placeholder=""
        type="month"
        :clearable="false"
        @change="handleDateChange">
      </bk-date-picker>
      <div class="audit-search-select">
        <iam-search-select
          ref="iamSearchSelect"
          style="width: 500px;"
          :data="searchData"
          :value="searchValue"
          @on-change="handleSearch" />
      </div>
    </render-search>
    <bk-table
      :data="tableList"
      size="small"
      :max-height="tableHeight"
      :class="{ 'set-border': tableLoading }"
      ext-cls="audit-table"
      :pagination="pagination"
      ref="tableRef"
      row-key="id"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
      :cell-class-name="getCellClass"
      @page-change="pageChange"
      @page-limit-change="limitChange"
      @expand-change="handleExpandChange">
      <bk-table-column type="expand" width="30">
        <template slot-scope="{ row }">
          <section class="audit-detail-wrapper" v-bkloading="{ isLoading: row.loading, opacity: 1 }">
            <template v-if="row.emptyData && ['refresh'].includes(row.emptyData.tipType)">
              <ExceptionEmpty
                :type="row.emptyData.type"
                :empty-text="row.emptyData.text"
                :tip-text="row.emptyData.tip"
                :tip-type="row.emptyData.tipType"
                @on-refresh="handleChildEmptyRefresh(row)"
              />
            </template>
            <template v-else>
              <template v-if="noDetailType.includes(row.type) || row.type === 'role.group.renew'">
                <!-- <div class="empty-wrapper"> -->
                <ExceptionEmpty />
              <!-- </div> -->
              </template>
              <template v-if="onlyDescriptionType.includes(row.detail.type)">
                <section v-if="!row.loading">
                  <p class="description single-hide" :title="row.detail.description">
                    {{ row.detail.description || '--' }}
                  </p>
                </section>
              </template>
              <template v-if="onlySubType.includes(row.detail.type)">
                <bk-table
                  v-if="!row.loading"
                  :data="row.detail.sub_objects"
                  ext-cls="audit-detail-table"
                  :outer-border="false"
                  :header-border="false"
                  :header-cell-style="{ background: '#f5f6fa', borderRight: 'none' }">
                  <bk-table-column :label="$t(`m.common['类型']`)">
                    <template slot-scope="props">
                      <span>{{ objectMap[props.row.type] || props.row.type }}</span>
                    </template>
                  </bk-table-column>
                  <bk-table-column :label="$t(`m.audit['实例']`)">
                    <template slot-scope="props">
                      <span>{{ props.row.name }}</span>
                    </template>
                  </bk-table-column>
                  <template slot="empty">
                    <ExceptionEmpty />
                  </template>
                </bk-table>
              </template>
              <template v-if="deType.includes(row.detail.type)">
                <section v-if="!row.loading">
                  <p class="description">{{ row.detail.description }}</p>
                  <p>{{ $t(`m.audit['版本号']`) }}: {{ row.detail.extra_info.version }}</p>
                </section>
              </template>
              <template v-if="dsType.includes(row.detail.type)">
                <bk-table
                  v-if="!row.loading"
                  :data="row.detail.sub_objects"
                  ext-cls="audit-detail-table"
                  :outer-border="false"
                  :header-border="false"
                  :header-cell-style="{ background: '#f5f6fa', borderRight: 'none' }">
                  <bk-table-column prop="name" :label="$t(`m.audit['对象实例']`)">
                    <template slot-scope="props">
                      <span :title="objectMap[props.row.type] || props.row.type">
                        {{ objectMap[props.row.type] || props.row.type }}
                      </span>
                    </template>
                  </bk-table-column>
                  <bk-table-column :label="$t(`m.audit['操作对象']`)">
                    <template slot-scope="props">
                      <span :title="props.row.name">{{ props.row.name }}</span>
                    </template>
                  </bk-table-column>
                  <bk-table-column :label="$t(`m.common['描述']`)">
                    <template slot-scope="props">
                      <span :title="props.row.description">{{ props.row.description || '--' }}</span>
                    </template>
                  </bk-table-column>
                  <template slot="empty">
                    <ExceptionEmpty />
                  </template>
                </bk-table>
              </template>
              <template v-if="seType.includes(row.detail.type)">
                <bk-table
                  v-if="!row.loading"
                  :data="row.detail.sub_objects"
                  ext-cls="audit-detail-table"
                  :outer-border="false"
                  :header-border="false"
                  :header-cell-style="{ background: '#f5f6fa', borderRight: 'none' }">
                  <bk-table-column prop="name" :label="$t(`m.common['类型']`)">>
                    <template slot-scope="props">
                      <span>{{ objectMap[props.row.type] || props.row.type }}</span>
                    </template>
                  </bk-table-column>
                  <bk-table-column :label="$t(`m.audit['实例']`)">
                    <template slot-scope="props">
                      <span :title="props.row.name">{{ props.row.name }}</span>
                    </template>
                  </bk-table-column>
                  <bk-table-column :label="$t(`m.audit['版本号']`)">
                    <template slot-scope="props">
                      <span>{{ props.row.version || '--' }}</span>
                    </template>
                  </bk-table-column>
                  <template slot="empty">
                    <ExceptionEmpty />
                  </template>
                </bk-table>
              </template>
              <template v-if="onlyExtraInfoType.includes(row.detail.type)">
                <!-- eslint-disable max-len -->
                <template v-if="row.detail.type !== 'role.group.renew' && row.detail.type !== 'template.version.sync'">
                  <render-detail-table :actions="row.detail.extra_info.policies" @on-refresh="handleChildEmptyRefresh(row)" />
                </template>
                <template v-if="row.detail.type === 'template.version.sync'">
                  <p>{{ $t(`m.audit['版本号']`) }}{{ $t(`m.common['：']`) }}{{ row.detail.extra_info.version }}</p>
                </template>
              </template>
              <template v-if="onlyRoleType.includes(row.detail.type)">
                <p>{{ $t(`m.audit['管理空间']`) }}{{ $t(`m.common['：']`) }}{{ row.detail.role_name }}</p>
              </template>
            </template>
          </section>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.audit['时间']`)" width="180">
        <template slot-scope="{ row }">
          <span :title="row.time">{{ row.time }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.audit['操作类型']`)">
        <template slot-scope="{ row }">
          <span :title="typeMap[row.type] || row.type">{{ typeMap[row.type] || row.type }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.audit['对象及类型']`)">
        <template slot-scope="{ row }">
          <span :title="`${objectMap[row.object_type] || row.object_type}${$t(`m.common['：']`)}${row.object_name}`">
            {{ objectMap[row.object_type] || row.object_type }}{{ $t(`m.common['：']`) }}{{ row.object_name }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.audit['操作者']`)">
        <template slot-scope="{ row }">
          <span :title="row.username">{{ row.username }}</span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.audit['操作来源']`)">
        <template slot-scope="{ row }">
          <span :title="sourceMap[row.source_type] || row.source_type">
            {{ sourceMap[row.source_type] || row.source_type }}
          </span>
        </template>
      </bk-table-column>
      <bk-table-column :label="$t(`m.audit['操作状态']`)" width="150">
        <template slot-scope="{ row }">
          <render-status :status="row.status" />
        </template>
      </bk-table-column>
      <template slot="empty">
        <ExceptionEmpty
          :type="emptyData.type"
          :empty-text="emptyData.text"
          :tip-text="emptyData.tip"
          :tip-type="emptyData.tipType"
          @on-clear="handleEmptyClear"
          @on-refresh="handleEmptyRefresh"
        />
      </template>
    </bk-table>
  </div>
</template>
<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import IamSearchSelect from '@/components/iam-search-select';
  import { fuzzyRtxSearch } from '@/common/rtx';
  import { buildURLParams } from '@/common/url';
  import { formatCodeData, getWindowHeight } from '@/common/util';
  import { NO_DETAIL_TYPE, ONLY_DESCRIPTION_TYPE, ONLY_EXTRA_INFO_TYPE, ONLY_SUB_TYPE, DE_TYPR, SE_TYPE, DS_TYPE, ONLY_ROLE_TYPE } from '@/common/constants';
  import RenderStatus from './components/render-status-item';
  import renderDetailTable from './components/render-instance-detail-table';

  export default {
    components: {
      IamSearchSelect,
      RenderStatus,
      renderDetailTable
    },
    data () {
      return {
        tableList: [],
        tableLoading: false,
        pagination: {
          current: 1,
          count: 0,
          limit: 10
        },
        currentBackup: 1,
        searchParams: {},
        searchList: [],
        searchValue: [],
        initDateTime: new Date(),
        objectMap: {
          group: this.$t(`m.userGroup['用户组']`),
          system: this.$t(`m.common['系统']`),
          user: this.$t(`m.common['用户']`),
          department: this.$t(`m.common['组织']`),
          role: this.$t(`m.audit['角色']`),
          template: this.$t(`m.myApply['权限模板']`),
          commonaction: this.$t(`m.audit['常用操作']`),
          super_manager: this.$t(`m.myApproval['超级管理员']`),
          system_manager: this.$t(`m.nav['系统管理员']`),
          rating_manager: this.$t(`m.nav['一级空间管理员']`),
          subset_manager: this.$t(`m.nav['二级空间管理员']`),
          subject_template: this.$t(`m.memberTemplate['人员模板']`),
          action: this.$t(`m.common['操作-table']`)
        },
        sourceMap: {
          web: this.$t(`m.audit['页面']`),
          api: 'API',
          openapi: 'API',
          approval: this.$t(`m.audit['审批']`),
          task: this.$t(`m.audit['后台任务']`)
        },
        typeMap: {
          'user.policy.create': this.$t(`m.audit['用户权限增加']`),
          'user.policy.update': this.$t(`m.audit['用户权限更新']`),
          'user.policy.delete': this.$t(`m.audit['用户权限删除']`),
          'user.group.delete': this.$t(`m.audit['用户退出用户组']`),
          'user.role.delete': this.$t(`m.audit['用户退出管理员']`),
          'user.temporary.policy.create': this.$t(`m.audit['用户临时权限增加']`),
          'user.temporary.policy.delete': this.$t(`m.audit['用户临时权限删除']`),
          'user.blacklist.member.create': this.$t(`m.audit['用户黑名单成员增加']`),
          'user.blacklist.member.delete': this.$t(`m.audit['用户黑名单成员删除']`),
          'user.permission.clean': this.$t(`m.audit['用户权限清理']`),
          'group.create': this.$t(`m.audit['用户组创建']`),
          'group.update': this.$t(`m.audit['用户组修改']`),
          'group.delete': this.$t(`m.audit['用户组删除']`),
          'group.member.create': this.$t(`m.audit['用户组成员增加']`),
          'group.member.delete': this.$t(`m.audit['用户组成员删除']`),
          'group.member.renew': this.$t(`m.audit['用户组成员续期']`),
          'group.policy.create': this.$t(`m.audit['用户组权限增加']`),
          'group.policy.update': this.$t(`m.audit['用户组权限更新']`),
          'group.policy.delete': this.$t(`m.audit['用户组权限删除']`),
          'group.template.create': this.$t(`m.audit['用户组添加权限模板']`),
          'group.template.delete': this.$t(`m.audit['用户组删除权限模板']`),
          'template.create': this.$t(`m.audit['权限模板创建']`),
          'template.update': this.$t(`m.audit['权限模板修改']`),
          'template.delete': this.$t(`m.audit['权限模板删除']`),
          'template.member.create': this.$t(`m.audit['权限模板成员增加']`),
          'template.member.delete': this.$t(`m.audit['权限模板成员删除']`),
          'template.member.update': this.$t(`m.audit['权限模板成员更新']`),
          'template.preupdate.create': this.$t(`m.audit['权限模板预更新创建']`),
          'template.preupdate.delete': this.$t(`m.audit['权限模板预更新删除']`),
          'template.version.sync': this.$t(`m.audit['权限模板版本全量同步']`),
          'template.version.update': this.$t(`m.audit['权限模板更新同步']`),
          'template.update.commit': this.$t(`m.audit['权限模板更新提交']`),
          'subject.template.create': this.$t(`m.audit['人员模板创建']`),
          'subject.template.delete': this.$t(`m.audit['人员模板删除']`),
          'subject.template.update': this.$t(`m.audit['人员模板更新']`),
          'subject.template.member.create': this.$t(`m.audit['人员模板成员增加']`),
          'subject.template.member.delete': this.$t(`m.audit['人员模板成员删除']`),
          'subject.template.group.delete': this.$t(`m.audit['用户组人员模板删除']`),
          'role.create': this.$t(`m.audit['管理员创建']`),
          'role.member.create': this.$t(`m.audit['管理员成员增加']`),
          'role.member.delete': this.$t(`m.audit['管理员成员删除']`),
          'role.member.update': this.$t(`m.audit['管理员成员修改']`),
          'role.member.policy.create': this.$t(`m.audit['管理员成员开启业务权限']`),
          'role.member.policy.delete': this.$t(`m.audit['管理员成员关闭业务权限']`),
          'role.update': this.$t(`m.audit['管理员更新']`),
          'role.delete': this.$t(`m.audit['管理员退出']`),
          'role.group.renew': this.$t(`m.audit['管理员用户组成员续期']`),
          'role.commonaction.create': this.$t(`m.audit['管理员常用操作新建']`),
          'role.commonaction.delete': this.$t(`m.audit['管理员常用操作删除']`),
          'event.rollback': this.$t(`m.audit['回滚事件']`),
          'approval.global.update': this.$t(`m.audit['修改默认审批流程']`),
          'approval.group.update': this.$t(`m.audit['修改用户组审批流程']`),
          'approval.action.update': this.$t(`m.audit['修改操作审批流程']`),
          'department.update': this.$t(`m.audit['组织架构同步']`),
          // 'department.group.delete': this.$t(`m.audit['删除组织用户组权限']`),
          'admin.api.allow.list.config.create': this.$t(`m.audit['ADMIN-API白名单创建']`),
          'admin.api.allow.list.config.delete': this.$t(`m.audit['ADMIN-API白名单删除']`),
          'authorization.api.allow.list.config.create': this.$t(`m.audit['授权类API白名单创建']`),
          'authorization.api.allow.list.config.delete': this.$t(`m.audit['授权类API白名单删除']`),
          'management.api.allow.list.config.create': this.$t(`m.audit['管理类API白名单创建']`),
          'management.api.allow.list.config.delete': this.$t(`m.audit['管理类API白名单删除']`),
          'group.transfer': this.$t(`m.audit['用户组权限交接']`),
          'action.sensitivity.level.update': this.$t(`m.audit['操作敏感等级更新']`),
          'role.update.notification.config': this.$t(`m.audit['续期通知更新']`)
        },
        currentMonth: '',
        noDetailType: NO_DETAIL_TYPE,
        onlyDescriptionType: ONLY_DESCRIPTION_TYPE,
        onlySubType: ONLY_SUB_TYPE,
        onlyExtraInfoType: ONLY_EXTRA_INFO_TYPE,
        deType: DE_TYPR,
        seType: SE_TYPE,
        dsType: DS_TYPE,
        onlyRoleType: ONLY_ROLE_TYPE,
        emptyData: {
          type: '',
          text: '',
          tip: '',
          tipType: ''
        },
        tableHeight: getWindowHeight() - 185
      };
    },
    computed: {
      ...mapGetters(['user'])
    },
    watch: {
      'pagination.current' (value) {
        this.currentBackup = value;
      }
    },
    created () {
      window.addEventListener('resize', () => {
        this.tableHeight = getWindowHeight() - 185;
      });
      this.currentMonth = this.getDate(this.getFormatDate(this.initDateTime));
      this.searchData = [
        {
          id: 'username',
          name: this.$t(`m.audit['操作者']`),
          remoteMethod: this.handleRemoteRtx
        },
        {
          id: 'type',
          name: this.$t(`m.audit['操作类型']`),
          remoteMethod: this.handleRemoteType
        },
        {
          id: 'object_type',
          name: this.$t(`m.audit['对象及类型']`),
          remoteMethod: this.handleRemoteObjectType
        },
        {
          id: 'source_type',
          name: this.$t(`m.audit['操作来源']`),
          children: [
            {
              name: this.$t(`m.audit['页面']`),
              id: 'web'
            },
            {
              name: 'API',
              id: 'openapi'
            },
            {
              name: this.$t(`m.audit['任务']`),
              id: 'task'
            }
          ],
          remoteMethod: () => {}
        },
        {
          id: 'status',
          name: this.$t(`m.audit['操作状态']`),
          children: [
            {
              name: this.$t(`m.audit['成功']`),
              id: 0
            },
            {
              name: this.$t(`m.audit['失败']`),
              id: 1
            },
            {
              name: this.$t(`m.audit['完成']`),
              id: 2
            },
            {
              name: this.$t(`m.audit['错误']`),
              id: 3
            }
          ],
          remoteMethod: () => {}
        }
      ];
      const isObject = payload => {
        return Object.prototype.toString.call(payload) === '[object Object]';
      };
      const currentQueryCache = this.getCurrentQueryCache();
      if (currentQueryCache && Object.keys(currentQueryCache).length) {
        if (currentQueryCache.limit) {
          this.pagination.limit = currentQueryCache.limit;
          this.pagination.current = currentQueryCache.current;
        }
        if (currentQueryCache.month) {
          this.currentMonth = currentQueryCache.month;
          this.initDateTime = new Date(`${currentQueryCache.month.slice(0, 4)}-${currentQueryCache.month.slice(4)}`);
        }
        for (const key in currentQueryCache) {
          if (key !== 'limit' && key !== 'current' && key !== 'month') {
            const curData = currentQueryCache[key];
            const tempData = this.searchData.find(item => item.id === key);
            if (isObject(curData)) {
              if (tempData) {
                this.searchValue.push({
                  id: key,
                  name: tempData.name,
                  values: [curData]
                });
                this.searchList.push(..._.cloneDeep(this.searchValue));
                this.searchParams[key] = curData.id;
              }
            } else if (tempData) {
              this.searchValue.push({
                id: key,
                name: tempData.name,
                values: [{
                  id: curData,
                  name: curData
                }]
              });
              this.searchList.push(..._.cloneDeep(this.searchValue));
              this.searchParams[key] = curData;
            } else {
              this.searchParams[key] = curData;
            }
          }
        }
      }
    },
    methods: {
      /**
       * 获取页面数据
       */
      async fetchPageData () {
        await this.fetchAuditList();
      },
      
      getDate (payload) {
        return payload.split('-').join('');
      },

      getFormatDate (payload) {
        const now = new Date(payload);
        const year = now.getFullYear();
        const month = now.getMonth() + 1;
        return `${year}-${month < 10 ? '0' + month.toString() : month}`;
      },

      getCellClass ({ row, column, rowIndex, columnIndex }) {
        if (columnIndex === 0 && ['role.update.notification.config'].includes(row.type)) {
          return 'audit-renewal-notice-cell-cls';
        }
        return '';
      },

      refreshCurrentQuery () {
        const { limit, current } = this.pagination;
        const params = {};
        const queryParams = {
          limit,
          current,
          month: this.currentMonth,
          role_name: this.user.role.name,
          ...this.searchParams
        };
        window.history.replaceState({}, '', `?${buildURLParams(queryParams)}`);
        for (const key in this.searchParams) {
          const tempObj = this.searchData.find(item => key === item.id);
          if (tempObj && tempObj.remoteMethod && typeof tempObj.remoteMethod === 'function') {
            if (this.searchList.length > 0) {
              this.emptyData.tipType = 'search';
              const tempData = this.searchList.find(item => item.id === key);
              params[key] = tempData.values[0];
            }
          } else {
            params[key] = this.searchParams[key];
          }
        }
        return {
          ...params,
          limit,
          current,
          month: this.currentMonth
        };
      },

      setCurrentQueryCache (payload) {
        window.localStorage.setItem('auditList', JSON.stringify(payload));
      },

      getCurrentQueryCache () {
        return JSON.parse(window.localStorage.getItem('auditList'));
      },

      async fetchAuditList (isLoading = false) {
        this.tableLoading = isLoading;
        this.setCurrentQueryCache(this.refreshCurrentQuery());
        const params = {
          limit: this.pagination.limit,
          offset: this.pagination.limit * (this.pagination.current - 1),
          month: this.currentMonth,
          source_type: '',
          type: '',
          object_type: '',
          object_id: '',
          status: '',
          ...this.searchParams
        };
        try {
          const { code, data } = await this.$store.dispatch('audit/getAuditList', params);
          this.pagination.count = data.count || 0;
          (data.results || []).forEach(item => {
            item.loading = false;
            item.expanded = false;
            item.detail = {};
          });
          this.tableList.splice(0, this.tableList.length, ...(data.results || []));
          this.emptyData = formatCodeData(code, this.emptyData, this.tableList.length === 0);
        } catch (e) {
          console.error(e);
          this.tableList = [];
          const { code } = e;
          this.emptyData = formatCodeData(code, this.emptyData);
          this.messageAdvancedError(e);
        } finally {
          this.tableLoading = false;
        }
      },

      handleRemoteRtx (value) {
        return fuzzyRtxSearch(value)
          .then(data => {
            return data.results;
          });
      },

      handleRemoteObjectType (value) {
        const list = [
          { id: 'group', name: this.$t(`m.myApply['用户组']`) },
          { id: 'user', name: this.$t(`m.common['用户']`) },
          { id: 'department', name: this.$t(`m.common['组织']`) },
          { id: 'template', name: this.$t(`m.myApply['权限模板']`) },
          { id: 'role', name: this.$t(`m.audit['角色']`) },
          { id: 'task', name: this.$t(`m.audit['任务']`) },
          { id: 'event', name: this.$t(`m.audit['审计事件']`) },
          { id: 'commonaction', name: this.$t(`m.audit['常用操作']`) },
          { id: 'action', name: this.$t(`m.common['操作']`) },
          { id: 'subject_template', name: this.$t(`m.memberTemplate['人员模板']`) }
        ];
        if (value === '') {
          return Promise.resolve(list);
        }
        return Promise.resolve(list.filter(item => item.name.indexOf(value) > -1));
      },

      handleRemoteType (value) {
        const list = [
          { id: 'user.policy.create', name: this.$t(`m.audit['用户权限增加']`) },
          { id: 'user.policy.update', name: this.$t(`m.audit['用户权限更新']`) },
          { id: 'user.policy.delete', name: this.$t(`m.audit['用户权限删除']`) },
          // { id: 'user.group.delete', name: this.$t(`m.audit['用户退出用户组']`) },
          // { id: 'user.role.delete', name: this.$t(`m.audit['用户退出管理员']`) },
          { id: 'user.temporary.policy.create', name: this.$t(`m.audit['用户临时权限增加']`) },
          { id: 'user.temporary.policy.delete', name: this.$t(`m.audit['用户临时权限删除']`) },
          { id: 'user.blacklist.member.create', name: this.$t(`m.audit['用户黑名单成员增加']`) },
          { id: 'user.blacklist.member.delete', name: this.$t(`m.audit['用户黑名单成员删除']`) },
          { id: 'user.permission.clean', name: this.$t(`m.audit['用户权限清理']`) },
          { id: 'group.create', name: this.$t(`m.audit['用户组创建']`) },
          { id: 'group.update', name: this.$t(`m.audit['用户组修改']`) },
          { id: 'group.delete', name: this.$t(`m.audit['用户组删除']`) },
          { id: 'group.member.create', name: this.$t(`m.audit['用户组成员增加']`) },
          { id: 'group.member.delete', name: this.$t(`m.audit['用户组成员删除']`) },
          { id: 'group.member.renew', name: this.$t(`m.audit['用户组成员续期']`) },
          { id: 'group.policy.create', name: this.$t(`m.audit['用户组权限增加']`) },
          { id: 'group.policy.update', name: this.$t(`m.audit['用户组权限更新']`) },
          { id: 'group.policy.delete', name: this.$t(`m.audit['用户组权限删除']`) },
          { id: 'group.template.create', name: this.$t(`m.audit['用户组添加权限模板']`) },
          { id: 'group.template.delete', name: this.$t(`m.audit['用户组删除权限模板']`) },
          { id: 'group.transfer', name: this.$t(`m.audit['用户组权限交接']`) },
          { id: 'template.create', name: this.$t(`m.audit['权限模板创建']`) },
          { id: 'template.update', name: this.$t(`m.audit['权限模板修改']`) },
          { id: 'template.delete', name: this.$t(`m.audit['权限模板删除']`) },
          { id: 'template.member.create', name: this.$t(`m.audit['权限模板成员增加']`) },
          { id: 'template.member.delete', name: this.$t(`m.audit['权限模板成员删除']`) },
          { id: 'template.member.update', name: this.$t(`m.audit['权限模板更新成员']`) },
          { id: 'template.preupdate.create', name: this.$t(`m.audit['权限模板预更新创建']`) },
          { id: 'template.preupdate.delete', name: this.$t(`m.audit['权限模板预更新删除']`) },
          { id: 'template.version.sync', name: this.$t(`m.audit['权限模板版本全量同步']`) },
          { id: 'template.version.update', name: this.$t(`m.audit['权限模板更新同步']`) },
          { id: 'template.update.commit', name: this.$t(`m.audit['权限模板更新提交']`) },
          { id: 'subject.template.create', name: this.$t(`m.audit['人员模板创建']`) },
          { id: 'subject.template.delete', name: this.$t(`m.audit['人员模板删除']`) },
          { id: 'subject.template.update', name: this.$t(`m.audit['人员模板更新']`) },
          { id: 'subject.template.member.create', name: this.$t(`m.audit['人员模板成员增加']`) },
          { id: 'subject.template.member.delete', name: this.$t(`m.audit['人员模板成员删除']`) },
          { id: 'subject.template.group.delete', name: this.$t(`m.audit['用户组人员模板删除']`) },
          { id: 'role.create', name: this.$t(`m.audit['管理员创建']`) },
          { id: 'role.update', name: this.$t(`m.audit['管理员更新']`) },
          { id: 'role.delete', name: this.$t(`m.audit['管理员退出']`) },
          { id: 'role.member.create', name: this.$t(`m.audit['管理员成员增加']`) },
          { id: 'role.member.delete', name: this.$t(`m.audit['管理员成员删除']`) },
          { id: 'role.member.update', name: this.$t(`m.audit['管理员成员修改']`) },
          { id: 'role.member.policy.create', name: this.$t(`m.audit['管理员成员开启业务权限']`) },
          { id: 'role.member.policy.delete', name: this.$t(`m.audit['管理员成员关闭业务权限']`) },
          { id: 'role.group.renew', name: this.$t(`m.audit['管理员用户组成员续期']`) },
          { id: 'role.commonaction.create', name: this.$t(`m.audit['管理员常用操作新建']`) },
          { id: 'role.commonaction.delete', name: this.$t(`m.audit['管理员常用操作删除']`) },
          { id: 'event.rollback', name: this.$t(`m.audit['回滚事件']`) },
          { id: 'approval.global.update', name: this.$t(`m.audit['修改默认审批流程']`) },
          { id: 'approval.group.update', name: this.$t(`m.audit['修改用户组审批流程']`) },
          { id: 'approval.action.update', name: this.$t(`m.audit['修改操作审批流程']`) },
          { id: 'department.update', name: this.$t(`m.audit['组织架构同步']`) },
          // { id: 'department.group.delete', name: this.$t(`m.audit['删除组织用户组权限']`) },
          { id: 'admin.api.allow.list.config.create', name: this.$t(`m.audit['ADMIN-API白名单创建']`) },
          { id: 'admin.api.allow.list.config.delete', name: this.$t(`m.audit['ADMIN-API白名单删除']`) },
          { id: 'authorization.api.allow.list.config.create', name: this.$t(`m.audit['授权类API白名单创建']`) },
          { id: 'authorization.api.allow.list.config.delete', name: this.$t(`m.audit['授权类API白名单删除']`) },
          { id: 'management.api.allow.list.config.create', name: this.$t(`m.audit['管理类API白名单创建']`) },
          { id: 'management.api.allow.list.config.delete', name: this.$t(`m.audit['管理类API白名单删除']`) },
          { id: 'action.sensitivity.level.update', name: this.$t(`m.audit['操作敏感等级更新']`) },
          { id: 'role.update.notification.config', name: this.$t(`m.audit['续期通知更新']`) }
        ];
        if (value === '') {
          return Promise.resolve(list);
        }
        return Promise.resolve(list.filter(item => item.name.indexOf(value) > -1));
      },

      resetPagination () {
        this.pagination = Object.assign({}, {
          limit: 10,
          current: 1,
          count: 0
        });
      },

      handleDateChange (date, type) {
        this.resetPagination();
        this.currentMonth = this.getDate(this.getFormatDate(date));
        this.fetchAuditList(true);
      },

      handleSearch (payload, result) {
        this.searchParams = payload;
        this.searchList = result;
        this.resetPagination();
        this.fetchAuditList(true);
      },

      handleEmptyClear () {
        this.searchParams = {};
        this.searchValue = [];
        this.emptyData.tipType = '';
        this.$refs.iamSearchSelect.$refs.searchSelect.isTagMultLine = false;
        this.resetPagination();
        this.fetchAuditList(true);
      },

      handleEmptyRefresh () {
        this.resetPagination();
        this.fetchAuditList(true);
      },

      handleChildEmptyRefresh (payload) {
        payload.expanded = false;
        this.handleExpandChange(payload);
      },

      pageChange (page) {
        if (this.currentBackup === page) {
          return;
        }
        this.pagination.current = page;
        this.fetchAuditList(true);
      },

      limitChange (currentLimit, prevLimit) {
        this.pagination.limit = currentLimit;
        this.pagination.current = 1;
        this.$refs.tableRef.clearFilter();
        this.fetchAuditList(true);
      },

      async handleExpandChange (row, expandedRows) {
        row.expanded = !row.expanded;
        this.$set(row, 'emptyData', {});
        if (this.noDetailType.includes(row.type)) {
          return;
        }
        if (row.expanded && Object.keys(row.detail).length < 1) {
          row.loading = true;
          try {
            const res = await this.$store.dispatch('audit/getAuditDetail', {
              id: row.id,
              month: this.currentMonth
            });
            row.detail = _.cloneDeep(res.data);
            if (this.seType.includes(row.detail.type)) {
              row.detail.sub_objects.forEach(item => {
                this.$set(item, 'version', row.detail.extra_info.version);
              });
            }
            if (this.dsType.includes(row.detail.type)) {
              row.detail.sub_objects.forEach(item => {
                this.$set(item, 'description', row.detail.description);
              });
            }
            if (this.onlyExtraInfoType.includes(row.detail.type)) {
              if (!['role.group.renew', 'template.version.sync'].includes(row.detail.type)) {
                row.detail.extra_info.policies.forEach(item => {
                  item.system_id = row.detail.extra_info.system.id;
                  item.system_name = row.detail.extra_info.system.name;
                });
              }
            }
          } catch (e) {
            console.error(e);
            row.emptyData = formatCodeData(e.code, { ...row.emptyData, ...{ tipType: 'refresh' } });
            this.messageAdvancedError(e);
          } finally {
            row.loading = false;
          }
        }
      }
    }
  };
</script>

<style lang="postcss" scoped>
.iam-audit-wrapper {
  .audit-search-select {
    margin-left: 10px;
    float: right;
  }
  .audit-table {
    margin-top: 16px;
    border-right: none;
    border-bottom: none;
    .bk-table-expanded-cell {
      padding: 0 30px 0 45px !important;
    }
    &.set-border {
      border-right: 1px solid #dfe0e5;
      border-bottom: 1px solid #dfe0e5;
    }
    .audit-detail-wrapper {
      position: relative;
      padding: 16px 50px 16px 165px;
      min-height: 60px;
      p {
        line-height: 24px;
      }
      .empty-wrapper {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        img {
          width: 60px;
        }
      }
    }
    .audit-detail-table {
      border: none;
      .bk-table-row-last {
        td {
          border-bottom: 1px solid #dfe0e5 !important;
        }
      }
    }
    /deep/ .audit-renewal-notice-cell-cls {
      .cell {
        display: none;
      }
    }
  }
}
</style>
