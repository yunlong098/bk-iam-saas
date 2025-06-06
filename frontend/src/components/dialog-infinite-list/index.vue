<template>
  <div class="dialog-infinite-list" @scroll="rootScroll">
    <div class="ghost-wrapper" :style="ghostStyle"></div>
    <div class="render-wrapper" ref="content">
      <div class="organization-content">
        <div
          v-bk-tooltips="{ content: nameType(item), placements: ['top-end'] }"
          v-for="(item, index) in renderOrganizationList"
          :key="item.id"
          :class="[
            'node-item',
            'organization-item',
            { 'focus': index === organizationIndex || selectedNode(item) },
            { 'is-disabled': disabledNode(item) }
          ]"
          @click.stop="nodeClick(item)">
          <div class="node-item-checkbox" v-if="item.showRadio">
            <span class="node-checkbox"
              :class="{
                'is-disabled': disabledNode(item),
                'is-checked': selectedNode(item),
                'is-indeterminate': item.indeterminate
              }"
              @click.stop="handleNodeClick(item)">
            </span>
          </div>
          <Icon
            type="file-close"
            :class="[
              'node-icon',
              'folder-icon',
              { 'active': selectedNode(item) && !item.disabled }
            ]"
          />
          <span :class="['node-item-name', 'organization-name', { 'is-disabled': disabledNode(item) }]">
            {{ item.name }}
          </span>
          <span
            v-if="item.showCount && enableOrganizationCount"
            class="node-user-count"
          >
            {{ '(' + item.count + ')' }}
          </span>
        </div>
      </div>
      <div class="user-content">
        <div
          v-bk-tooltips="{ content: nameType(item), placements: ['top-end'] }"
          v-for="(item, index) in renderUserList"
          :key="item.id"
          :class="[
            'node-item',
            'user-item',
            { 'focus': index === userIndex || selectedNode(item) },
            { 'is-disabled': disabledNode(item) }
          ]"
          @click.stop="nodeClick(item)">
          <div class="node-item-checkbox" v-if="item.showRadio">
            <span class="node-checkbox"
              :class="{
                'is-disabled': disabledNode(item),
                'is-checked': selectedNode(item),
                'is-indeterminate': item.indeterminate
              }"
              @click.stop="handleNodeClick(item)">
            </span>
          </div>
          <Icon
            type="personal-user"
            :class="[
              'node-icon',
              { 'active': selectedNode(item) && !item.disabled }
            ]"
          />
          <span
            :class="['node-item-name', 'user-name', { 'is-disabled': disabledNode(item) }]"
          >
            {{ item.username }}
            <template v-if="item.name !== ''">
              ({{ item.name }})
            </template>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import _ from 'lodash';
  import { mapGetters } from 'vuex';
  import { getParamsValue } from '@/common/util';
  import { NO_VERIFY_ORG_ROUTES } from '@/common/constants';

  export default {
    name: 'dialog-infinite-list',
    inject: {
      getGroupAttributes: { value: 'getGroupAttributes', default: null }
    },
    props: {
      // 所有数据
      allData: {
        type: Array,
        default: () => []
      },
      // 每个节点的高度
      itemHeight: {
        type: Number,
        default: 32
      },

      focusIndex: {
        type: Number,
        default: -1
      },

      isDisabled: {
        type: Boolean,
        default: false
      },
      hasSelectedDepartments: {
        type: Array,
        default: () => []
      },
      hasSelectedUsers: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        startIndex: 0,
        endIndex: 0,
        currentFocusIndex: this.focusIndex,
        organizationIndex: -1,
        userIndex: -1,
        enableOrganizationCount: window.ENABLE_ORGANIZATION_COUNT.toLowerCase() === 'true'
      };
    },
    computed: {
      ...mapGetters(['user', 'externalSystemsLayout']),
      ghostStyle () {
        return {
            height: this.allData.length * this.itemHeight + 'px'
        };
      },
      // 页面渲染的数据
      renderData () {
        // 渲染在可视区的数据
        return this.allData.slice(this.startIndex, this.endIndex);
      },
      renderOrganizationList () {
        return this.renderData.filter(item => item.type === 'depart');
      },
      renderUserList () {
        return this.renderData.filter(item => item.type === 'user');
      },
      disabledNode () {
        return (payload) => {
          const isDisabled = payload.disabled || this.isDisabled;
          return this.getGroupAttributes ? isDisabled || (this.getGroupAttributes().source_from_role && payload.type === 'depart') : isDisabled;
        };
      },
      isStaff () {
        return this.user.role.type === 'staff';
      },
      // 不需要校验组织架构授权范围的页面模块
      isUnLimitedScope () {
        return getParamsValue('search_scene') === 'add' || NO_VERIFY_ORG_ROUTES.includes(this.$route.name);
      },
      nameType () {
        return (payload) => {
          const { name, type, username, full_name: fullName, disabled } = payload;
          if (disabled) {
            return this.$t(`m.common['该成员已添加']`);
          }
          const typeMap = {
            user: () => {
              if (fullName) {
                return fullName;
              }
              return name ? `${username}(${name})` : username;
            },
            depart: () => {
              return fullName || name;
            }
          };
          return typeMap[type] ? typeMap[type]() : typeMap['user']();
        };
      },
      selectedNode () {
        return (payload) => {
          const { id, name, username, disabled } = payload;
          // 如果之前已选且禁用直接返回
          if (disabled && payload.isSelected) {
            return true;
          }
          const isExistSelected = this.hasSelectedDepartments.length > 0 || this.hasSelectedUsers.length > 0;
          if (isExistSelected) {
            const hasDeparts = this.hasSelectedDepartments.map(item => `${item.name}&${String(item.id)}`).includes(`${name}&${String(id)}`);
            const hasUsers = this.hasSelectedUsers.map(item => item.username).includes(username);
            payload.isSelected = hasDeparts || hasUsers;
            return payload.isSelected;
          }
          return false;
        };
      }
    },
    watch: {
      focusIndex (value) {
        this.currentFocusIndex = value;
        if (value === -1) {
          this.organizationIndex = -1;
          this.userIndex = -1;
        } else {
          this.computedIndex();
        }
      }
    },
    mounted () {
      this.endIndex = Math.ceil(this.$el.clientHeight / this.itemHeight);
    },
    methods: {
      /**
       * 滚动回调函数
       */
      rootScroll: _.throttle(function () {
        this.organizationIndex = -1;
        this.userIndex = -1;
        this.$emit('update:focusIndex', -1);
        this.updateRenderData(this.$el.scrollTop);
      }, 0),

      /**
       * 更新可视区渲染的数据列表
       *
       * @param {Number} scrollTop 滚动条高度
       */
      updateRenderData (scrollTop = 0) {
        // 可视区显示的条数
        const count = Math.ceil(this.$el.clientHeight / this.itemHeight);
        // 滚动后可视区新的 startIndex
        const newStartIndex = Math.floor(scrollTop / this.itemHeight);
        // 滚动后可视区新的 endIndex
        const newEndIndex = newStartIndex + count;
        this.startIndex = newStartIndex;
        this.endIndex = newEndIndex;
        this.$refs.content.style.transform = `translate3d(0, ${newStartIndex * this.itemHeight}px, 0)`;
      },

      /**
       * 搜索时支持键盘上下键的 hover index 计算
       */
      computedIndex () {
        if (this.renderOrganizationList.length && this.renderUserList.length) {
          if (this.currentFocusIndex < this.renderOrganizationList.length) {
            this.organizationIndex = this.currentFocusIndex;
            this.userIndex = -1;
          } else {
            this.userIndex = this.currentFocusIndex - this.renderOrganizationList.length;
            this.organizationIndex = -1;
          }
        } else if (this.renderOrganizationList.length && !this.renderUserList.length) {
          this.organizationIndex = this.currentFocusIndex;
        } else if (!this.renderOrganizationList.length && this.renderUserList.length) {
          this.userIndex = this.currentFocusIndex;
        } else {
          this.organizationIndex = -1;
          this.userIndex = -1;
        }

        // console.warn('organizationIndex: ' + this.organizationIndex)
        // console.warn('userIndex: ' + this.userIndex)
      },

      setCheckStatusByIndex () {
        if (this.organizationIndex !== -1) {
          const currentOrganizationItem = this.renderOrganizationList.find(
            (item, index) => index === this.organizationIndex
          );
          if (!currentOrganizationItem.disabled) {
            currentOrganizationItem.isSelected = !currentOrganizationItem.isSelected;
            this.$emit('on-checked', currentOrganizationItem.isSelected, !currentOrganizationItem.isSelected, currentOrganizationItem.isSelected, currentOrganizationItem);
          }
        }

        if (this.userIndex !== -1) {
          const currentUserItem = this.renderUserList.find((item, index) => index === this.userIndex);
          if (!currentUserItem.disabled) {
            currentUserItem.isSelected = !currentUserItem.isSelected;
            this.$emit('on-checked', currentUserItem.isSelected, !currentUserItem.isSelected, currentUserItem.isSelected, currentUserItem);
          }
        }
      },

      /**
       * 点击节点
       *
       * @param {Object} node 当前节点
       */
      async nodeClick (node) {
        if (this.isDisabled || (this.getGroupAttributes && this.getGroupAttributes().source_from_role && node.type === 'depart')) {
          return;
        }
        // 增加蓝盾侧限制勾选组织架构业务
        if (node.limitOrgNodeTip) {
          this.$emit('on-show-limit', { title: node.limitOrgNodeTip });
          return;
        }
        this.$emit('on-click', node);
        if (!node.disabled) {
          if (this.isStaff || this.isUnLimitedScope) {
            node.isSelected = !node.isSelected;
            this.$emit('on-checked', node.isSelected, !node.isSelected, node.isSelected, node);
          } else {
            const result = await this.fetchSubjectScopeCheck(node);
            if (result) {
              node.isSelected = !node.isSelected;
              this.$emit('on-checked', node.isSelected, !node.isSelected, node.isSelected, node);
            } else {
              this.messageWarn(this.$t(`m.verify['当前选择项不在授权范围内']`), 3000);
            }
          }
        }
      },

      async handleNodeClick (node) {
        const isDisabled = node.disabled || this.isDisabled || (this.getGroupAttributes && this.getGroupAttributes().source_from_role && node.type === 'depart');
        if (!isDisabled) {
          // 增加蓝盾侧限制勾选组织架构业务
          if (node.limitOrgNodeTip) {
            this.$emit('on-show-limit', { title: node.limitOrgNodeTip });
            return;
          }
          if (this.isStaff) {
            node.isSelected = !node.isSelected;
            this.$emit('on-checked', node.isSelected, !node.isSelected, true, node);
          } else {
            if (getParamsValue('search_scene') && getParamsValue('search_scene') === 'add') {
              node.isSelected = !node.isSelected;
              this.$emit('on-checked', node.isSelected, !node.isSelected, node.isSelected, node);
            } else {
              const result = await this.fetchSubjectScopeCheck(node);
              if (result) {
                node.isSelected = !node.isSelected;
                this.$emit('on-checked', node.isSelected, !node.isSelected, node.isSelected, node);
              } else {
                this.messageWarn(this.$t(`m.verify['当前选择项不在授权范围内']`), 3000);
              }
            }
          }
        }
      },

      // 校验组织架构选择器部门/用户范围是否满足条件
      async fetchSubjectScopeCheck ({ type, id, username }) {
        const subjectItem = {
          depart: () => {
            return {
              subjects: [{
                type: 'department',
                id
                     
              }]
            };
          },
          user: () => {
            return {
              subjects: [{
                type: 'user',
                id: username
              }]
            };
          }
        };
        const params = subjectItem[type]();
        const { code, data } = await this.$store.dispatch('organization/getSubjectScopeCheck', params);
        if (code === 0) {
          const { id: subjectId, type: subjectType } = params.subjects[0];
          const result = data && data.length
            && data.find(item => item.type === subjectType && item.id === String(subjectId));
          return result;
        }
      }
    }
  };
