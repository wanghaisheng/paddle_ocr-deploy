import {
    createWebHashHistory,
    createRouter
} from "vue-router";
import Home from './components/Home.vue'

const routes = [{
        path: '/',
        name: 'Home',
        component: Home
    },
    {
        name: 'ImageOcr',
        path: '/ImageOcr',
        component: () => import('./components/ImageOcr.vue')
    },
    {
        name: 'PositiveOrNegative',
        path: '/PositiveOrNegative',
        component: () => import('./components/PositiveOrNegative.vue')
    },
    {
        name: 'ImageStitch',
        path: '/ImageStitch',
        component: () => import('./components/ImageStitch.vue')
    },
];

const router = createRouter({
    history: createWebHashHistory(),
    routes,
});

export default router;