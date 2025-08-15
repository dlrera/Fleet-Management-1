<template>
  <v-container fluid class="fill-height" style="background: linear-gradient(135deg, #216093 0%, #001B48 100%);">
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <v-card elevation="12" rounded="lg">
          <v-card-title class="text-h4 text-center py-6 bg-primary">
            <v-icon size="40" class="mr-2">mdi-shield-lock</v-icon>
            <span class="text-white">Welcome Back</span>
          </v-card-title>
          
          <v-card-text class="pa-8">
            <v-form @submit.prevent="handleLogin" ref="form" v-model="valid">
              <v-text-field
                v-model="credentials.username"
                label="Username"
                prepend-inner-icon="mdi-account"
                variant="outlined"
                class="mb-4"
                :rules="[rules.required]"
                :disabled="loading"
                color="primary"
              ></v-text-field>

              <v-text-field
                v-model="credentials.password"
                label="Password"
                prepend-inner-icon="mdi-lock"
                variant="outlined"
                :type="showPassword ? 'text' : 'password'"
                :append-inner-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append-inner="showPassword = !showPassword"
                :rules="[rules.required]"
                :disabled="loading"
                color="primary"
              ></v-text-field>

              <v-checkbox
                v-model="rememberMe"
                label="Remember me"
                color="primary"
                class="mb-4"
              ></v-checkbox>

              <v-alert
                v-if="error"
                type="error"
                variant="tonal"
                class="mb-4"
                closable
                @click:close="error = null"
              >
                {{ error }}
              </v-alert>

              <v-btn
                type="submit"
                block
                size="large"
                color="primary"
                :loading="loading"
                :disabled="!valid || loading"
                class="mb-4"
              >
                <v-icon left>mdi-login</v-icon>
                Sign In
              </v-btn>

              <v-divider class="my-4"></v-divider>

              <div class="text-center">
                <p class="text-body-2 mb-2">Demo Credentials</p>
                <v-chip-group>
                  <v-chip color="accent" variant="tonal" @click="fillDemoCredentials">
                    <v-icon start size="small">mdi-account</v-icon>
                    admin / admin123
                  </v-chip>
                </v-chip-group>
              </div>
            </v-form>
          </v-card-text>

          <v-card-actions class="px-8 pb-8">
            <v-btn variant="text" color="primary" block @click="showRegister = true">
              Don't have an account? Sign Up
            </v-btn>
          </v-card-actions>
        </v-card>

        <!-- Registration Dialog -->
        <v-dialog v-model="showRegister" max-width="500">
          <v-card>
            <v-card-title class="text-h5 bg-primary text-white">
              Create Account
            </v-card-title>
            <v-card-text class="pt-6">
              <v-form @submit.prevent="handleRegister" ref="registerForm" v-model="registerValid">
                <v-text-field
                  v-model="registerData.username"
                  label="Username"
                  variant="outlined"
                  :rules="[rules.required]"
                  class="mb-3"
                ></v-text-field>
                <v-text-field
                  v-model="registerData.email"
                  label="Email"
                  variant="outlined"
                  :rules="[rules.required, rules.email]"
                  class="mb-3"
                ></v-text-field>
                <v-text-field
                  v-model="registerData.password"
                  label="Password"
                  type="password"
                  variant="outlined"
                  :rules="[rules.required, rules.minLength]"
                  class="mb-3"
                ></v-text-field>
                <v-text-field
                  v-model="registerData.password2"
                  label="Confirm Password"
                  type="password"
                  variant="outlined"
                  :rules="[rules.required, rules.passwordMatch]"
                ></v-text-field>
              </v-form>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn variant="text" @click="showRegister = false">Cancel</v-btn>
              <v-btn color="primary" variant="elevated" @click="handleRegister" :loading="loading">
                Create Account
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

export default {
  name: 'Login',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    
    const valid = ref(false)
    const registerValid = ref(false)
    const loading = ref(false)
    const error = ref(null)
    const showPassword = ref(false)
    const rememberMe = ref(false)
    const showRegister = ref(false)
    
    const credentials = ref({
      username: '',
      password: ''
    })
    
    const registerData = ref({
      username: '',
      email: '',
      password: '',
      password2: ''
    })
    
    const rules = {
      required: v => !!v || 'This field is required',
      email: v => /.+@.+\..+/.test(v) || 'Invalid email',
      minLength: v => v.length >= 8 || 'Password must be at least 8 characters',
      passwordMatch: v => v === registerData.value.password || 'Passwords do not match'
    }
    
    const fillDemoCredentials = () => {
      credentials.value.username = 'admin'
      credentials.value.password = 'admin123'
    }
    
    const handleLogin = async () => {
      error.value = null
      loading.value = true
      
      try {
        await authStore.login(credentials.value)
        router.push('/')
      } catch (err) {
        error.value = err.response?.data?.detail || 'Invalid username or password'
      } finally {
        loading.value = false
      }
    }
    
    const handleRegister = async () => {
      if (!registerValid.value) return
      
      loading.value = true
      try {
        await authStore.register(registerData.value)
        showRegister.value = false
        router.push('/')
      } catch (err) {
        error.value = err.response?.data?.detail || 'Registration failed'
      } finally {
        loading.value = false
      }
    }
    
    return {
      valid,
      registerValid,
      loading,
      error,
      showPassword,
      rememberMe,
      showRegister,
      credentials,
      registerData,
      rules,
      fillDemoCredentials,
      handleLogin,
      handleRegister
    }
  }
}
</script>

<style scoped>
.fill-height {
  min-height: 100vh;
}
</style>