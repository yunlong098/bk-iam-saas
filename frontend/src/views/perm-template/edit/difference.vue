<template>
  <smart-action class="iam-template-diff-wrapper">
    <render-horizontal-block :label="$t(`m.common['选择实例']`)">
      <render-sync
        ref="syncRef"
        :id="$route.params.id"
        :add-action="addActions"
        :clone-action="cloneActions"
        @on-ready="handleSyncReady"
        @on-all-submit="handleAllSubmit" />
    </render-horizontal-block>
    <div slot="action">
      <bk-button
        theme="primary"
        :loading="isLoading"
        :disabled="(disabled || !isLastPage) && !isNoAddActions"
        @click="handleNextStep">
        <span v-bk-tooltips="{ content: $t(`m.info['请先确认完所有实例']`), disabled: !(!isLastPage && !isNoAddActions) }">
          {{ $t(`m.common['提交']`) }}
        </span>
      </bk-button>
      <bk-button
        style="margin-left: 10px;"
        :loading="prevLoading"
        :disabled="disabled"
        @click="handlePrevStep">
        {{ $t(`m.common['取消']`) }}
      </bk-button>
    </div>
  </smart-action>
</template>
<script>
  import store from '@/store';
  import { mapGetters } from 'vuex';
  import { leavePageConfirm } from '@/common/leave-page-confirm';
  import RenderSync from './sync';

  export default {
    name: '',
    components: {
      RenderSync
    },
    data () {
      return {
        curCom: 'diff',
        isLoading: false,
        prevLoading: false,
        addActions: [],
        disabled: true,
        isLastPage: false,
        isNoAddActions: false
      };
    },
    computed: {
      ...mapGetters('permTemplate', ['actions', 'preActionIds', 'cloneActions', 'preGroupOnePage'])
    },
    watch: {
      actions: {
        handler (value) {
          const tempActions = [];
          value.forEach((item, index) => {
            item.actions.forEach(act => {
              // if (['added'].includes(act.flag)) {
              if (['added'].includes(act.flag) || (['unchecked'].includes(act.tag) && act.checked)) {
                tempActions.push(act);
              }
            });
            (item.sub_groups || []).forEach(sub => {
              sub.actions.forEach(act => {
                // if (['added'].includes(act.flag)) {
                if (['added'].includes(act.flag) || (['unchecked'].includes(act.tag) && act.checked)) {
                  tempActions.push(act);
                }
              });
            });
          });
          this.addActions = tempActions;
          this.isNoAddActions = this.addActions.length < 1;
        },
        immediate: true
      }
    },
    beforeRouteEnter (to, from, next) {
      store.commit('setHeaderTitle', '');
      next();
    },
    created () {
      this.isOnePage = false;
    },
    methods: {
      async handleNextStep () {
        if (this.isNoAddActions) {
          this.handleUpdateCommit();
          return;
        }
        const { flag, groups, isNoAdd, emptyIndex } = this.$refs.syncRef.getData();
        groups.forEach(e => {
          e.actions.forEach(_ => {
            if (!_.resource_groups || !_.resource_groups.length) {
              _.resource_groups = (_.related_resource_types && _.related_resource_types.length) ? [{ id: '', related_resource_types: _.related_resource_types }] : [];
            }
          });
        });
        if (flag) {
          if (emptyIndex > -1) {
            this.messageWarn(this.$t(`m.info['权限模板用户组存在空实例']`, { value: emptyIndex }), 3000);
          }
          return;
        }
        if (this.preGroupOnePage) {
          if (isNoAdd) {
            this.handleUpdateCommit();
            return;
          }
          this.submitPreGroupSync(groups);
          return;
        }
        if (this.isLastPage) {
          this.submitPreGroupSync(groups);
        }
      },

      async preGroupSync (groups) {
        try {
          await this.$store.dispatch('permTemplate/preGroupSync', {
            id: this.$route.params.id,
            data: {
              groups
            }
          });
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },

      async submitPreGroupSync (groups) {
        this.isLoading = true;
        try {
          await this.preGroupSync(groups);
          await this.handleUpdateCommit(false);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          setTimeout(() => {
            this.isLoading = false;
          }, 300);
        }
      },

      async handleUpdateCommit (isLoading = true) {
        if (isLoading) {
          this.isLoading = true;
        }
        try {
          await this.$store.dispatch('permTemplate/updateCommit', {
            id: this.$route.params.id
          });
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'success',
            message: this.$t(`m.info['提交成功']`)
          });
          location.reload();
          this.$router.push({
            name: 'permTemplate'
          });
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          if (isLoading) {
            this.isLoading = false;
          }
        }
      },

      handleAllSubmit (payload) {
        this.isLastPage = payload;
      },

      handleSyncReady () {
        this.disabled = false;
      },

      handlePrevStep () {
        let cancelHandler = Promise.resolve();
        if (window.changeDialog) {
          cancelHandler = leavePageConfirm();
        }
        cancelHandler.then(async () => {
          this.prevLoading = true;
          try {
            await this.$store.dispatch('permTemplate/cancelPreUpdate', {
              id: this.$route.params.id
            });
            this.$router.go(-1);
          } catch (e) {
            console.error(e);
            this.messageAdvancedError(e);
          } finally {
            this.prevLoading = false;
          }
        }, _ => _);
      }
    }
  };
</script>
