let a=document.createElement("style");a.innerHTML=".image-sr .upload[data-v-261a9d94]{font-size:24px;color:#fff;margin:50px 0}.image-sr .upload .file[data-v-261a9d94]{padding:4px 10px;height:20px;line-height:20px;position:relative;cursor:pointer;color:#888;background:#fafafa;border:1px solid #ddd;border-radius:4px;overflow:hidden;display:inline-block}.image-sr .upload .file input[data-v-261a9d94]{position:absolute;font-size:100px;right:0;top:0;opacity:0;cursor:pointer}.image-sr .upload .file[data-v-261a9d94]:hover{color:#444;background:#eee;border-color:#ccc;text-decoration:none}.image-sr .loading[data-v-261a9d94]{z-index:5000;height:100vh;width:100vw;position:absolute;top:0;left:0;padding:50% 0;background:rgba(0,0,0,.3);font-size:24px;color:#fff}.image-sr .preview[data-v-261a9d94]{position:relative;background:#f1f0ef;padding:10px}.image-sr .info[data-v-261a9d94]{color:#999;line-height:20px;margin:5px}",document.head.appendChild(a);import{r as e}from"./request.be6d239d.js";import{r as o,c as i,a as t,w as r,d,b as l,v as n,p as s,f as p,o as c,g}from"./index.4ea71b32.js";var f={name:"ImageSuperResolution",props:{msg:String,files:[]},data:()=>({count:0,loading:!1,imageData:null,direct:!0}),methods:{async formData(a){this.loading=!0;let o=a.target.files,i=new FormData;for(let a=0;a<o.length;a++)i.append("images",o[a]);let t={"Content-Type":"multipart/form-data"};try{const a=await e.post("/cv/image/superresolution",i,{headers:t,responseType:"blob"});this.imageData=window.URL.createObjectURL(a.data)}catch(a){alert("解析图片失败",a),console.error(a)}finally{this.loading=!1}}}};const m=a=>(s("data-v-261a9d94"),a=a(),p(),a),u={class:"image-sr"},h=m((()=>d("h1",null,"图片超分辨率",-1))),v=g("回首页"),x=m((()=>d("h3",null,"选择一张照片",-1))),b=m((()=>d("div",{class:"info"}," 可将图片的分辨率提升2～4倍。 ",-1))),w=m((()=>d("div",{class:"info"}," 服务器流量限制，小图片玩玩就行了，最好不要超过500K ",-1))),y={class:"upload"},D={class:"loading"},k=m((()=>d("h3",null,"结果预览",-1))),z={class:"preview"},_=["src"];f.render=function(a,e,s,p,g,f){const m=o("router-link");return c(),i("div",u,[h,t(m,{to:{name:"Home"}},{default:r((()=>[v])),_:1}),x,b,w,d("div",y,[d("input",{name:"",class:"file",id:"upload_file",type:"file",multiple:!1,onChange:e[0]||(e[0]=(...a)=>f.formData&&f.formData(...a)),"max-size":"1000"},null,32)]),l(d("div",D,"耗时比较久，请耐心等待 . . .",512),[[n,g.loading]]),k,d("div",z,[d("img",{src:g.imageData},null,8,_)])])},f.__scopeId="data-v-261a9d94";export{f as default};
