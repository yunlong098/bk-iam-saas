<template>
  <!-- eslint-disable max-len -->
  <header class="header-nav-layout">
    <div :class="['logo', 'fl']" @click.stop="handleBackHome">
      <img :src="appLogo" :alt="$t(`m.nav['蓝鲸权限中心']`)">
      <span class="text">{{ appName }}</span>
    </div>
    <div class="header-breadcrumbs fl">
      <div class="nav-container">
        <span v-for="(item, i) in navData" :key="i">
          <h2
            v-if="item.show"
            class="header-nav-title"
            @click="handleSelect(item, i)"
            :class="index === i ? 'active' : ''"
          >
            {{ item.text }}
          </h2>
        </span>
      </div>
    </div>
    <div class="user fr">
      <div class="help-flag">
        <Icon type="help-fill" />
        <div :class="[
          'dropdown-panel',
          { 'lang-dropdown-panel': !curLanguageIsCn }
        ]">
          <div class="item" @click="handleOpenDocu">{{ $t(`m.common['产品文档']`) }}</div>
          <div class="item" @click="handleOpenVersion">
            {{ $t(`m.common['版本日志']`) }}
          </div>
          <div class="item" @click="handleOpenQuestion">
            {{ $t(`m.common['问题反馈']`) }}
          </div>
          <div class="item" @click="handleOpenSource">
            {{ $t(`m.common['开源社区']`) }}
          </div>
        </div>
      </div>
      <div class="lang-flag">
        <Icon :type="`icon-${['zh-cn', 'ja'].includes($i18n.locale) ? 'zh-cn' : $i18n.locale}`" />
        <div class="dropdown-panel">
          <div
            :class="[
              'item',
              {
                'item-active': $i18n.locale === item.value
              }
            ]"
            @click="handleChangeLocale(item.value)"
            v-for="item in languageList"
            :key="item.value"
          >
            <div class="lang-flex">
              <Icon :type="`icon-${item.value || 'zh-cn'}`" />
              <span class="lang-flex-label">{{ item.label }}</span>
            </div>
          </div>
        </div>
      </div>
      <p
        class="user-name"
        @click.stop="handleSwitchIdentity"
        data-test-id="header_btn_triggerSwitchRole"
      >
        {{ user.username }}
        <Icon
          type="down-angle"
          :class="['user-name-angle', { dropped: isShowUserDropdown }]"
        />
      </p>
      <transition name="toggle-slide">
        <section
          class="iam-grading-admin-list-wrapper"
          :style="style"
          v-show="isShowGradingWrapper"
          v-bk-clickoutside="handleClickOutSide"
        >
          <template>
            <!-- <div class="operation auth-manager" v-if="roleList.length">
                            <div class="user-dropdown-item " :title="$t(`m.nav['切换管理空间']`)" @click="handleManager">
                                <Icon type="grade-admin" class="iam-manager-icon" />
                                {{ $t(`m.nav['切换管理空间']`) }}
                            </div>
                        </div> -->
            <div class="operation">
              <div
                class="user-dropdown-item"
                :title="$t(`m.nav['退出登录']`)"
                @click="handleLogout"
              >
                <!-- <Icon type="logout" /> -->
                {{ $t(`m.nav['退出登录']`) }}
              </div>
            </div>
          </template>
        </section>
        <!-- <template>
                    <div class="operation right">
                        <div class="user-dropdown-item " @click="handleLogout">
                            <Icon type="logout" />
                            {{ $t(`m.nav['注销']`) }}
                        </div>
                    </div>
                </template> -->
      </transition>
    </div>
    <system-log v-model="showSystemLog" />
  </header>
</template>

