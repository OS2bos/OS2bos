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
        if (token === null) {
            sessionStorage.removeItem('bevaccesstoken')
        } else {
            axios.defaults.headers.common['Authorization'] = `Token ${ token }`
            sessionStorage.setItem('bevaccesstoken', token)
        }
        state.accesstoken = token
    },
    setUID (state, uid) {
        if (uid === null) {
            sessionStorage.removeItem('bevuid')
        } else {
            sessionStorage.setItem('bevuid', uid)
        }
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
                return u.id === authdata.uid
            })
            commit('setUser', user)
            notify('Du er logget ind', 'success')
        })
        .catch(err => {
            console.log(err)
        })
    },
    login: function({commit, dispatch, rootState}, authData) {
        axios.post('/token/', {
            username: authData.username,
            password: authData.password
        })
        .then(res => {
            commit('setAccessToken', res.data.access)
            commit('setRefreshToken', res.data.refresh)
            dispatch('setTimer')
            dispatch('fetchLists')
            .then(() => {
                let user = rootState.user.users.find(function(u) {
                    return u.username === authData.username
                })
                commit('setUser', user)
                notify('Du er logget ind', 'success')
                dispatch('postLogin')
            })
            .catch(err => {
                console.log(err)
            })
        })
        .catch(err => {
            store.dispatch('parseErrorOutput', err)
            dispatch('clearAuth')
        })
    },
    setTimer: function({dispatch}) {
        setInterval(() => {
            dispatch('refreshToken')
        }, 270000);
    },
    postLogin: function() {
        router.push('/')
    },
    refreshToken: function({commit, dispatch, state}) {
        if (state.refreshtoken) {    
            axios.post('/token/refresh/', {
                refresh: state.refreshtoken
            })
            .then(res => {
                commit('setAccessToken', res.data.access)
            })
            .catch(err => {
                console.log(err)
                dispatch('clearAuth')
            })
        }
    },
    autoLogin: function({commit, dispatch, rootState}) {
        // check for tokens in session storage and refresh session
        const refreshtoken = sessionStorage.getItem('refreshtoken')
        const accesstoken = sessionStorage.getItem('bevaccesstoken')
        const user_id = parseInt(sessionStorage.getItem('userid'))
        if (refreshtoken) {
            commit('setAccessToken', accesstoken)
            commit('setRefreshToken', refreshtoken)
            dispatch('refreshToken')
            .then(() => {
                dispatch('setTimer')
                dispatch('fetchLists').then(() => {
                    let user = rootState.user.users.find(function(u) {
                        return u.id === user_id
                    })
                    commit('setUser', user)
                })
                dispatch('postLogin')
            })
            .catch(err => store.dispatch('parseErrorOutput', err))
        } else {
            dispatch('clearAuth')
        }
    },
    logout: function({dispatch}) {
        dispatch('clearAuth')
        notify('Du er logget ud')
    },
    clearAuth: function ({commit}) {
        commit('setAccessToken', null)
        commit('setRefreshToken', null)
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