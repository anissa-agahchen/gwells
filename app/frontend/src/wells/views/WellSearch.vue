<template>
  <b-card class="container p-1">
    <h1 class="card-title" id="wellSearchTitle">Well Search</h1>
    <div>
      <div>
        <p>
          Not all groundwater wells are registered with the province, as registration was voluntary until February 29, 2016. Data quality issues may impact search results.
        </p>
        <p>
          Search by one of the fields below, or zoom to a location on the map and select the "Search Wells in this Area" button.
        </p>
      </div>
    </div>
    <b-row class="mt-4">
      <b-col cols="12" lg="6" xl="5">
        <b-form @submit.prevent="handleSearchSubmit({ trigger: 'search' })" @reset.prevent="handleReset()">
          <b-card no-body border-variant="dark" class="mb-1">
            <b-tabs card v-model="tabIndex">
              <b-tab title="Basic Search">
                <div class="card-text">
                  <b-row>
                    <b-col>
                      <b-form-group>
                        <form-input id="id_search" group-class="font-weight-bold" v-model="searchParams.search">
                          <label>
                            Search by well tag or ID plate number, street address, city or owner name
                            <b-badge pill variant="primary" id="basicSearchInfo" tabindex="0"><i class="fa fa-question fa-lg"></i></b-badge>
                            <b-popover target="basicSearchInfo" triggers="hover focus" content="Enter the well electronic filing number or physical identification plate number, or the street address, city or well owner name."></b-popover>
                          </label>
                        </form-input>
                      </b-form-group>
                    </b-col>
                  </b-row>
                  <b-row class="my-3">
                    <b-col>
                      <b-btn variant="primary" type="submit">Search</b-btn>
                      <b-btn variant="dark" type="reset" class="mx-2">Reset</b-btn>
                    </b-col>
                  </b-row>
                  <b-row>
                    <b-col>
                      <well-exports/>
                    </b-col>
                  </b-row>
                  <b-row>
                    <b-col>
                      <p>For additional search options, try:</p>
                      <ul>
                          <li><a href="http://maps.gov.bc.ca/ess/hm/wrbc/" id="BCWRAtlas">B.C. Water Resource Atlas</a></li>
                          <li><a href="http://maps.gov.bc.ca/ess/hm/imap4m/" id="iMapBC">iMapBC</a></li>
                      </ul>
                    </b-col>
                  </b-row>
                </div>
              </b-tab>
              <b-tab title="Advanced Search">
                <div class="card-text">
                  <div v-for="section in defaultFilters" :key="section.header">
                    <b-row class="mt-1">
                      <b-col>
                        <h3>{{ section.header }}</h3>
                      </b-col>
                    </b-row>
                    <template v-for="field in section.fields">
                      <template v-if="field.authenticated ? userRoles.wells.view : true">
                        <search-form-radio
                          v-if="field.type === 'radio'"
                          :key="field.id"
                          :id="`${field.id}Filter`"
                          :label="field.label"
                          label-cols="5"
                          v-model="searchParams[field.param]"
                          :options="field.options" />
                        <search-form-range
                          v-else-if="field.type === 'range'"
                          :key="field.id"
                          type="number"
                          label-cols="3"
                          :id="`${field.id}Filter`"
                          :label="field.label"
                          :errors="searchErrors[field.param]"
                          :step="field.step ? field.step : 'any'"
                          :min-value="searchParams[`${field.param}_min`]"
                          v-on:start-input="searchParams[`${field.param}_min`] = $event"
                          :max-value="searchParams[`${field.param}_max`]"
                          v-on:end-input="searchParams[`${field.param}_max`] = $event"/>
                        <search-form-range
                          v-else-if="field.type === 'dateRange'"
                          :key="field.id"
                          type="date"
                          label-cols="3"
                          :id="`${field.id}Filter`"
                          :label="field.label"
                          placeholder="YYYY/MM/DD"
                          :errors="searchErrors[field.param]"
                          :min-value="searchParams[`${field.param}_after`]"
                          v-on:start-input="searchParams[`${field.param}_after`] = $event"
                          :max-value="searchParams[`${field.param}_before`]"
                          v-on:end-input="searchParams[`${field.param}_before`] = $event"/>
                        <search-form-select
                          v-else-if="field.type === 'select'"
                          :key="field.id"
                          label-cols="6"
                          :id="`${field.id}Filter`"
                          :label="field.label"
                          placeholder="----------"
                          :errors="searchErrors[field.param]"
                          v-model="searchParams[field.param]"
                          :options="filterSelectOptions[field.id]"
                          :value-field="field.valueField"
                          :text-field="field.textField" />
                        <search-form-input
                          v-else
                          :key="field.id"
                          :type="field.type"
                          label-cols="6"
                          :id="`${field.id}Filter`"
                          :label="field.label"
                          :errors="searchErrors[field.param]"
                          v-model="searchParams[field.param]"/>
                      </template>
                    </template>
                  </div>
                  <b-row>
                    <b-col class="my-3">
                      <b-btn variant="primary" type="submit">Search</b-btn>
                      <b-btn variant="dark" type="reset" class="mx-2">Reset</b-btn>
                    </b-col>
                  </b-row>
                  <b-row class="mt-1">
                    <b-col>
                      <h3>Additional Fields</h3>
                    </b-col>
                  </b-row>
                  <b-form-row v-for="field in selectedFilters" :key="field.id">
                    <b-col>
                      <search-form-radio
                        v-if="field.type === 'radio'"
                        :id="`${field.id}Filter`"
                        :label="field.label"
                        v-model="searchParams[field.param]"
                        :options="field.options" />
                      <search-form-range
                        v-else-if="field.type === 'range'"
                        type="number"
                        :id="`${field.id}Filter`"
                        :label="field.label"
                        :errors="searchErrors[field.param]"
                        :step="field.step ? field.step : 'any'"
                        :min-value="searchParams[`${field.param}_min`]"
                        v-on:start-input="searchParams[`${field.param}_min`] = $event"
                        :max-value="searchParams[`${field.param}_max`]"
                        v-on:end-input="searchParams[`${field.param}_max`] = $event"/>
                      <search-form-boolean-or-range
                        v-else-if="field.type === 'booleanOrRange'"
                        type="number"
                        :id="`${field.id}Filter`"
                        :label="field.label"
                        boolean-label="Any value"
                        :errors="searchErrors[field.param]"
                        :boolean-errors="searchErrors[`${field.param}_any_value`]"
                        :step="field.step ? field.step : 'any'"
                        :min-value="searchParams[`${field.param}_min`]"
                        v-on:start-input="searchParams[`${field.param}_min`] = $event"
                        :max-value="searchParams[`${field.param}_max`]"
                        v-on:end-input="searchParams[`${field.param}_max`] = $event"
                        :boolean-value="searchParams[`${field.param}_has_value`]"
                        v-on:boolean-input="searchParams[`${field.param}_has_value`] = $event"/>
                      <search-form-boolean-or-text
                        v-else-if="field.type === 'booleanOrText'"
                        :type="text"
                        :id="`${field.id}Filter`"
                        :label="field.label"
                        boolean-label="Any value"
                        :errors="searchErrors[field.param]"
                        v-model="searchParams[field.param]"
                        :boolean-value="searchParams[`${field.param}_has_value`]"
                        v-on:boolean-input="searchParams[`${field.param}_has_value`] = $event"/>
                      <search-form-range
                        v-else-if="field.type === 'dateRange'"
                        type="date"
                        :id="`${field.id}Filter`"
                        :label="field.label"
                        placeholder="YYYY/MM/DD"
                        :errors="searchErrors[field.param]"
                        :min-value="searchParams[`${field.param}_after`]"
                        v-on:start-input="searchParams[`${field.param}_after`] = $event"
                        :max-value="searchParams[`${field.param}_before`]"
                        v-on:end-input="searchParams[`${field.param}_before`] = $event"/>
                      <search-form-select
                        v-else-if="field.type === 'select'"
                        :id="`${field.id}Filter`"
                        :label="field.label"
                        placeholder="----------"
                        :errors="searchErrors[field.param]"
                        v-model="searchParams[field.param]"
                        :options="filterSelectOptions[field.id]"
                        :value-field="field.valueField"
                        :text-field="field.textField" />
                      <search-form-input
                        v-else-if="field.type === 'number' || field.type === 'text'"
                        :type="field.type"
                        :id="`${field.id}Filter`"
                        :label="field.label"
                        :errors="searchErrors[field.param]"
                        v-model="searchParams[field.param]"/>
                    </b-col>
                    <b-col cols="1">
                      <b-button-close @click="removeSelectedFilter(field.id)" class="pt-1">&times;</b-button-close>
                    </b-col>
                  </b-form-row>
                  <b-row>
                    <b-col sm="9" class="mb-1">
                      <b-form-select id="additionalFilterInput" v-model="selectedFilter">
                        <option :value="null">Select a field to search on</option>
                        <template v-for="section in additionalFilters">
                          <optgroup v-if="section.authenticated ? userRoles.wells.view : true" :key="section.header" :label="section.header">
                            <template v-for="field in section.fields">
                              <option v-if="field.authenticated ? userRoles.wells.view : true" :key="field.id" :value="field" :disabled="selectedFilterIds.includes(field.id)">{{ field.label }}</option>
                            </template>
                          </optgroup>
                        </template>
                      </b-form-select>
                    </b-col>
                    <b-col sm="3" class="mb-1">
                      <b-button block variant="primary" @click="selectFilter" :disabled="selectedFilter === null">Add Field</b-button>
                    </b-col>
                  </b-row>
                </div>
              </b-tab>
            </b-tabs>
          </b-card>
        </b-form>
      </b-col>
      <b-col>
        <search-map
            :latitude="latitude"
            :longitude="longitude"
            :locations="locations"
            :zoomToMarker="zoomToResults"
            v-on:coordinate="handleMapCoordinate"
            ref="searchMap"
            @moved="handleMapMoveEnd"
            />
        <b-alert variant="info" class="mt-2" :show="!!mapError">{{ mapError }}</b-alert>
      </b-col>
    </b-row>
    <b-row class="my-5" v-show="!isInitialSearch">
      <b-col>
        <b-table
          id="well-search-table"
          :items="wellSearch"
          :isBusy="!!pendingSearch"
          :fields="wellSearchColumns"
          :per-page="perPage"
          :current-page="currentPage"
        >
        <template slot="well_tag_number" slot-scope="data">
          <router-link :to="{ name: 'wells-detail', params: {id: data.value} }">{{data.value}}</router-link>
        </template>
        </b-table>
        <b-row>
          <b-col>
            <div class="my-3" v-if="numberOfRecords > 0">Showing {{ currentRecordsCountStart }} to {{ currentRecordsCountEnd }} of {{ numberOfRecords }} {{ numberOfRecords === 1 ? 'record' : 'records'}}.</div>
          </b-col>
        </b-row>
        <b-pagination v-show="numberOfRecords > perPage" class="mt-3" :disabled="!!pendingSearch" size="md" :total-rows="numberOfRecords" v-model="currentPage" :per-page="perPage" @input="wellSearch()">
        </b-pagination>
      </b-col>
    </b-row>
    <b-row v-if="!isInitialSearch">
      <b-col>
        <p>
          Can’t find the well you are looking for? Try your search again using a different set of criteria. If you still need more assistance, Contact <a href="https://portal.nrs.gov.bc.ca/web/client/contact">FrontCounterBC</a>.
        </p>
        <p>
          <a href="http://www.frontcounterbc.gov.bc.ca/Start/surface-water/" @click="handleOutboundLinkClicks('www.frontcounterbc.gov.bc.ca/Start/surface-water/')">
              Learn about and submit water license applications
          </a>  with FrontCounterBC.
        </p>
      </b-col>
    </b-row>
  </b-card>
