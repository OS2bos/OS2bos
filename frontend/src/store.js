import Vue from 'vue'
import Vuex from 'vuex'
import auth from './store-modules/auth.js'
import nav from './store-modules/nav.js'
import lists from './store-modules/lists.js'
import activity from './store-modules/activity.js'
import payment from './store-modules/payment.js'

Vue.use(Vuex)

export default new Vuex.Store({
    modules: {
        auth,
        nav,
        lists,
        activity,
        payment
    }
})
