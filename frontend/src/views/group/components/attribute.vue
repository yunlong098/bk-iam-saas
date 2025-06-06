<template>
  <div>
    <div class="attribute-item"
      v-for="(item, index) in attrValues"
      :key="index"
      :class="index !== 0 ? 'set-margin-top' : ''">
      <div class="attribute-select">
        <bk-select
          v-model="item.id"
          :clearable="false"
          :disabled="item.disabled || isDisabledMode"
          searchable
          style="width: 160px;"
          @selected="handleAttributeSelected(...arguments, item)">
          <bk-option v-for="option in list"
            :key="option.id"
            :id="option.id"
            :name="option.display_name">
          </bk-option>
        </bk-select>
        <!-- 单独处理dbm系统业务个别属性id需要展示不同的组件 -->
        <template v-if="isMemberSelector(item)">
          <BkUserSelector
            ref="selector"
            class="sub-selector-content"
            :api="userApi"
            :value="formatMemberValue(item)"
            :disabled="formatDisabled(item)"
            :placeholder="$t(`m.verify['请输入']`)"
            :empty-text="$t(`m.common['无匹配人员']`)"
            @change="handleMemberChange(...arguments, item)"
          />
        </template>
        <template v-else>
          <bk-select
            v-model="item.selecteds"
            class="sub-selector-content"
            :ref="`${item.id}&${index}&valueRef`"
            :multiple="true"
            searchable
            :disabled="formatDisabled(item)"
            :loading="item.loading"
            :remote-method="handleRemoteValue"
            @clear="handleClear(...arguments, item)"
            @toggle="handleAttrValueToggle(...arguments, index, item)"
            @selected="handleAttrValueSelected(...arguments, item)">
            <bk-option v-for="option in attrValueListMap[item.id]"
              :key="option.id"
              :id="option.id"
              :name="option.display_name">
              <template v-if="option.id !== ''">
                <span>{{ option.display_name }}</span>
              </template>
              <template v-else>
                <div v-bkloading="{ isLoading: item.isScrollRemote, size: 'mini' }"></div>
              </template>
            </bk-option>
          </bk-select>
        </template>
      </div>
      <div class="attribute-action" v-if="isShowAction(item)">
        <Icon type="add-hollow" @click="addAttribute" />
        <Icon
          type="reduce-hollow"
          :class="attrValues.length === 1 ? 'disabled' : ''"
          style="margin-left: 3px;"
          @click="deleteAttribute(index)" />
      </div>
    </div>
  </div>
</template>

