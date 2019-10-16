/* Copyright (C) 2019 Magenta ApS, http://magenta.dk.
 * Contact: info@magenta.dk.
 *
 * This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at https://mozilla.org/MPL/2.0/. */


import axios from '../components/http/Http.js'
import router from '../router.js'
import notify from '../components/notifications/Notify.js'
import store from '../store.js';


const state = {
    accesstoken: null,
    uid: null
}

const getters = {
    getAuth (state) {
        if (state.accesstoken && state.uid) {
            return {
                token: state.accesstoken,
                uid: state.uid
            }
        } else {
            return false
        }
    }
}

const mutations = {
    setAccessToken (state, token) {
        state.accesstoken = token
    },
    setUID (state, uid) {
        state.uid = uid
    }
}

const actions = {
    registerAuth: function({commit, dispatch, rootState}, authdata) {
        commit('setAccessToken', authdata.token)
        commit('setUID', authdata.uid)
        dispatch('fetchLists')
        .then(() => {
            let user = rootState.user.users.find(function(u) {
                return u.id === parseInt(authdata.uid)
            })
            commit('setUser', user)
            notify('Du er logget ind', 'success')
        })
        .catch(err => {
            console.log(err)
        })
    },
    logout: function({dispatch}) {
        dispatch('clearAuth')
        notify('Du er logget ud')
    },
    clearAuth: function ({commit}) {
        commit('setAccessToken', null)
        commit('setUID', null)
        commit('setUser', null)
        router.replace('/login')
    }
}

export default {
    state,
    getters,
    mutations,
    actions
}