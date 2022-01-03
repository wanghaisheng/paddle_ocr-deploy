<template>
  <div class="emotion">
    <h1>文本情绪判断</h1>
    <router-link :to="{ name: 'Home' }">回首页</router-link>

    <div class="content">
      <div class="result">
        <transition name="draw">
          <div class="left" :style="leftStyle"></div>
        </transition>
        <div class="center">{{ label }}</div>
        <transition name="draw">
          <div class="right" :style="rightStyle"></div>
        </transition>
      </div>
      <textarea
        v-model="text"
        placeholder="随便输入一些想说的"
        rows="20"
        cols="100"
        @input="onchange"
      ></textarea>
    </div>
  </div>
</template>

<script>
import request from "..//request.js";

export default {
  name: "PositiveOrNegative",
  components: {},
  props: {},
  data() {
    return {
      text: "",
      result: { text: "", label: "other", score: 0.5 },
      timmer: -1,
    };
  },
  computed: {
    label() {
      return this.result.label === "negative" ? "消极" : "积极";
    },
    leftStyle() {
      let score =
        this.result.label === "negative"
          ? 1 - this.result.score
          : this.result.score;
      return `width: ${(score * 100).toFixed(2)}%`;
    },
    rightStyle() {
      let score =
        this.result.label === "negative"
          ? 1 - this.result.score
          : this.result.score;

      return `width: ${(100 - score * 100).toFixed(2)}%`;
    },
  },
  methods: {
    onchange() {
      clearTimeout(this.timmer);
      this.timmer = setTimeout(() => {
        this.sentiment();
      }, 800);
    },

    sentiment() {
      this.text = this.text.trim();
      if (this.text === "") {
        this.result = { text: "", label: "other", score: 0.5 };
        return;
      }
      request
        .post("/nlp/sentiment/analysis", { text: [this.text] })
        .then((resp) => {
          if (
            resp.data &&
            resp.data.code === 0 &&
            resp.data.result.length > 0
          ) {
            this.result = resp.data.result[0];
          }
        })
        .catch((e) => console.error(e));
    },
  },
};
</script>

<style lang="less" scoped>
.emotion {
  .content {
    .result {
      display: flex;
      width: 80vw;
      margin: 10px auto;
      text-align: center;
      .left {
        height: 50px;
        background: #42b983;
        border-radius: 50px 0 80px 50px;
      }
      .center {
        line-height: 2;
      }
      .right {
        height: 50px;
        background: coral;
        border-radius: 80px 50px 50px 0;
      }
    }
  }
}
.draw-enter-active, .draw-leave-active {
    transition: all 1s ease;
}
.draw-enter, .draw-leave-to /* .fade-leave-active below version 2.1.8 */ {
    height: 0;
}
</style>
