<template>
  <div class="image-stitch">
    <h1>图像拼接</h1>
    <router-link :to="{ name: 'Home' }">回首页</router-link>

    <h3>选择多个文件</h3>
    <div class="upload">
      <input
        name=""
        class="file"
        id="upload_file"
        type="file"
        multiple
        @change="formData"
      />

      <div class="switch">
        <input
          v-model="direct"
          type="checkbox"
          id="toggle-button"
          name="switch"
          checked
        />
        <label for="toggle-button" class="button-label">
          <span class="circle"></span>
          <span class="text on" v-show="direct">横向拼接</span>
          <span class="text off" v-show="!direct">纵向拼接</span>
        </label>
      </div>
    </div>
    <div class="loading" v-show="loading">处理中 . . .</div>
    <h3>结果预览</h3>
    <div class="preview">
      <img :src="imageData" />
    </div>
  </div>
</template>

<script>
import request from "../request.js";

export default {
  name: "ImageStitch",
  props: {
    msg: String,
    files: [],
  },
  data() {
    return {
      count: 0,
      loading: false,
      imageData: null,
      direct: true
    };
  },
  methods: {
    async formData(e) {
      this.loading = true;
      let files = e.target.files;
      let formData = new FormData();
      // formData重复的往一个值添加数据并不会被覆盖掉，可以全部接收到，可以通过formData.getAll('files')来查看所有插入的数据
      for (let i = 0; i < files.length; i++) {
        formData.append("images", files[i]);
      }
      formData.append("direct", this.direct?'horizontal':'vertical')
      let url = "/cv/image/merge";
      let headers = {
        "Content-Type": "multipart/form-data",
      };

      try {
        const data = await request.post(url, formData, {
          headers: headers,
          responseType: "blob",
        });
        this.imageData = window.URL.createObjectURL(data.data);
      } catch (e) {
        alert("解析图片失败", e);
        console.error(e);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style lang="less" scoped>
.image-stitch {
  .upload {
    font-size: 24px;
    color: white;
    margin: 50px 0;
    .file {
      padding: 4px 10px;
      height: 20px;
      line-height: 20px;
      position: relative;
      cursor: pointer;
      color: #888;
      background: #fafafa;
      border: 1px solid #ddd;
      border-radius: 4px;
      overflow: hidden;
      display: inline-block;
      *display: inline;
      *zoom: 1;
    }

    .file input {
      position: absolute;
      font-size: 100px;
      right: 0;
      top: 0;
      opacity: 0;
      filter: alpha(opacity=0);
      cursor: pointer;
    }

    .file:hover {
      color: #444;
      background: #eee;
      border-color: #ccc;
      text-decoration: none;
    }

    .switch {
      margin: 20px;
      #toggle-button {
        display: none;
      }

      .button-label {
        position: relative;
        display: inline-block;
        width: 130px;
        height: 35px;
        background-color: #ccc;
        box-shadow: #ccc 0px 0px 0px 2px;
        border-radius: 30px;
        overflow: hidden;
      }

      .circle {
        position: absolute;
        top: 0;
        left: 0;
        width: 35px;
        height: 35px;
        border-radius: 50%;
        background-color: #fff;
      }

      .button-label .text {
        line-height: 35px;
        font-size: 18px;
        text-shadow: 0 0 2px #ddd;
      }

      .on {
        color: #fff;
        display: inline-block;
        text-indent: -25px;
      }

      .off {
        color: #fff;
        display: inline-block;
        text-indent: 38px;
      }

      .button-label .circle {
        left: 0;
        transition: all 0.3s;
      }

      #toggle-button:checked + label.button-label .circle {
        left: 95px;
      }
    }
  }
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
    padding: 10px;
  }
}
</style>
