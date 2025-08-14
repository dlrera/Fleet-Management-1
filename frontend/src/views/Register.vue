<template>
  <div class="register-page">
    <div class="container">
      <div class="row justify-content-center min-vh-100 align-items-center">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow">
            <div class="card-body p-4">
              <div class="text-center mb-4">
                <i class="bi bi-truck fs-1 text-primary"></i>
                <h2 class="mt-2">Create Account</h2>
                <p class="text-muted">Join Fleet Management System</p>
              </div>

              <div v-if="error" class="alert alert-danger" role="alert">
                {{ error }}
              </div>

              <div v-if="success" class="alert alert-success" role="alert">
                Registration successful! Redirecting...
              </div>

              <form @submit.prevent="handleRegister">
                <div class="row">
                  <div class="col-md-6 mb-3">
                    <label for="firstName" class="form-label">First Name</label>
                    <input
                      type="text"
                      class="form-control"
                      id="firstName"
                      v-model="formData.first_name"
                      required
                    />
                  </div>
                  <div class="col-md-6 mb-3">
                    <label for="lastName" class="form-label">Last Name</label>
                    <input
                      type="text"
                      class="form-control"
                      id="lastName"
                      v-model="formData.last_name"
                      required
                    />
                  </div>
                </div>

                <div class="mb-3">
                  <label for="username" class="form-label">Username</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-person"></i>
                    </span>
                    <input
                      type="text"
                      class="form-control"
                      id="username"
                      v-model="formData.username"
                      required
                      placeholder="Choose a username"
                    />
                  </div>
                </div>

                <div class="mb-3">
                  <label for="email" class="form-label">Email Address</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-envelope"></i>
                    </span>
                    <input
                      type="email"
                      class="form-control"
                      id="email"
                      v-model="formData.email"
                      required
                      placeholder="Enter email"
                    />
                  </div>
                </div>

                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-lock"></i>
                    </span>
                    <input
                      type="password"
                      class="form-control"
                      id="password"
                      v-model="formData.password"
                      required
                      placeholder="Create password (min. 12 characters)"
                      minlength="12"
                    />
                  </div>
                </div>

                <div class="mb-3">
                  <label for="confirmPassword" class="form-label">Confirm Password</label>
                  <div class="input-group">
                    <span class="input-group-text">
                      <i class="bi bi-lock-fill"></i>
                    </span>
                    <input
                      type="password"
                      class="form-control"
                      id="confirmPassword"
                      v-model="formData.password_confirm"
                      required
                      placeholder="Confirm password"
                    />
                  </div>
                  <div v-if="passwordMismatch" class="text-danger mt-1">
                    <small>Passwords do not match</small>
                  </div>
                </div>

                <div class="d-grid gap-2">
                  <button 
                    type="submit" 
                    class="btn btn-primary"
                    :disabled="loading || passwordMismatch"
                  >
                    <span v-if="loading">
                      <span class="spinner-border spinner-border-sm me-2"></span>
                      Creating Account...
                    </span>
                    <span v-else>
                      <i class="bi bi-person-plus me-2"></i>
                      Sign Up
                    </span>
                  </button>
                </div>
              </form>

              <hr class="my-4" />

              <div class="text-center">
                <p class="mb-0">
                  Already have an account?
                  <router-link to="/login" class="text-decoration-none">
                    Sign in
                  </router-link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

export default {
  name: 'Register',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const formData = ref({
      first_name: '',
      last_name: '',
      username: '',
      email: '',
      password: '',
      password_confirm: ''
    })
    
    const loading = ref(false)
    const error = ref('')
    const success = ref(false)

    const passwordMismatch = computed(() => {
      return formData.value.password && 
             formData.value.password_confirm && 
             formData.value.password !== formData.value.password_confirm
    })

    const handleRegister = async () => {
      if (passwordMismatch.value) {
        error.value = 'Passwords do not match'
        return
      }

      error.value = ''
      loading.value = true
      
      try {
        await authStore.register(formData.value)
        success.value = true
        setTimeout(() => {
          router.push('/')
        }, 1500)
      } catch (err) {
        const errorData = err.response?.data
        if (errorData?.username) {
          error.value = 'Username already exists'
        } else if (errorData?.email) {
          error.value = 'Email already registered'
        } else {
          error.value = errorData?.detail || 'Registration failed. Please try again.'
        }
      } finally {
        loading.value = false
      }
    }

    return {
      formData,
      loading,
      error,
      success,
      passwordMismatch,
      handleRegister
    }
  }
}
</script>

<style scoped>
.register-page {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

.card {
  border: none;
  border-radius: 1rem;
}

.input-group-text {
  background-color: transparent;
  border-right: none;
}

.form-control {
  border-left: none;
}

.form-control:focus {
  box-shadow: none;
  border-color: #ced4da;
}

.input-group:focus-within .input-group-text {
  border-color: #86b7fe;
}
</style>