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
  <div class="container p-1">
    <!-- Active surveys -->
    <b-alert
        show
        variant="info"
        class="mb-3"
        v-for="(survey, index) in surveys"
        :key="`survey ${index}`">
      <p class="m-0">
        <a :href="survey.survey_link">
          {{ survey.survey_introduction_text }}
        </a>
      </p>
    </b-alert>

    <b-card no-body class="p-3 mb-4">
      <h1>Aquifer Search</h1>

      <div class="pb-2">
        <b-button
          id="aquifers-add"
          v-on:click="navigateToNew"
          v-if="userRoles.aquifers.edit"
          variant="primary">Add new Aquifer</b-button>
      </div>

      <b-alert
        :show="noSearchCriteriaError"
        variant="danger">
        <i class="fa fa-exclamation-circle"/>&nbsp;&nbsp;At least one search field is required
      </b-alert>

      <b-form
        v-on:submit.prevent="triggerSearch"
        v-on:reset="triggerReset">
        <b-form-row>
          <b-col cols="12" md="4">
            <h5>Search by aquifer name or number</h5>
            <b-form-group label="(leave blank to see all aquifers)">
              <b-form-input
                type="text"
                id="aquifers-search-field"
                v-model="search"/>
            </b-form-group>
            <b-form-checkbox-group
              stacked
              v-model="sections"
              :options="aquifer_resource_sections"
            />

          </b-col>
        </b-form-row>
        <b-form-row>
          <b-col>
            <b-form-group class="aquifer-search-actions">
              <b-button variant="primary" type="submit" id="aquifers-search">Search</b-button>
              <b-button variant="default" type="reset">Reset</b-button>
            </b-form-group>
          </b-col>
        </b-form-row>
      </b-form>

      <b-table
        id="aquifers-results"
        class="mt-3"
        :fields="aquiferListFields"
        :items="aquiferList"
        :show-empty="emptyResults"
        :sort-by.sync="sortBy"
        :sort-desc.sync="sortDesc"
        empty-text="No aquifers could be found"
        no-local-sorting
        striped
        v-if="aquiferList">
        <template slot="aquifer_id" slot-scope="data">
          <router-link :to="{ name: 'aquifers-view', params: {id: data.value} }">{{data.value}}</router-link>
        </template>
        <template slot="material" slot-scope="row">
          {{row.item.material_description}}
        </template>
        <template slot="subtype" slot-scope="row">
          {{row.item.subtype_description}}
        </template>
        <template slot="vulnerability" slot-scope="row">
          {{row.item.vulnerability_description}}
        </template>
        <template slot="vulnerability" slot-scope="row">
          {{row.item.vulnerability_description}}
        </template>
        <template slot="productivity" slot-scope="row">
          {{row.item.productivity_description}}
        </template>
        <template slot="demand" slot-scope="row">
          {{row.item.demand_description}}
        </template>
      </b-table>

      <b-container v-if="aquiferList && !emptyResults">
        <b-row>
          <b-col>
            Showing {{ displayOffset }} to {{ displayPageLength }} of {{ response.count }}
          </b-col>
          <b-col v-if="displayPagination">
            <b-pagination :total-rows="response.count" :per-page="limit" v-model="currentPage" />
          </b-col>
        </b-row>
      </b-container>

    </b-card>
  </div>
</template>

<style>
table.b-table > thead > tr > th.sorting::before,
table.b-table > tfoot > tr > th.sorting::before {
  display: none !important;
}
table.b-table > thead > tr > th.sorting::after,
table.b-table > tfoot > tr > th.sorting::after {
  content: "\f0dc" !important;
  font-family: "FontAwesome";
  opacity: 1 !important;
}
ul.pagination {
  justify-content: end;
}

.aquifer-search-actions {
  margin-top: 1em
}
</style>

