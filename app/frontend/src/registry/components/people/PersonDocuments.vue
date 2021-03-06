<template>
  <div id="person-documents">
    <div v-if="loading" class="row no-gutters">
      <div class="col-md-12">
        Loading documents...
        <div class="fa-2x text-center">
          <i class="fa fa-circle-o-notch fa-spin"></i>
        </div>
      </div>
    </div>
    <div v-else>
      <div class="row no-gutters" v-if="userRoles.registry.edit">
        <div class="col-md-12">
          <h4>Internal documentation - authorized access only</h4>
          <div v-if="error">
            {{error}}
          </div>
          <ul v-else-if="files && files.private && files.private.length">
            <li v-for="(file, index) in files.private" :key="index">
              <a :href="file.url" :download="file.name" target="_blank">{{file.name}}</a>
              <a class="fa fa-trash fa-lg"
                variant="primary"
                style="margin-left: .5em"
                href="#"
                v-on:click="confirmDeleteFile(file.name, 'private', $event)" />
            </li>
          </ul>
            <div v-else>
              No additional private documentation currently available.
            </div>
        </div>
      </div>
    </div>
    <b-modal
      ok-variant="primary"
      cancel-variant="default"
      v-on:ok="deleteFile"
      ref="deleteModal" >
      <p>Are you sure you would like to delete this file?</p>
      <p>{{file}}</p>
    </b-modal>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import ApiService from '@/common/services/ApiService.js'

export default {
  name: 'PersonDocuments',
  props: {
    files: null,
    guid: {
      type: String,
      default: null
    }
  },
  data () {
    return {
      loading: false,
      error: null,
      file: '',
      fileType: ''
    }
  },
  computed: {
    ...mapGetters(['userRoles'])
  },
  methods: {
    showModal () {
      this.$refs.deleteModal.show()
    },
    hideModal () {
      this.$refs.deleteModal.hide()
    },
    confirmDeleteFile (file, fileType, e) {
      e.preventDefault()
      this.file = file
      this.fileType = fileType
      this.showModal()
    },
    deleteFile () {
      this.hideModal()
      let isPrivate = false
      if (this.fileType === 'private') {
        isPrivate = true
      }
      ApiService.deleteFile(`drillers/${this.guid}/delete_document?filename=${this.file}&private=${isPrivate}`)
        .then(() => {
          this.$emit('fetchFiles')
        })
    }
  }
}
</script>

<style lang="scss">

</style>
