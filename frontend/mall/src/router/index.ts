import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import ProductList from '@/views/ProductList.vue'
import ProductDetail from '@/views/ProductDetail.vue'
import Register from '@/views/Register.vue'
import Login from '@/views/Login.vue'
import AddressManagement from '@/views/AddressManagement.vue'
import ShoppingCart from '@/views/ShoppingCart.vue'
import OrderConfirm from '@/views/OrderConfirm.vue'
import OrderPayment from '@/views/OrderPayment.vue'
import OrderList from '@/views/OrderList.vue'
import OrderDetail from '@/views/OrderDetail.vue'
import UserCenter from '@/views/UserCenter.vue'
import MerchantProductShelf from '@/views/MerchantProductShelf.vue'
import MerchantShipping from '@/views/MerchantShipping.vue'
import MerchantServiceMessages from '@/views/MerchantServiceMessages.vue'
import { getMe } from '@/services/user-center'
import { getAuthState, setAuthSession } from '@/utils/auth'

type UserRole = 'admin' | 'merchant' | 'normal' | 'staff' | ''

function getDefaultRouteByRole(role: UserRole) {
  if (role === 'admin' || role === 'merchant') {
    return '/merchant/products'
  }
  return '/home'
}

async function resolveUserRole(): Promise<UserRole> {
  const state = getAuthState()
  const cachedRole = (state.role || '') as UserRole
  if (!state.accessToken) {
    return ''
  }
  if (cachedRole) {
    return cachedRole
  }

  try {
    const profile = await getMe(state.accessToken)
    const role = (profile.role || '') as UserRole
    setAuthSession(state.accessToken, state.refreshToken, profile.username || state.username, role)
    return role
  } catch {
    return ''
  }
}

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
      path: '/login',
      name: 'Login',
      component: Login,
    },
    {
      path: '/addresses',
      name: 'AddressManagement',
      component: AddressManagement,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/cart',
      name: 'ShoppingCart',
      component: ShoppingCart,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/order/confirm',
      name: 'OrderConfirm',
      component: OrderConfirm,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/order/payment/:id',
      name: 'OrderPayment',
      component: OrderPayment,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/orders',
      name: 'OrderList',
      component: OrderList,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/orders/:id',
      name: 'OrderDetail',
      component: OrderDetail,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/user-center',
      name: 'UserCenter',
      component: UserCenter,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/merchant/products',
      name: 'MerchantProductShelf',
      component: MerchantProductShelf,
      meta: {
        requiresAuth: true,
        roles: ['admin', 'merchant'],
      },
    },
    {
      path: '/merchant/shipping',
      name: 'MerchantShipping',
      component: MerchantShipping,
      meta: {
        requiresAuth: true,
        roles: ['admin', 'merchant'],
      },
    },
    {
      path: '/merchant/service-messages',
      name: 'MerchantServiceMessages',
      component: MerchantServiceMessages,
      meta: {
        requiresAuth: true,
        roles: ['admin', 'merchant'],
      },
    },
    {
      path: '/',
      redirect: '/home',
    },
  ],
})

router.beforeEach(async (to) => {
  const state = getAuthState()
  const isLoggedIn = Boolean(state.accessToken)
  const requiresAuth = Boolean(to.meta.requiresAuth)
  const allowedRoles = Array.isArray(to.meta.roles) ? (to.meta.roles as UserRole[]) : []

  if (requiresAuth && !isLoggedIn) {
    return {
      path: '/login',
      query: { redirect: to.fullPath },
    }
  }

  if (!isLoggedIn) {
    return true
  }

  const role = await resolveUserRole()
  const defaultRoute = getDefaultRouteByRole(role)

  if (allowedRoles.length > 0 && !allowedRoles.includes(role)) {
    return defaultRoute
  }

  if (to.path === '/login' || to.path === '/register') {
    return defaultRoute
  }

  return true
})

export default router