<script>
  import { mapGetters } from 'vuex';
  // import IamGuide from '@/components/iam-guide/index.vue';
  import { leavePageConfirm } from '@/common/leave-page-confirm';
  import { il8n, language } from '@/language';
  import { bus } from '@/common/bus';
  import { formatI18nKey, jsonpRequest, getManagerMenuPerm, navDocCenterPath } from '@/common/util';
  import { NEED_CONFIRM_DIALOG_ROUTER } from '@/common/constants';
  import { getRouterDiff, getNavRouterDiff } from '@/common/router-handle';
  import SystemLog from '../system-log';
  import Cookies from 'js-cookie';
  import magicbox from 'bk-magic-vue';
  import logoSvg from '@/images/logo.svg';

  // 有选项卡的页面，user-group-detail 以及 perm-template-detail
  const getTabData = (routerName) => {
    const map = {
      '': [],
      permTemplateDetail: [
        {
          name: 'TemplateDetail',
          label: il8n('permTemplate', '模板详情')
        },
        {
          name: 'AttachGroup',
          label: il8n('permTemplate', '关联的组')
        }
      ],
      userGroupDetail: [
        {
          name: 'GroupDetail',
          label: il8n('userGroup', '组详情')
        },
        {
          name: 'GroupPerm',
          label: il8n('userGroup', '组权限')
        }
      ]
    };

    return map[routerName];
  };

  const getIdentityIcon = () => {
    const str = language === 'zh-cn' ? '' : '-en';
    return {
      '': `super-admin-new${str}`,
      super_manager: `super-admin-new${str}`,
      system_manager: `system-admin-new${str}`,
      rating_manager: `grade-admin-new${str}`
    };
  };

  export default {
    inject: ['reloadCurPage'],
    components: {
      SystemLog
      // IamGuide
    },
    props: {
      routeName: {
        type: String,
        default: ''
      },
      userGroupId: {
        type: [String, Number]
      }
    },
    data () {
      return {
        isShowUserDropdown: false,
        showSystemLog: false,
        isShowGradingWrapper: false,
        curIdentity: '',
        curRole: '',
        curRoleId: 0,
        iconMap: {
          '': 'personal-user',
          super_manager: 'super-admin',
          system_manager: 'system-admin',
          rating_manager: 'grade-admin',
          staff: 'personal-user'
        },
        identityIconMap: getIdentityIcon(),
        // super_manager: 超级用户, staff: 普通用户, system_manager: 系统管理员, rating_manager: 管理空间
        roleDisplayMap: {
          super_manager: this.$t(`m.myApproval['超级管理员']`),
          system_manager: this.$t(`m.nav['系统管理员']`),
          rating_manager: this.$t(`m.grading['管理空间']`),
          staff: this.$t(`m.nav['普通用户']`)
        },
        // curHeight: 500,

        hasPageTab: false,
        panels: [{ name: 'mission', label: '任务报表' }],
        active: 'mission',
        getTabData: getTabData,
        curRoleList: [],
        searchValue: '',
        showGuide: false,
        isShowHeader: false,
        placeholderValue: '',
        userGroupName: '',
        navData: [
          { text: this.$t(`m.nav['个人工作台']`), id: 0, show: true, type: ['staff'] },
          { text: this.$t(`m.nav['管理空间']`), id: 1, show: true, type: ['all_manager'] },
          { text: this.$t(`m.nav['统计分析']`), id: 2, show: false, type: ['super_manager'] },
          { text: this.$t(`m.nav['平台管理']`), id: 3, show: false, type: ['super_manager'] }
        ],
        defaultRouteList: ['myPerm', 'userGroup', 'audit', 'user', 'addGroupPerm'],
        systemNoSuperList: ['myPerm', 'userGroup', 'audit', 'resourcePermiss', 'addGroupPerm'],
        isRatingChange: false,
        haveManager: false,
        showNavDataLength: 0,
        curHeight: 78,
        languageList: [
          {
            label: '中文',
            value: 'zh-cn'
          },
          {
            label: 'English',
            value: 'en'
          }
        ],
        curFromName: ''
      };
    },
    computed: {
      ...mapGetters([
        'navStick',
        'headerTitle',
        'backRouter',
        'user',
        'mainContentLoading',
        'roleList',
        'index',
        'navCurRoleId',
        'externalSystemId',
        'versionLogs'
      ]),
      ...mapGetters('userGlobalConfig', ['globalConfig']),
      style () {
        return {
          // height: `${this.roleList.length ? this.curHeight : 46}px`
          height: `46px`
        };
      },
      curAccountLogo () {
        return [].slice.call(this.user.username)[0].toUpperCase() || '-';
      },
      isHide () {
        return this.$route.query.system_id && this.$route.query.tid;
      },
      isShowSearch () {
        return this.searchValue === '';
      },
      appName () {
        // 如果未获取到配置，使用默认title
        return this.globalConfig && this.globalConfig.i18n ? this.globalConfig.i18n.productName : this.$t('m.nav["蓝鲸权限中心"]');
      },
      appLogo () {
        // 如果未获取到配置，使用默认logo
        const src = this.globalConfig.appLogo || logoSvg;
        return src;
      }
    },
    watch: {
      $route: function (to, from) {
        this.curFromName = from.name || '';
        this.hasPageTab = !!to.meta.hasPageTab;
        if (['permTemplateDetail', 'userGroupDetail'].includes(to.name)) {
          this.panels = this.getTabData(to.name);
          let active = to.query.tab || this.panels[0].name;
          if (active === 'group_perm') {
            active = 'GroupPerm';
          }
          this.active = active;
        }
      },
      user: {
        handler (value) {
          this.curRoleId = value.role.id || 0;
          this.curRole = value.role.type || 'staff';
          this.placeholderValue = this.$t(`m.common['切换身份']`);
        },
        deep: true
      },
      roleList: {
        handler (newValue, oldValue) {
          this.curRoleList.splice(0, this.curRoleList.length, ...newValue);
          if (this.curRoleList.length) {
            this.setTabRoleData();
          }
          this.setNavData();
        },
        immediate: true
      },
      isShowGradingWrapper (value) {
        if (!value) {
          this.searchValue = '';
        }
      },
      routeName: {
        handler (value) {
          // const isSystemNoSuper = this.roleList.find((item) => ['system_manager'].includes(item.type) && !['super_manager'].includes(item.type));
          // const list = isSystemNoSuper ? this.systemNoSuperList : this.defaultRouteList;
          const list = this.defaultRouteList;
          const index = list.findIndex((item) => item === value);
          if (index > -1) {
            ['addGroupPerm'].includes(value)
              ? this.fetchUserGroup()
              : this.$store.commit('updateIndex', index);
          }
        },
        immediate: true
      },
      navData: {
        handler (newValue, oldValue) {
          if ((!oldValue || (oldValue && oldValue.length < 1)) && newValue.length > 0) {
            this.showGuide = true;
          }
          this.showNavDataLength = newValue.filter((e) => e.show).length;
          this.haveManager
            = this.showNavDataLength
              && this.showGuide
              && newValue.find((item) => item.type.includes('all_manager') && item.show);
        },
        immediate: true,
        deep: true
      }
    },
    created () {
      const { id, name, type } = this.user.role;
      this.curRole = type;
      this.curIdentity = name;
      this.curRoleId = id;
      this.$once('hook:beforeDestroy', () => {
        bus.$off('reload-page');
        bus.$off('refresh-role');
        bus.$off('on-set-tab');
        bus.$off('rating-admin-change');
      });
      this.setNavData();
    },
    mounted () {
      bus.$on('on-set-tab', (data) => {
        this.active = data;
      });

      bus.$on('rating-admin-change', () => {
        const data = this.navData.find((e) => e.type.includes('staff'));
        this.isRatingChange = true;
        this.handleSelect(data, 0);
      });
    },
    methods: {
      // 获取用户组详情
      async fetchUserGroup () {
        const params = {
          id: this.userGroupId
        };
        if (this.externalSystemId) {
          params.hidden = false;
        }
        try {
          const res = await this.$store.dispatch('userGroup/getUserGroupDetail', params);
          this.$nextTick(() => {
            this.$set(this, 'userGroupName', res.data.name);
          });
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        }
      },
      handleClickOutSide (e) {
        this.isShowGradingWrapper = false;
      },

      // super_manager: 超级用户, staff: 普通用户, system_manager: 系统管理员, rating_manager: 管理空间
      isShowSuperManager (value) {
        if (value.type === 'super_manager') {
          return true;
        }
      },
      isShowSystemManager (value) {
        if (value.type === 'system_manager') {
          return true;
        }
      },
      isShowRatingManager (value) {
        if (value.type === 'rating_manager') {
          return true;
        }
      },

      handleInput (value) {
        this.curRoleList = this.roleList.filter((item) => item.name.indexOf(value) > -1);
      },

      handleOpenVersion () {
        this.showSystemLog = true;
      },

      handleOpenDocu () {
        navDocCenterPath(this.versionLogs, '/UserGuide/Introduce/README.md', true);
      },

      handleOpenQuestion () {
        window.open(window.BK_CE_URL);
      },

      handleOpenSource () {
        window.open(`https://github.com/TencentBlueKing/bk-iam`);
      },

      back () {
        const curRouterName = this.$route.name;
        const needConfirmFlag = NEED_CONFIRM_DIALOG_ROUTER.includes(curRouterName);
        let cancelHandler = Promise.resolve();
        if (window.changeDialog && needConfirmFlag) {
          cancelHandler = leavePageConfirm();
        }
        cancelHandler.then(
          () => {
            if (this.$route.name === 'applyCustomPerm') {
              this.$router.push({
                name: 'applyJoinUserGroup'
              });
            } else if (this.backRouter === -1) {
              history.go(-1);
            } else {
              this.$router.push({
                name: this.backRouter,
                params: this.$route.params,
                query: this.$route.query
              });
            }
          },
          (_) => _
        );
      },

      // 需要切换的时候刷新不同菜单下的同名路由
      handleRefreshSameRoute (payload) {
        if (['resourcePermiss', 'sensitivityLevel', 'approvalProcess'].includes(this.$route.name) && [1, 3].includes(payload)) {
          this.reloadCurPage(this.$route);
        }
      },

      async updateRouter (navIndex = 0) {
        let difference = [];
        const permResult = getManagerMenuPerm(this.roleList);
        // const list = permResult.includes('hasSystemNoSuperManager') ? this.systemNoSuperList : this.defaultRouteList;
        const list = this.defaultRouteList;
        if (navIndex === 1) {
          // 不同导航栏下相同的权限路由名称跳转增加延时时间，防止相同接口调用多次被节流
          await this.$store.dispatch('userInfo');
          const type = this.curRole;
          difference = getRouterDiff(type);
          this.$store.commit('updataRouterDiff', type);
        } else {
          difference = getNavRouterDiff(navIndex, permResult);
          this.$store.commit('updataNavRouterDiff', navIndex);
        }
        this.handleRefreshSameRoute(navIndex);
        const curRouterName = this.$route.name;
        if (difference.length) {
          if (difference.includes(curRouterName)) {
            this.$store.commit('setHeaderTitle', '');
            window.localStorage.removeItem('iam-header-title-cache');
            window.localStorage.removeItem('iam-header-name-cache');
            this.$router.push({
              name: this.isRatingChange ? 'myManageSpace' : list[navIndex],
              params: navIndex === 1 ? { id: this.user.role.id, entry: 'updateRole' } : {}
            });
          } else {
            // 修复当前是添加组权限页面点击其他角色菜单会再次跳到权限管理
            // 处理二级管理空间点击staff菜单不刷新路由问题
            // 处理超级管理员账号下头部导航没选择默认路由问题
            const OtherRoute = [
              'gradingAdminDetail',
              'gradingAdminCreate',
              'gradingAdminClone',
              'gradingAdminEdit',
              'myManageSpace',
              'myManageSpaceCreate',
              'secondaryManageSpaceCreate',
              'secondaryManageSpaceDetail',
              'secondaryManageSpaceEdit',
              'addGroupPerm',
              'authorBoundaryEditFirstLevel'
            ];
            if (OtherRoute.includes(curRouterName)) {
              this.$router.push({
                name: list[navIndex]
              });
            }
          }
          // 更新后重置我的管理空间跳转开关
          this.isRatingChange = false;
        }
      },

      async handleSelect (roleData, index) {
        if (window.changeDialog && NEED_CONFIRM_DIALOG_ROUTER.includes(this.$route.name)) {
          const cancelHandler = leavePageConfirm();
          cancelHandler.then(
            () => {
              this.handleHeaderNav(roleData, index);
            },
            (_) => _
          );
        } else {
          this.handleHeaderNav(roleData, index);
        }
      },

      // 处理当前页未保存信息切换头部导航栏校验
      async handleHeaderNav (roleData, index) {
        const currentData = { ...roleData };
        this.navData.forEach((e) => {
          e.active = false;
        });
        this.$set(currentData, 'active', true);
        this.$store.commit('updateIndex', index);
        window.localStorage.setItem('index', index);
        this.isShowGradingWrapper = false;
        this.isShowUserDropdown = false;
        try {
          await this.$store.dispatch('role/updateCurrentRole', { id: currentData.id });
          bus.$emit('nav-change', { id: currentData.id }, index);
          this.updateRouter(index);
        } catch (err) {
          if (index === 1 && this.curRoleList.length) {
            this.resetLocalStorage();
            const { id, type, name } = this.curRoleList[0];
            this.$set(currentData, 'id', id);
            this.navCurRoleId = id;
            this.curRoleId = id;
            this.curRole = type;
            this.$store.commit('updateCurRoleId', id);
            this.$store.commit('updateIdentity', { id, type, name });
            this.$store.commit('updateNavId', id);
            this.$store.commit('updateIndex', index);
            window.localStorage.setItem('index', index);
            bus.$emit('nav-change', { id: currentData.id }, index);
            await this.$store.dispatch('role/updateCurrentRole', { id });
            this.updateRouter(index, type);
          }
        }
      },

      async handleBackHome () {
        await this.$store.dispatch('role/updateCurrentRole', { id: 0 });
        await this.$store.dispatch('userInfo');
        this.$store.commit('updateIndex', 0);
        window.localStorage.setItem('index', 0);
        this.$router.push({ name: 'myPerm' });
      },

      setMagicBoxLocale (targetLocale) {
        const { lang, locale } = magicbox;
        const magicBoxLanguageMap = {
          'zh-cn': lang.zhCN,
          en: lang.enUS
        };
        locale.use(magicBoxLanguageMap[formatI18nKey()]);
        window.CUR_LANGUAGE = formatI18nKey();
        this.$i18n.locale = formatI18nKey();
      },
        
      async handleChangeLocale (language) {
        const curDomain = window.BK_DOMAIN || window.location.hostname.replace(/^.*(\.[^.]+\.[^.]+)$/, '$1');
        Cookies.remove(
          'blueking_language',
          {
            expires: -1,
            domain: curDomain,
            path: ''
          }
        );
        // 增加语言cookie有效期为一年
        const expires = new Date();
        expires.setFullYear(expires.getFullYear() + 1);
        Cookies.set(
          'blueking_language',
          language,
          {
            expires: expires,
            domain: curDomain
          }
        );
        this.setMagicBoxLocale(language);
        if (window.BK_COMPONENT_API_URL) {
          const url = `${window.BK_COMPONENT_API_URL}/api/c/compapi/v2/usermanage/fe_update_user_language/`;
          try {
            await jsonpRequest(url, { language });
          } finally {
            window.location.reload();
          }
          return;
        }
        window.location.reload();
      },

      handleSwitchIdentity () {
        // this.curHeight = document.getElementsByClassName('user-dropdown')[0].offsetHeight
        this.isShowGradingWrapper = !this.isShowGradingWrapper;
      },
      
      handleLogout () {
        window.localStorage.removeItem('iam-header-title-cache');
        window.localStorage.removeItem('iam-header-name-cache');
        window.localStorage.removeItem('applyGroupList');
        window.location = `${window.LOGIN_SERVICE_URL}/?c_url=${encodeURIComponent(window.location.href)}&is_from_logout=1`;
      },

      handleManager () {
        const data = this.navData.find((e) => !e.type.includes('staff'));
        this.handleSelect(data, 1);
        this.$store.commit('updateSelectManager', true);
      },

      resetLocalStorage () {
        window.localStorage.removeItem('customPermProcessList');
        window.localStorage.removeItem('gradeManagerList');
        window.localStorage.removeItem('auditList');
        window.localStorage.removeItem('joinGroupProcessList');
        window.localStorage.removeItem('groupList');
        window.localStorage.removeItem('templateList');
        window.localStorage.removeItem('applyGroupList');
        window.localStorage.removeItem('iam-header-title-cache');
        window.localStorage.removeItem('iam-header-name-cache');
        window.localStorage.removeItem('index');
      },

      // 根据角色设置
      setTabRoleData () {
        const superManager = this.curRoleList.find((e) => e.type === 'super_manager');
        const systemManager = this.curRoleList.find((e) => e.type === 'system_manager');
        const allManager = this.curRoleList.find((e) => e.type !== 'staff');
        this.navData.forEach((element, i) => {
          element.active = i === this.index;
          const rolesMap = [
            [
              () => element.type.includes('super_manager') && superManager,
              () => {
                element = Object.assign(element, { id: superManager.id, show: true });
              }
            ],
            [
              () => element.type.includes('system_manager') && systemManager && !superManager,
              () => {
                element = Object.assign(element, { id: systemManager.id, show: true });
              }
            ],
            [
              () => element.type.includes('all_manager') && allManager,
              () => {
                element = Object.assign(element, { id: this.navCurRoleId || allManager.id });
              }
            ]
          ];
          const getRole = rolesMap.find((item) => item[0]());
          if (getRole) {
            getRole[1]();
          }
        });
        this.$store.commit('updateNavData', this.navData);
      },

      setNavData () {
        this.$nextTick(() => {
          for (let i = 0; i < this.navData.length; i++) {
            if (this.navData[i].type.includes('all_manager')) {
              this.navData[i].show = !!this.roleList.length;
              break;
            }
          }
        });
      }
    }
  };
</script>

<style>
@import "./index";
</style>
