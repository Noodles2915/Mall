import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import ProductList from '@/views/ProductList.vue'
import ProductDetail from '@/views/ProductDetail.vue'
import Register from '@/views/Register.vue'
import AddressManagement from '@/views/AddressManagement.vue'
import ShoppingCart from '@/views/ShoppingCart.vue'
import OrderConfirm from '@/views/OrderConfirm.vue'
import OrderPayment from '@/views/OrderPayment.vue'
import OrderList from '@/views/OrderList.vue'
import OrderDetail from '@/views/OrderDetail.vue'

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
      path: '/register',
      name: 'Register',
      component: Register,
    },
    {
      path: '/addresses',
      name: 'AddressManagement',
      component: AddressManagement,
    },
    {
      path: '/cart',
      name: 'ShoppingCart',
      component: ShoppingCart,
    },
    {
      path: '/order/confirm',
      name: 'OrderConfirm',
      component: OrderConfirm,
    },
    {
      path: '/order/payment/:id',
      name: 'OrderPayment',
      component: OrderPayment,
    },
    {
      path: '/orders',
      name: 'OrderList',
      component: OrderList,
    },
    {
      path: '/orders/:id',
      name: 'OrderDetail',
      component: OrderDetail,
    },
    {
      path: '/',
      redirect: '/home',
    },
  ],
})

export default router