</template>

<script>
import axios from 'axios'
import querystring from 'querystring'
import debounce from 'lodash.debounce'

import { mapGetters } from 'vuex'
import ApiService from '@/common/services/ApiService.js'
import {FETCH_CODES} from '@/submissions/store/actions.types.js'
import {FETCH_DRILLER_NAMES, FETCH_ORGANIZATION_NAMES} from '@/wells/store/actions.types.js'
import SearchFormInput from '@/wells/components/SearchFormInput.vue'
import SearchFormRadio from '@/wells/components/SearchFormRadio.vue'
import SearchFormRange from '@/wells/components/SearchFormRange.vue'
import SearchFormSelect from '@/wells/components/SearchFormSelect.vue'
import SearchFormBooleanOrRange from '@/wells/components/SearchFormBooleanOrRange.vue'
import SearchFormBooleanOrText from '@/wells/components/SearchFormBooleanOrText.vue'
import SearchMap from '@/wells/components/SearchMap.vue'
import Exports from '@/wells/components/Exports.vue'
import searchFields from '@/wells/searchFields.js'

const triggers = {
  // the map trigger indicates a search was triggered by moving the map.
  // this should update the search results table to only show visible wells
  MAP: 'map',

  // the QUERY trigger means the search was triggered by a querystring in the URL
  // e.g. the user bookmarked a search or shared a link.
  QUERY: 'query',

  // the search trigger means the basic or advanced search form was used to search for wells.
  SEARCH: 'search',

  // the 'none' trigger indicates a search hasn't been explicitly requested by user input yet,
  // and the search will not run.
  NONE: null
}

