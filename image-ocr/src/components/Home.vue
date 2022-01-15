<template>
  <div class="home">
    <h1>Fun tools, 小工具</h1>

    <div class="menus">
      <div class="menu" v-for="menu in menus" :key="menu.name">
        <router-link :to="{'name': menu.name}">{{menu.title}}</router-link>
      </div>
    </div>

    <div class="image">
      <img src="../assets/image/table-wood-white-chair-isolated-tool-1105844-pxhere.com.jpg" alt="">
    </div>
  </div>
</template>

<script>


export default {
  name: "Home",
  components: {
  },
  props: {
    msg: String,
  },
  data() {
    return {
      menus: [
        {name: 'ImageOcr', title: '图像转文字'},
        {name: 'dishes', title: '菜品识别'},
        {name: 'ImageArtist', title: '风格迁移'},
        {name: 'ImageSuperResolution', title: '图片超分辨率'},
        // {name: 'ImageColor', title: '老照片修复'},
        {name: 'ImageStitch', title: '图像拼接'},
        {name: 'PositiveOrNegative', title: '文本情绪判断'},
      ]
    };
  },
  methods: {
   
    
  }
};
</script>

<style lang="less" scoped>
.home {
  .menus {
    display: flex;
    flex-wrap: wrap;
    text-align: center;
    .menu {
      margin: 50px;
    }
  }
}
</style>
