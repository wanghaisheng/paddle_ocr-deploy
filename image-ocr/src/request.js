import axios from 'axios'

// 创建axios实例
var instance = axios.create({ timeout: 1000 * 300 })

// 响应拦截器
instance.interceptors.response.use(
    // 请求成功
    res => res.status === 200 ? Promise.resolve(res) : Promise.reject(res),
    // 请求失败
    error => {
        const { response } = error
        if (response) {
            // 请求已发出，但是不在2xx的范围
            return Promise.reject(response)
        } else {
            console.log('catch error', error)
            return Promise.reject(error)
        }
    }
)

export default instance
