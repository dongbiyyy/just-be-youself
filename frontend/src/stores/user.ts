import { defineStore } from 'pinia'
import client from '../api/client'

export interface UserInfo {
  id: number
  username: string
  email: string
  full_name: string
  role: string
  department: string
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null as UserInfo | null
  }),
  actions: {
    async login(username: string, password: string) {
      const form = new URLSearchParams()
      form.append('username', username)
      form.append('password', password)
      const { data } = await client.post('/auth/login', form, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      this.token = data.access_token
      localStorage.setItem('token', this.token)
      await this.fetchMe()
    },
    async fetchMe() {
      const { data } = await client.get<UserInfo>('/auth/me')
      this.user = data
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
    }
  }
})
