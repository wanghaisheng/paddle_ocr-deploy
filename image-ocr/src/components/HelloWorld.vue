<template>
  <div class="uploader">
    <h1>{{ msg }}</h1>
    <file-pond
      :name="uploadName"
      ref="pond"
      label-idle="Drop files here..."
      :allow-multiple="false"
      accepted-file-types="image/jpeg, image/png"
      :server="uploadOptions"
      :files="files"
      @:init="handleFilePondInit"
    />
    <div class="loading" v-show="loading">
      处理中 . . .
    </div>
    <div class="preview">
      <div class="text" v-for="(t,index) in textData" :key="index">
        <div>{{t}}</div>
      </div>
    </div>
  </div>
</template>

<script>
// Import Vue FilePond
import vueFilePond from "vue-filepond";
// Import FilePond styles
import "filepond/dist/filepond.min.css";
// Import FilePond plugins
// Please note that you need to install these plugins separately
// Import image preview plugin styles
import "filepond-plugin-image-preview/dist/filepond-plugin-image-preview.min.css";
// Import image preview and file type validation plugins
import FilePondPluginFileValidateType from "filepond-plugin-file-validate-type";
import FilePondPluginImagePreview from "filepond-plugin-image-preview";

const FilePond = vueFilePond(
  FilePondPluginFileValidateType,
  FilePondPluginImagePreview
);

export default {
  name: "HelloWorld",
  components: {
    FilePond,
  },
  props: {
    msg: String,
    files: [],
  },
  data() {
    return {
      count: 0,
      imageUpload: "",
      uploadName: 'images',
      uploadOptions: {
        process: {
          url: "/cv/ocr/text",
          method: 'POST',
          ondata: this.formData,
          onload: this.loaded,
          onerror: error => {console.error(error)}
        }
      },
      loading: false,
      textData: [],
    };
  },
  methods: {
    handleFilePondInit() {
      
    },
    formData(d) {
      if (d) {
        let images = d.getAll(this.uploadName).filter(data => data instanceof File) 
        d.delete(this.uploadName)
        images.forEach(img =>  d.append(this.uploadName, img))
      }
      this.textData = []
      this.loading = true
      return d
    },
    loaded(d) {
      this.loading = false
      try {
        let data = JSON.parse(d)
        if (data.code === 0) {
          let lastTop = 0
          let line = ''
          data.result[0].data.forEach(text => {
            let top = text.text_box_position[0][1]
            if (lastTop < top) {
              lastTop = top
              this.textData.push(line)
              line = ''
            } else {
              line += '    ' 
            }
            line += text.text
          })
          this.textData.push(line)

        } else {
          alert('解析图片失败', textData.code)
        }
      } catch(e) {
        alert('解析图片失败', e)
        console.error(e)
      }
    }
  }
};
</script>

<style lang="less" scoped>
.uploader {
  .loading {
    z-index: 5000;
    height: 100vh;
    width: 100vw;
    position: absolute;
    top: 0;
    left: 0;
    padding: 50% 0px;
    background: rgba(0, 0, 0, 0.3);
    font-size: 24px;
    color: white;
  }
  .preview {
    position: relative;
    background: #f1f0ef;
  }
}
</style>