export default {
  name: 'WellSearch',
  components: {
    'search-form-boolean-or-text': SearchFormBooleanOrText,
    'search-form-boolean-or-range': SearchFormBooleanOrRange,
    'search-form-input': SearchFormInput,
    'search-form-radio': SearchFormRadio,
    'search-form-range': SearchFormRange,
    'search-form-select': SearchFormSelect,
    'search-map': SearchMap,
    'well-exports': Exports
  },
  data () {
    return {
      pendingSearch: null,
      pendingMapSearch: null,
      scrolled: false,
      mapError: null,
      lastSearchTrigger: null,

      isBusy: false,
      isInitialSearch: true,
      tabIndex: 0,
      currentPage: 1,
      perPage: 10,
      numberOfRecords: 0,
      latitude: null,
      longitude: null,
      locations: [],
      mapBounds: {},
      selectedFilter: null,
      selectedFilters: [],

      wellSearchColumns: [
        { label: 'Well Tag', key: 'well_tag_number', sortable: true },
        { label: 'ID Plate', key: 'identification_plate_number', sortable: true },
        { label: 'Owner Name', key: 'owner_full_name', sortable: true },
        { label: 'Street Address', key: 'street_address', sortable: true },
        { label: 'Legal Lot', key: 'legal_lot', sortable: true },
        { label: 'Legal Plan', key: 'legal_plan', sortable: true },
        { label: 'Legal District Lot', key: 'legal_district_lot', sortable: true },
        { label: 'Land District', key: 'land_district', sortable: true },
        { label: 'Legal PID', key: 'legal_pid', sortable: true },
        { label: 'Diameter', key: 'diameter', sortable: true },
        { label: 'Finished Well Depth', key: 'finished_well_depth', sortable: true }
      ],

      tableData: [],

      // searchParams will be set by searchParamsReset()
      searchParams: {},
      searchErrors: {},

      // flag to indicate that the search should reset without a further API request
      searchShouldReset: false,

      // additional location search params
      mapSearchParams: {},
      defaultFilters: searchFields.default,
      additionalFilters: searchFields.optional
    }
  },
  computed: {
    ...mapGetters(['codes', 'drillerNames', 'organizationNames', 'userRoles']),
    selectedFilterIds () {
      return this.selectedFilters.map(filter => filter.id)
    },
    defaultFilterFields () {
      return this.defaultFilters.map(section => section.fields).reduce((a, b) => a.concat(b), [])
    },
    additionalFilterFields () {
      return this.additionalFilters.map(section => section.fields).reduce((a, b) => a.concat(b), [])
    },
    defaultSearchParams () {
      const params = {match_any: 'true'}
      // Populate params with empty values for selects
      const defaultSelectParams = this.defaultFilterFields.filter(filter => filter.type === 'select').map(filter => filter.param)
      defaultSelectParams.forEach((param) => {
        params[param] = ''
      })

      return params
    },
    landDistrictOptions () {
      if (this.codes.land_district_codes === undefined || (this.codes.land_district_codes && Object.entries(this.codes.land_district_codes).length === 0)) {
        return []
      }
      return this.codes.land_district_codes.map((district) => {
        return {
          value: district.land_district_code,
          text: `${district.land_district_code} - ${district.name}`
        }
      })
    },
    wellSubclassOptions () {
      if (!this.codes.well_classes) {
        return []
      }
      const options = []
      this.codes.well_classes.forEach((wellClass) => {
        wellClass.wellsubclasscode_set.forEach((wellSubclass) => {
          options.push({
            value: wellSubclass.well_subclass_guid,
            text: `${wellClass.description} - ${wellSubclass.description}`
          })
        })
      })

      return options
    },
    filterSelectOptions () {
      return {
        aquiferLithology: this.codes.aquifer_lithology_codes || [],
        coordinateAcquisitionCode: this.codes.coordinate_acquisition_codes || [],
        decommissionMethod: this.codes.decommission_methods || [],
        developmentMethods: this.codes.development_methods || [],
        drillingMethods: this.codes.drilling_methods || [],
        filterPackMaterial: this.codes.filter_pack_material || [],
        filterPackMaterialSize: this.codes.filter_pack_material_size || [],
        groundElevationMethod: this.codes.ground_elevation_methods || [],
        intendedWaterUse: this.codes.intended_water_uses || [],
        landDistrict: this.landDistrictOptions,
        licencedStatus: this.codes.licenced_status_codes || [],
        linerMaterial: this.codes.liner_material_codes || [],
        observationWellStatus: this.codes.observation_well_status || [],
        orgResponsible: this.organizationNames || [],
        ownerProvince: this.codes.province_codes || [],
        personResponsible: this.drillerNames || [],
        publicationStatus: this.codes.well_publication_status_codes || [],
        screenIntakeMethod: this.codes.screen_intake_methods || [],
        screenBottoms: this.codes.screen_bottoms || [],
        screenMaterial: this.codes.screen_materials || [],
        screenOpenings: this.codes.screen_openings || [],
        screenType: this.codes.screen_types || [],
        surfaceSealMaterial: this.codes.surface_seal_materials || [],
        surfaceSealMethod: this.codes.surface_seal_methods || [],
        waterQualityCharacteristics: this.codes.water_quality_characteristics || [],
        waterQualityColour: this.codes.water_quality_colours || [],
        wellClass: this.codes.well_classes || [],
        wellStatus: this.codes.well_status_codes || [],
        wellSubclass: this.wellSubclassOptions,
        yieldEstimationMethod: this.codes.yield_estimation_methods || []
      }
    },
    // currentRecordsCountStart is the starting record number in the table of wells
    // (e.g. the 1 in 'showing 1 to 10 of 25 records')
    currentRecordsCountStart () {
      return (this.currentPage - 1) * this.perPage + 1
    },
    // currentRecordsCountEnd is the last visible record number in the table of wells
    // (e.g. the 10 in 'showing 1 to 10 of 25 records')
    currentRecordsCountEnd () {
      return (this.currentPage - 1) * this.perPage + this.tableData.length
    },
    zoomToResults () {
      return this.lastSearchTrigger !== triggers.MAP
    }
  },
  methods: {
    /**
    * wellSearch searches for wells based on parameters in the querystring
    */
    wellSearch (ctx = {}) {
      const { perPage = this.perPage, currentPage = this.currentPage, trigger = this.lastSearchTrigger } = ctx

      // cancel previous search request and add a cancellation token for this request
      if (this.pendingSearch) {
        this.pendingSearch.cancel()
      }

      // if the searchShouldReset flag is true, stop the well search before making
      // any requests and return an empty array to the table.
      // we also stop here if the trigger has not been set; this is to avoid triggering
      // searches without user input.
      if (this.searchShouldReset || !trigger) {
        this.searchErrors = {}
        this.numberOfRecords = 0
        this.currentPage = 1
        this.searchShouldReset = false
        return []
      }

      // add a cancellation token to this request
      const CancelToken = axios.CancelToken
      const requestContext = CancelToken.source()
      this.pendingSearch = requestContext

      const params = {
        limit: perPage,
        offset: perPage * (currentPage - 1)
      }

      // if the table has been ordered, add an 'ordering' param to the API call
      if (ctx.sortBy) {
        params['ordering'] = `${ctx.sortDesc ? '-' : ''}${ctx.sortBy}`
      }

      // add other search parameters into the params object.
      // these will be urlencoded and the API will filter on these values.
      Object.assign(params, this.searchParams)

      // if triggering the search using the map, the search will be restricted to
      // the visible map bounds
      if (trigger === triggers.MAP) {
        Object.assign(params, this.mapBounds)
      }

      // send the analytic event when triggering search by the search button
      if (trigger === triggers.SEARCH) {
        this.triggerAnalyticsSearchEvent(params)
      }

      return ApiService.query('wells', params, { cancelToken: this.pendingSearch.token }).then((response) => {
        this.searchErrors = {}
        this.numberOfRecords = response.data.count
        this.tableData = response.data.results

        // the first search that happens when page loads doesn't need
        // to automatically scroll the page.  Only scroll when updating
        // the search results.
        if (!this.isInitialSearch && !this.scrolled) {
          this.$SmoothScroll(this.$el.querySelector('#map'))
        }
        // flag that the initial search that happens on page load
        // has already occurred.
        this.isInitialSearch = false

        return response.data.results || []
      }).catch((err) => {
        if (err.response && err.response.data) {
          this.searchErrors = err.response.data
        }

        return []
      }).finally(() => {
        this.pendingSearch = null
      })
    },
    handleScroll () {
      const pos = this.$el.querySelector('#map').scrollTop | 100
      this.scrolled = window.scrollY > 0.9 * pos
    },
    locationSearch (ctx = {}) {
      const { trigger = triggers.SEARCH } = ctx

      // cancel previous location search request and add a cancellation token for this request
      if (this.pendingMapSearch) {
        this.pendingMapSearch.cancel()
      }

      const CancelToken = axios.CancelToken
      const requestContext = CancelToken.source()
      this.pendingMapSearch = requestContext

      let params = Object.assign({}, this.searchParams)

      if (trigger === triggers.MAP) {
        Object.assign(params, this.mapBounds)
      }

      ApiService.query('wells/locations', params, { cancelToken: this.pendingMapSearch.token }).then((response) => {
        this.mapError = null
        this.locations = response.data.map((well) => {
          return [well.latitude, well.longitude, well.well_tag_number, well.identification_plate_number]
        })
      }).catch((e) => {
        if (e.response.data) {
          this.mapError = e.response.data.detail
        }
        this.locations = []
      }).finally(() => {
        this.pendingMapSearch = null
      })
    },
    debounceSearch: debounce(function () {
      this.handleSearchSubmit({ trigger: triggers.MAP })
    }, 500),
    handleMapMoveEnd () {
      this.setMapBounds()
      if (this.pendingMapSearch) {
        this.pendingSearch.cancel()
      }
      this.debounceSearch()
    },
    setMapBounds () {
      if (this.$refs.searchMap && this.$refs.searchMap.map) {
        const bounds = this.$refs.searchMap.map.getBounds()
        const sw = bounds.getSouthWest()
        const ne = bounds.getNorthEast()
        const boundBox = {
          sw_lat: sw.lat,
          sw_long: sw.lng,
          ne_lat: ne.lat,
          ne_long: ne.lng
        }
        this.mapBounds = boundBox
      }
    },
    resetMapBounds () {
      if (this.$refs.searchMap && this.$refs.searchMap.resetView) {
        this.$refs.searchMap.resetView()
        this.setMapBounds()
      }
    },
    handleSearchSubmit (options) {
      const { trigger = triggers.SEARCH } = options
      this.lastSearchTrigger = trigger

      this.cleanSearchParams()
      this.updateQueryParams()
      this.$root.$emit('bv::refresh::table', 'well-search-table')
      this.locationSearch(options)
    },
    handleReset () {
      this.resetMapBounds()
      this.searchParamsReset()
      this.tableData = []
      this.locations = []
      this.mapError = null
      this.searchShouldReset = true
      this.$root.$emit('bv::refresh::table', 'well-search-table')
    },
    searchParamsReset () {
      this.searchParams = {...this.defaultSearchParams}
      this.selectedFilters = []
      this.$nextTick(() => {
        this.$router.push({ query: null })
      })
    },
    initTabIndex () {
      const hash = this.$route.hash
      if (hash === '#advanced') {
        this.tabIndex = 1
      } else {
        this.tabIndex = 0
      }
      // add a watcher for tabIndex after setting the initial value
      this.$watch('tabIndex', function () {
        this.searchParamsReset()
      })
    },
    initSearchParams () {
      const query = this.$route.query
      // check if the page loads with a query (e.g. user bookmarked a search)
      // if so, set the search boxes to the query params
      if (Object.entries(query).length !== 0 && query.constructor === Object) {
        this.searchParams = Object.assign({...this.defaultSearchParams}, query)
      } else {
        this.searchParamsReset()
      }
    },
    initSelectedFilters () {
      const query = this.$route.query
      this.additionalFilterFields.filter((field) => {
        const fieldParams = this.getParamNames(field)
        return fieldParams.some(param => param in query)
      }).forEach(field => this.selectedFilters.push(field))
    },
    handleMapCoordinate (latln) {
      this.latitude = null
      this.longitude = null
      setTimeout(() => {
        this.latitude = latln.lat
        this.longitude = latln.lng
      }, 0)
    },
    handleOutboundLinkClicks (link) {
      if (window.ga) {
        window.ga('send', 'event', {
          eventCategory: 'Outbound Link',
          eventAction: 'click',
          eventLabel: link
        })
      }
    },
    triggerAnalyticsSearchEvent (params) {
      // trigger the search event, sending along the search params as a string
      if (window.ga) {
        window.ga('send', {
          hitType: 'event',
          eventCategory: 'Button',
          eventAction: 'WellSearch',
          eventLabel: querystring.stringify(params)
        })
      }
    },
    cleanSearchParams () {
      // Clear any null or empty string values, to keep URLs clean.
      Object.entries(this.searchParams).forEach(([key, value]) => {
        if (value === undefined || value === '' || value === null) {
          delete this.searchParams[key]
        }
      })
    },
    updateQueryParams () {
      const params = Object.assign({}, this.searchParams)
      const paramsEmpty = Object.entries(params).length === 0 && params.constructor === Object

      // if params are completely empty, clear the query string,
      // otherwise add the params to the query string.  this allows
      // users to bookmark searches.
      const query = paramsEmpty ? null : params
      const tabHash = (this.tabIndex === 1) ? 'advanced' : null

      this.$router.push({ query: query, hash: tabHash })
    },
    selectFilter () {
      if (this.selectedFilter) {
        this.selectedFilters.push(this.selectedFilter)
        // Set an empty value to show placeholder if we don't already have one.
        if (this.selectedFilter.type === 'select' &&
            !(this.selectedFilter.param in this.searchParams)) {
          this.searchParams[this.selectedFilter.param] = ''
        } else if (this.selectedFilter.type === 'booleanOrRange' &&
            !(`${this.selectedFilter.param}_has_value` in this.searchParams)) {
          this.searchParams[`${this.selectedFilter.param}_has_value`] = false
        }
      }

      this.selectedFilter = null
    },
    removeSelectedFilter (filterId) {
      const index = this.selectedFilters.findIndex(filter => filterId === filter.id)
      const filter = this.selectedFilters[index]
      const params = this.getParamNames(filter)

      this.selectedFilters.splice(index, 1)
      params.filter(
        param => param in this.searchParams).forEach(
        param => delete this.searchParams[param])
    },
    getParamNames (field) {
      if (field.type === 'range') {
        return [`${field.param}_min`, `${field.param}_max`]
      } else if (field.type === 'dateRange') {
        return [`${field.param}_before`, `${field.param}_after`]
      } else if (field.type === 'booleanOrRange') {
        return [`${field.param}_min`, `${field.param}_max`, `${field.param}_has_value`]
      } else if (field.type === 'booleanOrText') {
        return [field.param, `${field.param}_has_value`]
      } else {
        return [field.param]
      }
    }
  },
  created () {
    this.$store.dispatch(FETCH_CODES)
    this.$store.dispatch(FETCH_DRILLER_NAMES)
    this.$store.dispatch(FETCH_ORGANIZATION_NAMES)

    this.initSearchParams()
    this.initTabIndex()
    this.initSelectedFilters()

    // if the page loaded with a query, start a search.
    // Otherwise, the search does not need to run (see #1713)
    const query = this.$route.query
    if (Object.entries(query).length !== 0 && query.constructor === Object) {
      this.lastSearchTrigger = triggers.QUERY
      setTimeout(() => {
        this.locationSearch()
      }, 0)
      this.wellSearch()
    }
  },
  beforeMount () {
    this.scrolled = window.scrollY > 100
    window.addEventListener('scroll', this.handleScroll)
  },
  beforeDestroy () {
    window.removeEventListener('scroll', this.handleScroll)
  }
}
</script>

<style>
.wellTable[aria-busy='false'] {
  opacity: 1;
}
.wellTable[aria-busy='true'] {
  opacity: 0.6;
}
</style>