</script>

<style lang="postcss">
.dialog-infinite-list {
  height: 862px;
  font-size: 14px;
  overflow: auto;
  position: relative;
  will-change: transform;
  &::-webkit-scrollbar {
    width: 4px;
    background-color: lighten(transparent, 80%);
  }
  &::-webkit-scrollbar-thumb {
    height: 5px;
    border-radius: 2px;
    background-color: #e6e9ea;
  }
  .ghost-wrapper,
  .render-wrapper {
    position: absolute;
    left: 0;
    top: 0;
    right: 0;
    z-index: -1;
  }
  .ghost-wrapper {
    z-index: -1;
  }
  .organization-content,
  .user-content {
    .node-item {
      display: flex;
      align-items: center;
      padding: 5px 10px;
      border-radius: 2px;
      cursor: pointer;
      .node-checkbox {
        display: inline-block;
        position: relative;
        top: 3px;
        width: 16px;
        height: 16px;
        margin: 0 6px 0 0;
        border: 1px solid #979ba5;
        border-radius: 2px;
        &.is-checked {
          border-color: #3a84ff;
          background-color: #3a84ff;
          background-clip: border-box;
          &:after {
            content: "";
            position: absolute;
            top: 1px;
            left: 4px;
            width: 4px;
            height: 8px;
            border: 2px solid #fff;
            border-left: 0;
            border-top: 0;
            transform-origin: center;
            transform: rotate(45deg) scaleY(1);
          }
          &.is-disabled {
            background-color: #dcdee5;
          }
        }
        &.is-disabled {
          border-color: #dcdee5;
          cursor: not-allowed;
        }
        &.is-indeterminate {
          border-width: 7px 4px;
          border-color: #3a84ff;
          background-color: #fff;
          background-clip: content-box;
          &:after {
            visibility: hidden;
          }
        }
      }
      .node-icon {
        font-size: 16px;
        color: #a3c5fd;
        margin-right: 5px;
        &.file-icon {
          font-size: 17px;
        }
        &.active {
          color: #3a84ff;
        }
      }
      .node-user-count {
        color: #c4c6cc;
      }
      &:hover,
      &.focus {
        color: #3a84ff;
        background: #eef4ff;
        .node-icon,
        .node-user-count {
          color: #3a84ff;
        }
      }
      &.is-disabled {
        color: #c4c6cc;
        background-color: transparent;
        cursor: not-allowed;
        .node-icon,
        .node-user-count {
          color: #c4c6cc;
        }
        &:hover {
          background-color: #eee;
        }
      }
      &-name {
        display: inline-block;
        max-width: calc(100% - 72px);
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        vertical-align: top;
        &:hover {
          color: #3a84ff;
        }
        &.is-disabled {
          &:hover {
            color: #c4c6cc;
          }
        }
      }
      &-checkbox {
        margin-right: 5px;
      }
    }
  }
}
</style>
