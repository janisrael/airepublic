import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('auth_token'))
  const isAuthenticated = ref(false)
  const loading = ref(false)
  const error = ref(null)

  // Getters
  const userRole = computed(() => user.value?.role_name || user.value?.role || 'user')
  const userPermissions = computed(() => user.value?.permissions || [])
  const isAdmin = computed(() => userRole.value === 'admin' || userRole.value === 'superuser')
  const isPremium = computed(() => userRole.value === 'premium_user' || isAdmin.value)
  const isDeveloper = computed(() => userRole.value === 'developer' || isAdmin.value)

  // Actions
  const setUser = (userData) => {
    user.value = userData
    isAuthenticated.value = !!userData
  }

  const setToken = (authToken) => {
    token.value = authToken
    if (authToken) {
      localStorage.setItem('auth_token', authToken)
    } else {
      localStorage.removeItem('auth_token')
    }
  }

  const setLoading = (isLoading) => {
    loading.value = isLoading
  }

  const setError = (errorMessage) => {
    error.value = errorMessage
  }

  const clearError = () => {
    error.value = null
  }

  // Authentication methods
  const login = async (credentials) => {
    setLoading(true)
    clearError()

    try {
      const response = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials)
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setToken(data.token)
        setUser(data.user)
        return { success: true, user: data.user }
      } else {
        setError(data.error || 'Login failed')
        return { success: false, error: data.error || 'Login failed' }
      }
    } catch (err) {
      const errorMessage = 'Network error. Please try again.'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  const register = async (userData) => {
    setLoading(true)
    clearError()

    try {
      const response = await fetch('http://localhost:5000/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
      })

      const data = await response.json()

      if (response.ok && data.success) {
        return { success: true, message: data.message }
      } else {
        setError(data.error || 'Registration failed')
        return { success: false, error: data.error || 'Registration failed' }
      }
    } catch (err) {
      const errorMessage = 'Network error. Please try again.'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  const logout = async () => {
    setLoading(true)
    clearError()

    try {
      if (token.value) {
        await fetch('http://localhost:5000/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token.value}`,
            'Content-Type': 'application/json',
          }
        })
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      setToken(null)
      setUser(null)
      setLoading(false)
    }
  }

  const refreshToken = async () => {
    if (!token.value) return false

    try {
      const response = await fetch('http://localhost:5000/api/auth/refresh', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token.value}`,
          'Content-Type': 'application/json',
        }
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setToken(data.token)
        setUser(data.user)
        return true
      } else {
        logout()
        return false
      }
    } catch (err) {
      console.error('Token refresh error:', err)
      logout()
      return false
    }
  }

  const verifyToken = async () => {
    if (!token.value) return false

    try {
      const response = await fetch('http://localhost:5000/api/auth/verify', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token.value}`,
          'Content-Type': 'application/json',
        }
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setUser(data.user)
        return true
      } else {
        logout()
        return false
      }
    } catch (err) {
      console.error('Token verification error:', err)
      logout()
      return false
    }
  }

  const socialLogin = async (provider) => {
    setLoading(true)
    clearError()

    try {
      // Redirect to backend OAuth endpoint
      window.location.href = `http://localhost:5000/api/auth/social/${provider}`
    } catch (err) {
      const errorMessage = 'Social login failed. Please try again.'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  const socialRegister = async (provider) => {
    setLoading(true)
    clearError()

    try {
      // Redirect to backend OAuth endpoint with registration flag
      window.location.href = `http://localhost:5000/api/auth/social/${provider}?action=register`
    } catch (err) {
      const errorMessage = 'Social registration failed. Please try again.'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  const forgotPassword = async (email) => {
    setLoading(true)
    clearError()

    try {
      const response = await fetch('http://localhost:5000/api/auth/forgot-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        return { success: true, message: data.message }
      } else {
        setError(data.error || 'Password reset failed')
        return { success: false, error: data.error || 'Password reset failed' }
      }
    } catch (err) {
      const errorMessage = 'Network error. Please try again.'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  const resetPassword = async (token, newPassword) => {
    setLoading(true)
    clearError()

    try {
      const response = await fetch('http://localhost:5000/api/auth/reset-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token, password: newPassword })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        return { success: true, message: data.message }
      } else {
        setError(data.error || 'Password reset failed')
        return { success: false, error: data.error || 'Password reset failed' }
      }
    } catch (err) {
      const errorMessage = 'Network error. Please try again.'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  const updateProfile = async (profileData) => {
    setLoading(true)
    clearError()

    try {
      const response = await fetch('http://localhost:5000/api/auth/profile', {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token.value}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData)
      })

      const data = await response.json()

      if (response.ok && data.success) {
        setUser(data.user)
        return { success: true, user: data.user }
      } else {
        setError(data.error || 'Profile update failed')
        return { success: false, error: data.error || 'Profile update failed' }
      }
    } catch (err) {
      const errorMessage = 'Network error. Please try again.'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  const changePassword = async (currentPassword, newPassword) => {
    setLoading(true)
    clearError()

    try {
      const response = await fetch('http://localhost:5000/api/auth/change-password', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token.value}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ currentPassword, newPassword })
      })

      const data = await response.json()

      if (response.ok && data.success) {
        return { success: true, message: data.message }
      } else {
        setError(data.error || 'Password change failed')
        return { success: false, error: data.error || 'Password change failed' }
      }
    } catch (err) {
      const errorMessage = 'Network error. Please try again.'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setLoading(false)
    }
  }

  // Permission checking
  const hasPermission = (permission) => {
    return userPermissions.value.includes(permission)
  }

  const hasRole = (role) => {
    return userRole.value === role
  }

  const hasAnyRole = (roles) => {
    return roles.includes(userRole.value)
  }

  // Initialize store
  const initialize = async () => {
    console.log('Auth store initialize: token.value =', token.value)
    if (token.value) {
      setLoading(true)
      try {
        console.log('Auth store: Verifying token...')
        await verifyToken()
        console.log('Auth store: Token verification complete. User:', user.value)
      } finally {
        setLoading(false)
      }
    } else {
      console.log('Auth store: No token found, user remains unauthenticated')
    }
  }

  return {
    // State
    user,
    token,
    isAuthenticated,
    loading,
    error,
    
    // Getters
    userRole,
    userPermissions,
    isAdmin,
    isPremium,
    isDeveloper,
    
    // Actions
    setUser,
    setToken,
    setLoading,
    setError,
    clearError,
    
    // Authentication methods
    login,
    register,
    logout,
    refreshToken,
    verifyToken,
    socialLogin,
    socialRegister,
    forgotPassword,
    resetPassword,
    updateProfile,
    changePassword,
    
    // Permission methods
    hasPermission,
    hasRole,
    hasAnyRole,
    
    // Initialization
    initialize
  }
})
