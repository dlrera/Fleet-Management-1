<template>
  <div class="user-management-container">
    <v-card>
      <v-card-title class="d-flex align-center justify-space-between">
        <div>
          <h2>User Management</h2>
          <p class="text-body-2 text-medium-emphasis">Manage user accounts and permissions</p>
        </div>
        <v-btn color="primary" @click="showInviteDialog = true">
          <v-icon left>mdi-email-send</v-icon>
          Send Invitation
        </v-btn>
      </v-card-title>

      <v-card-text>
        <!-- User Table -->
        <v-data-table
          :headers="headers"
          :items="users"
          :loading="loading"
          class="elevation-0"
        >
          <template #item.roles="{ item }">
            <v-chip-group>
              <v-chip
                v-for="role in item.roles"
                :key="role"
                :color="getRoleColor(role)"
                size="small"
                variant="tonal"
              >
                {{ role }}
              </v-chip>
            </v-chip-group>
          </template>

          <template #item.is_active="{ item }">
            <v-chip
              :color="item.is_active ? 'success' : 'error'"
              size="small"
              variant="tonal"
            >
              {{ item.is_active ? 'Active' : 'Inactive' }}
            </v-chip>
          </template>

          <template #item.actions="{ item }">
            <v-btn
              icon="mdi-pencil"
              size="small"
              variant="text"
              @click="editUser(item)"
              :disabled="item.username === currentUser.username"
            />
            <v-btn
              :icon="item.is_active ? 'mdi-account-off' : 'mdi-account-check'"
              size="small"
              variant="text"
              :color="item.is_active ? 'warning' : 'success'"
              @click="toggleUserStatus(item)"
              :disabled="item.username === currentUser.username"
            />
            <v-btn
              icon="mdi-delete"
              size="small"
              variant="text"
              color="error"
              @click="confirmDelete(item)"
              :disabled="item.username === currentUser.username"
            />
          </template>
        </v-data-table>

        <!-- Pending Invitations -->
        <div v-if="invitations.length > 0" class="mt-6">
          <h3 class="text-h6 mb-3">Pending Invitations</h3>
          <v-list>
            <v-list-item
              v-for="invitation in invitations"
              :key="invitation.id"
              :class="{ 'expired': invitation.is_expired }"
            >
              <template #prepend>
                <v-icon>mdi-email-outline</v-icon>
              </template>
              <v-list-item-title>{{ invitation.email }}</v-list-item-title>
              <v-list-item-subtitle>
                Role: {{ invitation.role }} | 
                Invited by: {{ invitation.invited_by }} |
                Expires: {{ formatDate(invitation.expires_at) }}
              </v-list-item-subtitle>
              <template #append>
                <v-btn
                  size="small"
                  variant="text"
                  color="error"
                  @click="cancelInvitation(invitation)"
                >
                  Cancel
                </v-btn>
              </template>
            </v-list-item>
          </v-list>
        </div>
      </v-card-text>
    </v-card>

    <!-- Invite User Dialog -->
    <v-dialog v-model="showInviteDialog" max-width="500">
      <v-card>
        <v-card-title>Send User Invitation</v-card-title>
        <v-card-text>
          <v-form ref="inviteForm" v-model="inviteFormValid">
            <v-text-field
              v-model="inviteData.email"
              label="Email Address"
              type="email"
              required
              :rules="[v => !!v || 'Email is required', v => /.+@.+/.test(v) || 'Invalid email']"
            />
            <v-text-field
              v-model="inviteData.first_name"
              label="First Name"
            />
            <v-text-field
              v-model="inviteData.last_name"
              label="Last Name"
            />
            <v-select
              v-model="inviteData.role"
              :items="availableRoles"
              label="Role"
              required
              :rules="[v => !!v || 'Role is required']"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showInviteDialog = false">Cancel</v-btn>
          <v-btn
            color="primary"
            :disabled="!inviteFormValid"
            @click="sendInvitation"
          >
            Send Invitation
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Edit User Dialog -->
    <v-dialog v-model="showEditDialog" max-width="500">
      <v-card>
        <v-card-title>Edit User Roles</v-card-title>
        <v-card-text>
          <div class="mb-4">
            <strong>User:</strong> {{ editingUser?.username }} ({{ editingUser?.email }})
          </div>
          <v-select
            v-model="selectedRoles"
            :items="availableRoles"
            label="Roles"
            multiple
            chips
            closable-chips
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showEditDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="updateUserRoles">Save Changes</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="showDeleteDialog" max-width="400">
      <v-card>
        <v-card-title>Delete User</v-card-title>
        <v-card-text>
          Are you sure you want to delete user <strong>{{ userToDelete?.username }}</strong>?
          This will deactivate their account and they will no longer be able to log in.
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="showDeleteDialog = false">Cancel</v-btn>
          <v-btn color="error" @click="deleteUser">Delete</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { authAPI } from '@/services/api'

