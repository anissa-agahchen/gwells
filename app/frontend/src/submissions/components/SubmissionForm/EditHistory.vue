/*
Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
*/
<template>
  <fieldset :id="id" class="mt-5">
    <b-row>
      <b-col cols="12" lg="6">
        <legend :id="id">Change History
        </legend>
      </b-col>
    </b-row>
    <b-row>
      <b-col cols="12">
        <change-history :id="$route.params.id" resource="wells" :events="events" ref="wellHistory"/>
      </b-col>
    </b-row>
  </fieldset>
</template>

<script>
import Vue from 'vue'
import { mapGetters } from 'vuex'
import ChangeHistory from '@/common/components/ChangeHistory.vue'

export default {
  name: 'StaffEditHistory',
  props: {
    id: {
      type: String,
      isInput: false
    },
    events: {
      type: Vue
    }
  },
  components: {
    ChangeHistory
  },
  data () {
    return {}
  },
  computed: {
    ...mapGetters(['codes'])
  },
  created () {
    if (this.events) {
      this.events.$on('well-edited', () => {
        this.$refs.wellHistory.update()
      })
    }
  }
}
</script>

<style>

</style>