<script>
import querystring from 'querystring'
import ApiService from '@/common/services/ApiService.js'
import { mapGetters } from 'vuex'
const LIMIT = 30
const DEFAULT_ORDERING_STRING = 'aquifer_id'
function orderingQueryStringToData (str) {
  str = str || DEFAULT_ORDERING_STRING
  return {
    sortDesc: str.charAt(0) === '-',
    sortBy: str.replace(/^-/, '')
  }
}
export default {
  data () {
    let query = this.$route.query || {}
    return {
      ...orderingQueryStringToData(query.ordering),
      search: query.search,
      aquifer_search: query.aquifer_search,
      limit: LIMIT,
      currentPage: query.offset && (query.offset / LIMIT + 1),
      filterParams: Object.assign({}, query),
      response: {},
      aquiferListFields: [
        { key: 'aquifer_id', label: 'Aquifer number', sortable: true },
        { key: 'aquifer_name', label: 'Aquifer name', sortable: true },
        { key: 'location_description', label: 'Descriptive location', sortable: true },
        { key: 'material', label: 'Material', sortable: true },
        { key: 'litho_stratographic_unit', label: 'Litho stratigraphic unit', sortable: true },
        { key: 'subtype', label: 'Subtype', sortable: true },
        { key: 'vulnerability', label: 'Vulnerability', sortable: true },
        { key: 'area', label: 'Size-km²', sortable: true },
        { key: 'productivity', label: 'Productivity', sortable: true },
        { key: 'demand', label: 'Demand', sortable: true },
        { key: 'mapping_year', label: 'Year of mapping', sortable: true }
      ],
      surveys: [],
      noSearchCriteriaError: false,
      aquifer_resource_sections: [],
      sections: query.resources__section__code ? query.resources__section__code.split(',') : []
    }
  },
  computed: {
    offset () { return parseInt(this.$route.query.offset, 10) || 0 },
    displayOffset () { return this.offset + 1 },
    displayPageLength () {
      if (!this.response) {
        return undefined
      }
      return this.offset + this.response.results.length
    },
    aquiferList () { return this.response && this.response.results },
    displayPagination () { return this.aquiferList && (this.response.next || this.response.previous) },
    emptyResults () { return this.response && this.response.count === 0 },
    query () { return this.$route.query },
    ...mapGetters(['userRoles'])
  },
  methods: {
    navigateToNew () {
      this.$router.push({ name: 'new' })
    },
    fetchResults () {
      // trigger the Google Analytics search event
      this.triggerAnalyticsSearchEvent(this.query)
      ApiService.query('aquifers', this.query)
        .then((response) => {
          this.response = response.data
          this.scrollToTableTop()
        })
    },
    fetchResourceSections () {
      ApiService.query('aquifers/sections').then((response) => {
        this.aquifer_resource_sections = response.data.results.map(function (section) {
          return {
            text: section.name,
            value: section.code
          }
        })
      })
    },
    scrollToTableTop () {
      this.$SmoothScroll(this.$el, 100)
    },
    triggerPagination () {
      const i = (this.currentPage || 1) - 1
      delete this.filterParams.limit
      delete this.filterParams.offset
      if (i > 0) {
        this.filterParams.limit = LIMIT
        this.filterParams.offset = i * LIMIT
      }
      this.updateQueryParams()
    },
    triggerReset () {
      this.response = {}
      this.filterParams = {}
      this.search = ''
      this.aquifer_id = ''
      this.sections = []
      this.currentPage = 0
      this.noSearchCriteriaError = false
      this.updateQueryParams()
    },
    triggerSearch () {
      delete this.filterParams.aquifer_id
      delete this.filterParams.search
      delete this.filterParams.resources__section__code
      if (this.search) {
        this.filterParams.search = this.search
      }
      if (this.sections) {
        this.filterParams.resources__section__code = this.sections.join(',')
      }
      this.updateQueryParams()
    },
    triggerSort () {
      delete this.filterParams.ordering
      let ordering = `${this.sortDesc ? '-' : ''}${this.sortBy}`
      if (ordering !== DEFAULT_ORDERING_STRING) {
        this.filterParams.ordering = ordering
      }
      this.updateQueryParams()
    },
    updateQueryParams () {
      this.$router.replace({query: this.filterParams})
    },
    triggerAnalyticsSearchEvent (params) {
      // trigger the search event, sending along the search params as a string
      if (window.ga) {
        window.ga('send', {
          hitType: 'event',
          eventCategory: 'Button',
          eventAction: 'AquiferSearch',
          eventLabel: querystring.stringify(params)
        })
      }
    }
  },
  created () {
    // Fetch current surveys and add 'aquifer' surveys (if any) to this.surveys to be displayed
    ApiService.query('surveys').then((response) => {
      if (response.data) {
        response.data.forEach((survey) => {
          if (survey.survey_page === 'a') {
            this.surveys.push(survey)
          }
        })
      }
    }).catch((e) => {
      console.error(e)
    })
    this.fetchResourceSections()
  },
  watch: {
    query () { this.fetchResults() },
    currentPage () { this.triggerPagination() },
    sortDesc () { this.triggerSort() },
    sortBy () { this.triggerSort() }
  }
}
</script>
