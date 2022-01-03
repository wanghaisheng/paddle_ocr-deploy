import {
    createWebHistory,
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
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;