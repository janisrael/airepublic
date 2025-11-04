/**
 * Material Icons Utility Library
 * Comprehensive icon management for AI Republic project
 * Based on Google Material Icons: https://fonts.google.com/icons
 */

// Material Icons categorized for easy access
export const iconCategories = {
  // General Actions
  actions: [
    'compare_arrows', '3d_rotation', 'accessibility', 'accessibility_new',
    'accessible', 'accessible_forward', 'account_balance', 'account_balance_wallet',
    'account_box', 'account_circle', 'alarm', 'alarm_add', 'alarm_off', 'alarm_on',
    'all_inbox', 'all_out', 'android', 'announcement', 'arrow_right_alt',
    'aspect_ratio', 'assessment', 'assignment', 'assignment_ind',
    'assignment_late', 'assignment_return', 'assignment_returned',
    'assignment_turned_in', 'autorenew', 'backup'
  ],

  // Communication
  communication: [
    'chat', 'chat_bubble', 'chat_bubble_outline', 'message', 'email',
    'call', 'forum', 'contact_support', 'voicemail', 'sms', 'videocam',
    'person', 'person_add', 'group', 'account_circle'
  ],

  // Development & Code
  development: [
    'code', 'build', 'bug_report', 'construction', 'engineering',
    'memory', 'storage', 'devices', 'smartphone', 'computer',
    'developer_board', 'settings', 'api', 'web', 'database'
  ],

  // Files & Content
  files: [
    'folder', 'folder_open', 'insert_drive_file', 'description', 'note',
    'content_paste', 'file_copy', 'save', 'download', 'upload'
  ],

  // UI & Interface
  interface: [
    'visibility', 'visibility_off', 'settings', 'menu', 'apps',
    'dashboard', 'home', 'navigation', 'arrow_back', 'arrow_forward',
    'close', 'check', 'cancel', 'refresh'
  ],

  // Minion-specific Icons
  minions: [
    'smart_toy', 'toys', 'videogame_asset', 'extension', 'memory',
    'science', 'psychology', 'engineering', 'auto_fix_high', 'build',
    'construction', 'brush', 'palette', 'color_lens', 'lightbulb',
    'lightbulb_outline', 'eco', 'nature', 'pets', 'psychology',
    'auto_awesome', 'auto_fix_high', 'biotech', 'calculate', 'schema',
    'precision_manufacturing', 'hub', 'workspace_premium',
    'admin_panel_settings', 'shield', 'security', 'verified_user',
    'task', 'assignment', 'task_alt', 'pending_actions', 'update',
    'sync', 'sync_alt', 'refresh', 'restart_alt', 'system_update',
    'fitness_center', 'trending_up', 'grade', 'star', 'star_border'
  ],

  // Media & Entertainment
  media: [
    'play_arrow', 'pause', 'stop', 'skip_next', 'skip_previous',
    'volume_up', 'volume_down', 'volume_mute', 'volume_off',
    'mic', 'mic_off', 'videocam', 'videocam_off', 'camera',
    'camera_alt', 'image', 'photo_camera', 'movie', 'music_note'
  ],

  // Security & Safety
  security: [
    'lock', 'lock_open', 'security', 'shield', 'verified_user',
    'admin_panel_settings', 'key', 'fingerprint', 'vpn_key',
    'report_problem', 'warning', 'error', 'cancel'
  ],

  // Analytics & Data
  analytics: [
    'analytics', 'trending_up', 'trending_down', 'trending_flat',
    'bar_chart', 'pie_chart', 'timeline', 'assessment',
    'donut_small', 'donut_large', 'insert_chart'
  ],

  // Education & Learning
  education: [
    'school', 'book', 'bookmark', 'assignment', 'assignment_turned_in',
    'grade', 'class', 'quiz', 'auto_awesome', 'psychology'
  ],

  // Shopping & Commerce
  shopping: [
    'shop', 'shopping_cart', 'add_shopping_cart', 'remove_shopping_cart',
    'card_membership', 'card_travel', 'store', 'payment', 'credit_card'
  ],

  // Transportation
  transport: [
    'directions_car', 'directions_bus', 'directions_train', 'directions_walk',
    'directions_bike', 'flight', 'train', 'bus', 'subway', 'taxi'
  ],

  // Healthcare & Medical
  health: [
    'local_hospital', 'healing', 'medical_services', 'medical_information',
    'health_and_safety', 'medication', 'fitness_center'
  ],

  // Weather & Environment
  weather: [
    'sunnyt', 'cloud', 'rain', 'snow', 'storm', 'nature', 'eco',
    'energy_savings_leaf', 'recycling', 'water_drop'
  ]
}