<script>
  import { debounce } from 'lodash';
  import { sleep } from '@/common/util';
  import Attribute from '@/model/attribute';
  import BkUserSelector from '@blueking/user-selector';

  const ATTRIBUTE_ITEM = {
    id: '',
    name: '',
    values: []
  };

  const LOADING_ITEM = {
    id: '',
    display_name: ''
  };
    
  export default {
    components: {
      BkUserSelector
    },
    props: {
      list: {
        type: Array,
        default: () => []
      },
      value: {
        type: Array,
        default: () => []
      },
      // 查询参数
      params: {
        type: Object,
        default: () => {
          return {};
        }
      },
      mode: {
        type: String,
        default: 'normal'
      },
      limitValue: {
        type: Array,
        default: () => []
      }
    },
    data () {
      return {
        userApi: window.BK_USER_API,
        attrValues: [],
        curOperateData: {},
        pagination: {
          limit: 10,
          current: 1,
          totalPage: 0
        },
        attrValueListMap: {},
        isDisabledMode: false,
        curToggleItem: '',
        curKeyWord: '',
        curSelectDom: null
      };
    },
    computed: {
      isShowAction () {
        return payload => {
          if (this.isDisabledMode) {
            return false;
          }
          return !payload.disabled;
        };
      },
      isMemberSelector () {
        return (payload) => {
          return ['bk_cmdb'].includes(this.params.system_id) && ['operator', 'bk_bak_operator'].includes(payload.id);
        };
      },
      formatDisabled () {
        return (payload) => {
          return payload.disabled || !payload.id;
        };
      },
      formatMemberValue () {
        return (payload) => {
          const { values } = payload;
          if (values && values.length > 0) {
            return values.map((v) => v.id);
          }
          return [];
        };
      }
    },
    watch: {
      value: {
        handler (val) {
          if (val.length < 1) {
            this.attrValues = [new Attribute(ATTRIBUTE_ITEM)];
            return;
          }
          this.attrValues = val;
          const flag = Object.keys(this.attrValueListMap).length > 0;
          this.attrValues.forEach(async item => {
            if (!flag && item.id) {
              await this.fetchValue(item);
            }
          });
        },
        immediate: true
      },
      limitValue: {
        handler (val) {
          if (val.length > 0) {
            this.isDisabledMode = true;
            this.pagination.limit = 10000;
            let tempArr = [];
            val.map(item => {
              const tempList = item.values.map(v => {
                return {
                  id: v.id,
                  display_name: v.name
                };
              });
              this.$set(this.attrValueListMap, item.id, tempList);
            });
            if (this.value.length < 1) {
              this.attrValues = val.map(item => {
                const { id, name } = item;
                return new Attribute({ id, name, selecteds: [], values: [] });
              });
              tempArr = this.attrValues;
            } else {
              const differenceValue = val.filter(item => !this.value.map(v => v.id).includes(item.id));
              if (differenceValue.length > 0) {
                const tempValues = differenceValue.map(item => {
                  const { id, name } = item;
                  return new Attribute({ id, name, selecteds: [], values: [] });
                });
                tempArr = tempValues;
                this.attrValues.push(...tempValues);
              }
            }
            const flag = Object.keys(this.attrValueListMap).length > 0;
            tempArr.forEach(async item => {
              if (!flag && item.id) {
                await this.fetchValue(item);
              }
            });
          }
        },
        immediate: true
      },
      list: {
        handler (val) {
          if (val.length > 0) {
            val.forEach(item => {
              if (!this.attrValueListMap.hasOwnProperty(item.id)) {
                this.$set(this.attrValueListMap, item.id, []);
              }
            });
          }
        },
        immediate: true
      }
    },
    methods: {
      handleMemberChange (payload, row) {
        this.$set(row, 'selecteds', payload);
        if (!payload.length) {
          row.values = [];
          this.trigger();
          return;
        }
        const tempValues = [];
        payload.forEach((item) => {
          tempValues.push({
            id: item,
            name: item
          });
        });
        row.values = [...tempValues];
        this.trigger();
      },

      handleClear (value, payload) {
        payload.values = [];
        this.trigger();
      },

      handleAttrValueSelected (value, options, payload) {
        if (value.length < 1) {
          payload.values = [];
          this.trigger();
          return;
        }
        const tempValues = [];
        value.forEach((item, index) => {
          const attrData = options[index];
          tempValues.push({
            id: item,
            name: attrData.name
          });
        });
        payload.values = [...tempValues];
        this.trigger();
      },
            
      async fetchValue (item) {
        item.loading = true;
        try {
          const res = await this.$store.dispatch('permApply/getResourceAttrValues', {
            ...this.params,
            limit: this.pagination.limit,
            offset: this.pagination.limit * (this.pagination.current - 1),
            attribute: item.id,
            keyword: ''
          });
          this.pagination.totalPage = Math.ceil(res.data.count / this.pagination.limit);
          if (this.pagination.totalPage > 1) {
            res.data.results.push(LOADING_ITEM);
          }
          const results = (() => {
            const limitItem = this.limitValue.find(v => v.id === item.id);
            if (this.isDisabledMode && limitItem) {
              return res.data.results.filter(v => limitItem.selecteds.includes(v.id));
            }
            return res.data.results;
          })();
          this.$set(this.attrValueListMap, item.id, results);
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          item.loading = false;
        }
      },

      addAttribute () {
        this.attrValues.push(new Attribute(ATTRIBUTE_ITEM));
        this.trigger();
      },

      deleteAttribute (index) {
        if (this.attrValues.length === 1) {
          return;
        }
        this.attrValues.splice(index, 1);
        this.trigger();
      },

      handleAttributeSelected (newVal, option, payload) {
        payload.values = [];
        payload.selecteds = [];
        const curAttr = this.list.find(item => item.id === newVal);
        if (curAttr) {
          payload.name = curAttr.display_name || '';
        }
        if (this.attrValueListMap[payload.id] && this.attrValueListMap[payload.id].length < 1) {
          this.resetPagination(payload, '', true, false);
        }
      },

      async handleAttrValueToggle (val, index, payload) {
        if (this.isDisabledMode) {
          return;
        }
        this.curSelectDom = this.$refs[`${payload.id}&${index}&valueRef`][0];
        const curOptionDom = this.curSelectDom.$refs.optionList;
        curOptionDom.addEventListener('scroll', this.handleScroll);
        if (val) {
          // 记录当前操作的属性值数据
          this.curOperateData = payload;
          if ((this.curToggleItem && `${payload.id}&${index}&valueRef` !== this.curToggleItem) || !this.curKeyWord) {
            this.curSelectDom.searchLoading = false;
            this.resetPagination(payload, '', false, false);
          }
          this.curToggleItem = `${payload.id}&${index}&valueRef`;
        } else {
          this.curSelectDom = null;
          this.curOperateData = {};
          curOptionDom.removeEventListener('scroll', this.handleScroll);
        }
        this.pagination = Object.assign(this.pagination, { current: 1, limit: 10, totalPage: 0 });
        await this.fetchResourceAttrValues(payload);
      },

      async handleScroll (event) {
        if (this.pagination.current > this.pagination.totalPage) {
          // 删除loading项
          // 这里不能shift, 否则会存在滚动条往上滚动的时候，会删掉之前的数据
          // this.attrValueListMap[this.curOperateData.id].shift();
          return;
        }
        if (event.target.scrollTop + event.target.offsetHeight >= event.target.scrollHeight - 1) {
          ++this.pagination.current;
          if (this.pagination.current <= this.pagination.totalPage) {
            await this.fetchResourceAttrValues(this.curOperateData, this.curKeyWord, false, true);
            event.target.scrollTo(0, event.target.scrollTop - 10);
          }
        }
      },

      handleRemoteValue (value) {
        if (this.curSelectDom) {
          this.curSelectDom.searchLoading = false;
        }
        this.handleDebounceSearch(value);
      },

      handleDebounceSearch: debounce(function (value) {
        this.curKeyWord = value;
        if (this.curOperateData.id) {
          // 删除loading项
          this.attrValueListMap[this.curOperateData.id].shift();
          this.curSelectDom.searchLoading = true;
          this.resetPagination(this.curOperateData, value, false, false);
        }
      }, 800),

      async fetchResourceAttrValues (payload, keyword = '', isLoading = true, isScrollRemote = false) {
        payload.loading = isLoading && !isScrollRemote;
        payload.isScrollRemote = isScrollRemote;
        const { limit, current } = this.pagination;
        try {
          const res = await this.$store.dispatch('permApply/getResourceAttrValues', {
            ...this.params,
            limit: limit,
            offset: limit * (current - 1),
            attribute: payload.id,
            keyword
          });
          if (isScrollRemote) {
            const len = this.attrValueListMap[payload.id].length;
            this.attrValueListMap[payload.id].splice(len - 1, 0, ...res.data.results);
          } else {
            this.pagination.totalPage = Math.ceil(res.data.count / this.pagination.limit);
            if (this.pagination.totalPage > 1) {
              res.data.results.push(LOADING_ITEM);
            } else {
              res.data.results = res.data.results.filter((item) => item.id !== '');
            }
            this.attrValueListMap[payload.id] = [...res.data.results || []];
          }
        } catch (e) {
          console.error(e);
          this.messageAdvancedError(e);
        } finally {
          payload.loading = false;
          if (this.curSelectDom) {
            this.curSelectDom.searchLoading = false;
          }
          sleep(300).then(() => {
            payload.isScrollRemote = false;
          });
        }
      },

      async resetPagination (payload, keyword = '', isLoading = true, isScrollRemote = false) {
        this.pagination = Object.assign({
          limit: 10,
          current: 1,
          totalPage: 0
        });
        await this.fetchResourceAttrValues(payload, keyword, isLoading, isScrollRemote);
      },

      trigger () {
        this.$emit('on-change', this.attrValues);
      }
    }
  };
</script>

<style lang="postcss" scoped>
@import '@/css/mixins/attribute.css';
</style>
