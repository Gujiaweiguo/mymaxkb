<template>
  <el-form
    @submit.prevent
    :model="localModelValue"
    label-position="top"
    require-asterisk-position="right"
    label-width="auto"
    hide-required-asterisk
    ref="toolParameterFormRef"
  >
    <template v-for="f in input_field_list" :key="f.field">
      <el-form-item
        v-if="localModelValue[f.field]"
        :label="$t('workflow.nodes.startNode.question')"
        :prop="`${f.field}.value`"
        :rules="{
          message: $t('common.inputPlaceholder'),
          trigger: 'blur',
          required: f.required,
        }"
      >
        <template #label>
          <div class="flex-between">
            <div>
              {{ f.label.value }}
              <span class="color-danger" v-if="f.required">*</span>
            </div>
            <el-select
              :teleported="false"
              v-if="
                localModelValue[f.field] &&
                trigger.trigger_type === 'EVENT' &&
                trigger.trigger_setting.body.length
              "
              :model-value="localModelValue[f.field].source"
              @update:model-value="(val) => updateFieldValue(f.field, 'source', val)"
              size="small"
              style="width: 85px"
            >
              <el-option :label="$t('chat.quote')" value="reference" />
              <el-option :label="$t('common.custom')" value="custom" />
            </el-select>
          </div>
        </template>

        <el-cascader
          v-if="localModelValue[f.field].source === 'reference'"
          :model-value="localModelValue[f.field].value"
          @update:model-value="(val) => updateFieldValue(f.field, 'value', val)"
          :options="options"
          :placeholder="$t('common.selectPlaceholder')"
          :props="props"
          style="width: 100%"
        />
        <el-input
          v-else
          :model-value="localModelValue[f.field].value"
          @update:model-value="(val) => updateFieldValue(f.field, 'value', val)"
          :placeholder="$t('common.inputPlaceholder')"
        />
      </el-form-item>
    </template>
  </el-form>
</template>
<script setup lang="ts">
import { computed, ref, watch, reactive } from 'vue'
import { type FormInstance } from 'element-plus'
const toolParameterFormRef = ref<FormInstance>()
const props = defineProps<{ tool?: any; modelValue: any; trigger: any }>()
const emit = defineEmits(['update:modelValue'])

const localModelValue = reactive({ ...props.modelValue })

watch(
  () => props.modelValue,
  (newVal) => {
    Object.assign(localModelValue, newVal)
  },
  { deep: true }
)

function updateFieldValue(field: string, key: string, value: any) {
  if (!localModelValue[field]) {
    localModelValue[field] = {}
  }
  localModelValue[field][key] = value
  emit('update:modelValue', { ...localModelValue })
}

const showSource = computed(() => {
  return props.trigger.trigger_type === 'EVENT' && props.trigger.trigger_setting.body.length > 0
})

watch(
  () => showSource.value,
  () => {
    if (!showSource.value) {
      const parameter: any = {}
      input_field_list.value.forEach((f) => {
        if (props.modelValue[f.field]) {
          parameter[f.field] = {
            ...props.modelValue[f.field],
            source: 'custom',
          }
        } else {
          parameter[f.field] = { source: 'custom', value: f.default_value }
        }
      })
      emit('update:modelValue', { ...parameter })
    }
  },
)
const options = computed(() => {
  if (props.trigger.trigger_type === 'EVENT') {
    const body = props.trigger.trigger_setting.body
    if (body) {
      return [
        {
          label: 'body',
          value: 'body',
          children: body.map((item: any) => ({ label: item.field, value: item.field })),
        },
      ]
    }
    return []
  } else {
  }
  return []
})

const input_field_list = computed(() => {
  const result: Array<any> = []
  if (props.tool && props.tool.input_field_list) {
    props.tool.input_field_list.forEach((item: any) => {
      result.push({
        field: item.name,
        required: item.is_required,
        label: { value: item.name },
      })
    })
  }
  return result
})

const init_parameters = () => {
  const parameter: any = {}
  input_field_list.value.forEach((f) => {
    parameter[f.field] = { source: 'custom', value: f.default_value }
  })
  emit('update:modelValue', { ...parameter, ...props.modelValue })
}

init_parameters()
const validate = () => {
  return toolParameterFormRef.value?.validate()
}
defineExpose({ validate })
</script>
<style lang="scss"></style>