const authStore = useAuthStore()

// Data
const users = ref([])
const invitations = ref([])
const availableRoles = ref(['Admin', 'Fleet Manager', 'Technician', 'Read-only'])
const loading = ref(false)

// Dialog states
const showInviteDialog = ref(false)
const showEditDialog = ref(false)
const showDeleteDialog = ref(false)

// Form data
const inviteFormValid = ref(false)
const inviteData = ref({
  email: '',
  first_name: '',
  last_name: '',
  role: 'Read-only'
})

const editingUser = ref(null)
const selectedRoles = ref([])
const userToDelete = ref(null)

// Table headers
const headers = [
  { title: 'Username', key: 'username' },
  { title: 'Email', key: 'email' },
  { title: 'Name', key: 'full_name' },
  { title: 'Roles', key: 'roles' },
  { title: 'Status', key: 'is_active' },
  { title: 'Joined', key: 'date_joined' },
  { title: 'Actions', key: 'actions', sortable: false }
]

// Computed
const currentUser = computed(() => authStore.currentUser)

// Methods
const getRoleColor = (role) => {
  const colors = {
    'Admin': 'red',
    'Fleet Manager': 'blue',
    'Technician': 'green',
    'Read-only': 'grey'
  }
  return colors[role] || 'default'
}

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString()
}

const loadUsers = async () => {
  loading.value = true
  try {
    const response = await authAPI.get('/auth/manage/users/list_users/')
    users.value = response.data.map(user => ({
      ...user,
      full_name: `${user.first_name} ${user.last_name}`.trim() || '-'
    }))
  } catch (error) {
    console.error('Failed to load users:', error)
  } finally {
    loading.value = false
  }
}

const loadInvitations = async () => {
  try {
    const response = await authAPI.get('/auth/manage/users/pending_invitations/')
    invitations.value = response.data
  } catch (error) {
    console.error('Failed to load invitations:', error)
  }
}

const sendInvitation = async () => {
  try {
    const response = await authAPI.post('/auth/manage/users/send_invitation/', inviteData.value)
    
    // Show success message
    alert(response.data.message)
    
    // Reset form
    inviteData.value = {
      email: '',
      first_name: '',
      last_name: '',
      role: 'Read-only'
    }
    showInviteDialog.value = false
    
    // Reload invitations
    loadInvitations()
  } catch (error) {
    alert(error.response?.data?.error || 'Failed to send invitation')
  }
}

const cancelInvitation = async (invitation) => {
  if (!confirm(`Cancel invitation to ${invitation.email}?`)) return
  
  try {
    await authAPI.post('/auth/manage/users/cancel_invitation/', {
      invitation_id: invitation.id
    })
    loadInvitations()
  } catch (error) {
    alert('Failed to cancel invitation')
  }
}

const editUser = (user) => {
  editingUser.value = user
  selectedRoles.value = [...user.roles]
  showEditDialog.value = true
}

const updateUserRoles = async () => {
  try {
    await authAPI.post(`/auth/manage/users/${editingUser.value.id}/update_roles/`, {
      roles: selectedRoles.value
    })
    
    showEditDialog.value = false
    loadUsers()
  } catch (error) {
    alert('Failed to update user roles')
  }
}

const toggleUserStatus = async (user) => {
  const action = user.is_active ? 'deactivate' : 'activate'
  const confirmMsg = user.is_active 
    ? `Deactivate user ${user.username}? They will no longer be able to log in.`
    : `Reactivate user ${user.username}?`
  
  if (!confirm(confirmMsg)) return
  
  try {
    await authAPI.post(`/auth/manage/users/${user.id}/${action}/`)
    loadUsers()
  } catch (error) {
    alert(`Failed to ${action} user`)
  }
}

const confirmDelete = (user) => {
  userToDelete.value = user
  showDeleteDialog.value = true
}

const deleteUser = async () => {
  try {
    await authAPI.delete(`/auth/manage/users/${userToDelete.value.id}/`)
    showDeleteDialog.value = false
    loadUsers()
  } catch (error) {
    alert(error.response?.data?.error || 'Failed to delete user')
  }
}

// Lifecycle
onMounted(() => {
  loadUsers()
  loadInvitations()
})
</script>

<style scoped>
.user-management-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.expired {
  opacity: 0.6;
}
</style>