// Common icon mappings for different contexts
export const contextualIcons = {
  // User Actions
  create: 'add_circle',
  edit: 'edit',
  save: 'save',
  delete: 'delete',
  cancel: 'cancel',
  confirm: 'check_circle',
  close: 'close',
  refresh: 'refresh',
  
  // Navigation
  back: 'arrow_back',
  forward: 'arrow_forward',
  up: 'keyboard_arrow_up',
  down: 'keyboard_arrow_down',
  left: 'keyboard_arrow_left',
  right: 'keyboard_arrow_right',
  menu: 'menu',
  home: 'home',
  
  // Status
  loading: 'hourglass_empty',
  success: 'check_circle',
  error: 'error',
  warning: 'warning',
  info: 'info',
  help: 'help_outline',
  
  // Common UI Elements
  search: 'search',
  filter: 'filter_list',
  sort: 'sort',
  settings: 'settings',
  more: 'more_vert',
  
  // Minion States
  minionIdle: 'smart_toy',
  minionActive: 'psychology',
  minionTraining: 'fitness_center',
  minionLearning: 'school',
  minionWorking: 'engineering',
  minionDebugging: 'bug_report',
  minionCreating: 'construction',
  
  // Avatar Options (replacing emojis)
  robot: 'smart_toy',
  brain: 'psychology',
  lightning: 'flash_on',
  star: 'star',
  rock: 'dynamic_feed',
  diamond: 'workspace_premium',
  rocket: 'rocket_launch',
  target: 'gps_fixed'
}

// Minion Spirit Icons (replacing emoji representations)
export const spiritIcons = {
  Builder: 'construction',
  Debugger: 'bug_report',
  Analyst: 'analytics',
  Security: 'security',
  Checker: 'check_circle_outline',
  Writer: 'edit',
  Creative: 'auto_awesome',
  Translator: 'translate',
  Communicator: 'chat',
  Educator: 'school',
  DevOps: 'settings',
  Connector: 'hub',
  Designer: 'palette',
  Researcher: 'search',
  Mathematician: 'calculate',
  Consultant: 'support_agent',
  Scheduler: 'schedule'
}

// Get icon by category and filter
export function getIconsByCategory(category, filter = '') {
  const icons = iconCategories[category] || []
  if (!filter) return icons
  return icons.filter(icon => icon.toLowerCase().includes(filter.toLowerCase()))
}

// Get contextual icon by key
export function getContextualIcon(key) {
  return contextualIcons[key] || 'help_outline'
}

// Get spirit icon by spirit name
export function getSpiritIcon(spiritName) {
  return spiritIcons[spiritName] || 'help_outline'
}

// Get avatar icon (replacing emoji options)
export function getAvatarIcon(avatarKey) {
  const avatarMap = {
    'robot': 'smart_toy',
    'brain': 'psychology', 
    'lightning': 'flash_on',
    'star': 'star',
    'fire': 'flare',
    'diamond': 'workspace_premium',
    'rocket': 'rocket_launch',
    'target': 'gps_fixed'
  }
  return avatarMap[avatarKey] || 'smart_toy'
}

// Validate if icon exists in our library
export function isValidIcon(iconName) {
  const allIcons = Object.values(iconCategories).flat()
  return allIcons.includes(iconName)
}

// Get random icon from category
export function getRandomIcon(category) {
  const icons = iconCategories[category] || iconCategories.minions
  return icons[Math.floor(Math.random() * icons.length)]
}

// Export all icons as flat array for component usage
export const allIcons = Object.values(iconCategories).flat()

// Material Icons base CSS (neumorphism styling)
export const iconCSS = `
.material-icons, .material-icons-round {
  font-family: 'Material Icons Round';
  font-weight: normal;
  font-style: normal;
  font-size: 24px;
  line-height: 1;
  letter-spacing: normal;
  text-transform: none;
  display: inline-block;
  white-space: nowrap;
  word-wrap: normal;
  direction: ltr;
  -webkit-font-feature-settings: 'liga';
  -webkit-font-smoothing: antialiased;
}

.material-icons.neumorphic, .material-icons-round.neumorphic {
  font-size: 3.5rem;
  color: var(--background-tertiary, #e0e5ec);
  
  filter: drop-shadow(3px 3px 2px #a3b1c6) drop-shadow(-3px -3px 2px #ffffff);
  margin: 1rem;
  transition: all 0.3s ease;
}

// .material-icons.neumorphic:hover, .material-icons-round.neumorphic:hover {
//   cursor: pointer;
//   filter: drop-shadow(-3px -3px 1px #a3b1c6) drop-shadow(3px 3px 1px #ffffff);
// }

.material-icons.primary {
  color: var(--primary);
}

.material-icons.secondary {
  color: var(--secondary);
}

.material-icons.success {
  color: var(--success);
}

.material-icons.warning {
  color: var(--warning);
}

.material-icons.error {
  color: var(--error);
}
`

export default {
  iconCategories,
  contextualIcons,
  spiritIcons,
  getIconsByCategory,
  getContextualIcon,
  getSpiritIcon,
  getAvatarIcon,
  isValidIcon,
  getRandomIcon,
  allIcons,
  iconCSS
}
