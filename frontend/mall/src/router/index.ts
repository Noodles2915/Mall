import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import ProductList from '@/views/ProductList.vue'
import ProductDetail from '@/views/ProductDetail.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/home',
      name: 'Home',
      component: Home,
    },
    {
      path: '/products',
      name: 'ProductList',
      component: ProductList,
    },
    {
      path: '/products/:id',
      name: 'ProductDetail',
      component: ProductDetail,
    },
    {
      path: '/',
      redirect: '/home',
    },
  ],
})

export default router
