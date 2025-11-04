<template>
  <div class="material-icons-wrapper">
    <!-- Icon Display Grid -->
    <div class="icon-search">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="Search icons..." 
        class="search-input"
      />
      <span class="material-icons search-icon">search</span>
    </div>
    
    <div class="icon-categories">
      <div class="category-tabs">
        <button 
          v-for="category in categories" 
          :key="category.name"
          :class="['category-tab', { active: selectedCategory === category.name }]"
          @click="selectedCategory = category.name"
        >
          <span class="material-icons">{{ category.icon }}</span>
          {{ category.name }}
        </button>
      </div>
    </div>
    
    <div class="icons-grid">
      <div 
        v-for="icon in filteredIcons" 
        :key="icon"
        :class="['icon-item', { selected: selectedIcon === icon }]"
        @click="selectIcon(icon)"
        :title="icon"
      >
        <span class="material-icons">{{ icon }}</span>
        <span class="icon-name">{{ icon }}</span>
      </div>
    </div>
    
    <!-- Selected Icon Display -->
    <div v-if="selectedIcon" class="selected-display">
      <h3>Selected Icon:</h3>
      <div class="selected-icon">
        <span class="material-icons">{{ selectedIcon }}</span>
      </div>
      <p>Icon name: <code>{{ selectedIcon }}</code></p>
      <button class="btn btn-primary" @click="copyIconName">
        <span class="material-icons">content_copy</span>
        Copy Icon Name
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'MaterialIcons',
  data() {
    return {
      searchQuery: '',
      selectedCategory: 'All',
      selectedIcon: null,
      
      categories: [
        { name: 'All', icon: 'apps' },
        { name: 'Actions', icon: 'touch_app' },
        { name: 'Communication', icon: 'chat' },
        { name: 'Content', icon: 'content_paste' },
        { name: 'Editor', icon: 'edit' },
        { name: 'File', icon: 'folder' },
        { name: 'Hardware', icon: 'memory' },
        { name: 'Image', icon: 'image' },
        { name: 'Maps', icon: 'place' },
        { name: 'Navigation', icon: 'navigate_next' },
        { name: 'Device', icon: 'smartphone' },
        { name: 'Media', icon: 'play_arrow' },
        { name: 'Notification', icon: 'notifications' },
        { name: 'Places', icon: 'home' },
        { name: 'Social', icon: 'people' },
        { name: 'Toggle', icon: 'toggle_on' }
      ],
      
      iconList: [
        // Actions and General
        "compare_arrows", "3d_rotation", "accessibility", "accessibility_new", "accessible",
        "accessible_forward", "account_balance", "account_balance_wallet", "account_box",
        "account_circle", "alarm", "alarm_add", "alarm_off", "alarm_on", "all_inbox",
        "all_out", "android", "announcement", "arrow_right_alt", "aspect_ratio",
        "assessment", "assignment", "assignment_ind", "assignment_late", "assignment_return",
        "assignment_returned", "assignment_turned_in", "autorenew", "backup",
        
        // Books and Content
        "book", "bookmark", "bookmark_border", "bookmarks", "bug_report", "build",
        "cached", "calendar_today", "calendar_view_day", "camera_enhance",
        "cancel_schedule_send", "card_giftcard", "card_membership", "card_travel",
        "change_history", "check_circle", "check_circle_outline", "chrome_reader_mode",
        "class", "code", "commute", "contact_support", "contactless", "copyright",
        
        // Payment and Finance
        "credit_card", "dashboard", "date_range", "delete", "delete_forever",
        "delete_outline", "description", "dns", "done", "done_all", "done_outline",
        "donut_large", "donut_small", "drag_indicator", "eco", "eject",
        "euro_symbol", "event", "event_seat", "exit_to_app", "explore",
        "explore_off", "extension", "face", "favorite", "favorite_border",
        
        // Feedback and Support
        "feedback", "find_in_page", "find_replace", "fingerprint", "flight_land",
        "flight_takeoff", "flip_to_back", "flip_to_front", "g_translate",
        "gavel", "get_app", "gif", "grade", "group_work", "help", "help_outline",
        "highlight_off", "history", "home", "horizontal_split", "hourglass_empty",
        "hourglass_full", "http", "https", "important_devices", "info", "input",
        
        // Interface Elements
        "invert_colors", "label", "label_important", "label_off", "language",
        "launch", "line_style", "line_weight", "list", "lock", "lock_open",
        "loyalty", "markunread_mailbox", "maximize", "minimize", "motorcycle",
        "note_add", "offline_bolt", "offline_pin", "opacity", "open_in_browser",
        "open_in_new", "open_with", "pageview", "pan_tool", "payment",
        
        // Permissions and Security
        "perm_camera_mic", "perm_contact_calendar", "perm_data_setting",
        "perm_device_information", "perm_identity", "perm_media", "perm_phone_msg",
        "perm_scan_wifi", "pets", "picture_in_picture", "picture_in_picture_alt",
        "play_for_work", "polymer", "power_settings_new", "pregnant_woman",
        "print", "query_builder", "question_answer", "receipt", "record_voice_over",
        "redeem", "remove_shopping_cart", "reorder", "report_problem",
        
        // System and Settings
        "restore", "restore_from_trash", "restore_page", "room", "rounded_corner",
        "rowing", "schedule", "search", "settings", "settings_applications",
        "settings_backup_restore", "settings_bluetooth", "settings_brightness",
        "settings_cell", "settings_ethernet", "settings_input_antenna",
        "settings_input_component", "settings_input_composite", "settings_input_hdmi",
        "settings_input_svideo", "settings_overscan", "settings_phone", "settings_power",
        "settings_remote", "settings_voice", "shop", "shop_two", "shopping_basket",
        
        // Communication
        "shopping_cart", "speaker_notes", "speaker_notes_off", "spellcheck",
        "stars", "store", "subject", "supervised_user_circle", "supervisor_account",
        "swap_horiz", "swap_horizontal_circle", "swap_vert", "swap_vertical_circle",
        "sync_alt", "system_update_alt", "tab", "tab_unselected", "text_rotate_up",
        "text_rotate_vertical", "text_rotation_angledown", "text_rotation_angleup",
        "text_rotation_down", "text_rotation_none", "theaters", "thumb_down",
        "thumb_up", "thumbs_up_down",
        
        // Trending and Analytics
        "timeline", "toc", "today", "toll", "touch_app", "track_changes",
        "translate", "trending_down", "trending_flat", "trending_up", "turned_in",
        "turned_in_not", "update", "verified_user", "vertical_split", "view_agenda",
        "view_array", "view_carousel", "view_column", "view_day", "vue_headline",
        "view_list", "view_module", "view_quilt", "view_stream", "view_week",
        "visibility", "visibility_off", "voice_over_off", "watch_later", "work",
        "work_off", "work_outline", "youtube_searched_for", "zoom_in", "zoom_out",
        
        // Alerts and Warnings
        "add_alert", "error", "error_outline", "notification_important", "warning",
        "4k", "add_to_queue", "airplay", "album", "art_track", "av_timer",
        "branding_watermark", "call_to_action", "closed_caption", "control_camera",
        "equalizer", "explicit", "fast_forward", "fast_rewind", "featured_play_list",
        "featured_video", "fiber_dvr", "fiber_manual_record", "fiber_new",
        "fiber_pin", "fiber_smart_record",
        
        // Media Controls
        "forward_10", "forward_30", "forward_5", "games", "hd", "hearing",
        "high_quality", "library_add", "library_add_check", "library_books",
        "library_music", "loop", "mic", "mic_none", "mic_off", "missed_video_call",
        "movie", "music_video", "new_releases", "not_interested", "note", "pause",
        "pause_circle_filled", "pause_circle_outline", "play_arrow",
        "play_circle_filled", "play_circle_outline", "playlist_add",
        "playlist_add_check", "playlist_play", "queue", "queue_music",
        "queue_play_next", "radio", "recent_actors", "remove_from_queue",
        "repeat", "repeat_one", "replay", "replay_10", "replay_30", "replay_5",
        "shuffle", "skip_next", "skip_previous", "slow_motion_video", "snooze",
        
        // Device and Hardware
        "sort_by_alpha", "speed", "stop", "subscriptions", "subtitles",
        "surround_sound", "video_call", "video_label", "video_library",
        "videocam", "videocam_off", "volume_down", "volume_mute", "volume_off",
        "volume_up", "web", "web_asset", "call_made", "add_ic_call",
        "alternate_email", "business", "call", "call_end", "call_merge",
        "call_missed", "call_missed_outgoing", "call_received", "call_split",
        
        // Communication
        "cancel_presentation", "chat", "chat_bubble", "chat_bubble_outline",
        "clear_all", "comment", "contact_mail", "contact_phone", "contacts",
        "desktop_access_disabled", "dialer_sip", "dialpad", "domain_disabled",
        "duo", "email", "forum", "import_contacts", "import_export",
        "invert_colors_off", "list_alt", "live_help", "location_off",
        "location_on", "mail_outline", "message", "mobile_screen_share",
        "no_sim", "pause_presentation", "person_add_disabled", "phone",
        "phone_disabled", "phone_enabled", "phonelink_erase", "phonelink_lock",
        "phonelink_ring", "phonelink_setup", "portable_wifi_off",
        
        // Apps and Files
        "present_to_all", "print_disabled", "ring_volume", "rss_feed",
        "screen_share", "sentiment_satisfied_alt", "speaker_phone",
        "stay_current_landscape", "stay_current_portrait",
        "stay_primary_landscape", "stay_primary_portrait", "stop_screen_share",
        "swap_calls", "textsms", "unsubscribe", "voicemail", "vpn_key",
        "add", "add_box", "add_circle", "add_circle_outline", "amp_stories",
        "archive", "backspace", "ballot", "block", "clear", "create",
        
        // File Management
        "delete_sweep", "drafts", "dynamic_feed", "file_copy", "filter_list",
        "flag", "font_download", "forward", "gesture", "how_to_reg",
        "how_to_vote", "inbox", "link", "link_off", "low_priority",
        "mail", "markunread", "move_to_inbox", "next_week", "outlined_flag",
        "policy", "redo", "remove", "remove_circle", "remove_circle_outline",
        "reply", "reply_all", "report", "report_off", "save", "save_alt",
        
        // Navigation
        "select_all", "send", "sort", "square_foot", "text_format",
        "unarchive", "undo", "waves", "weekend", "where_to_vote",
        "access_alarm", "access_alarms", "access_time", "add_alarm",
        "add_to_home_screen", "airplanemode_active", "airplanemode_inactive",
        "battery_alert", "battery_charging_full", "battery_full", "battery_std",
        "battery_unknown", "bluetooth", "bluetooth_connected", "bluetooth_disabled",
        "bluetooth_searching", "brightness_auto", "brightness_high",
        "brightness_low", "brightness_medium", "data_usage", "developer_mode",
        "devices", "dvr", "gps_fixed", "gps_not_fixed", "gps_off",
        
        // Smart Toys and Gaming Icons (Perfect for Minions!)
        "smart_toy", "toys", "videogame_asset", "extension", "memory",
        "science", "psychology", "engineering", "auto_fix_high", "build",
        "construction", "brush", "palette", "color_lens", "lightbulb",
        "lightbulb_outline", "eco", "nature", "pets", "psychology",
        "auto_awesome", "auto_fix_high", "psychology", "science",
        "biotech", "calculate", "schema", "settings_cell", "hive",
        
        // Specific Minion-related Icons
        "bug_report", "construction", "engineering", "precision_manufacturing",
        "schema", "hub", "workspace_premium", "admin_panel_settings",
        "shield", "shield_outline", "security", "verified_user",
        "check_circle", "task", "assignment", "assignment_turned_in",
        "task_alt", "pending_actions", "update", "sync", "sync_alt",
        "refresh", "restart_alt", "system_update", "fitness_center",
        "trending_up", "grade", "star", "star_border", "star_rate",
        "auto_awesome", "auto_fix_high", "psychology", "science"
      ]
    }
  },
  computed: {
    filteredIcons() {
      let icons = this.iconList

      // Search filter
      if (this.searchQuery) {
        icons = icons.filter(icon => 
          icon.toLowerCase().includes(this.searchQuery.toLowerCase())
        )
      }

      // Category filter
      if (this.selectedCategory !== 'All') {
        icons = this.getIconsByCategory()
      }

      return icons
    },
    
    getIconsByCategory() {
      const categoryMap = {
        'Actions': ['touch_app', 'compare_arrows', 'build', 'create', 'edit', 'delete', 'save', 'refresh'],
        'Communication': ['chat', 'message', 'email', 'call', 'forum', 'contact_support', 'voicemail'],
        'Content': ['content_paste', 'file_copy', 'description', 'note_add', 'text_format'],
        'Editor': ['edit', 'format_color_reset', 'format_bold', 'format_italic', 'code'],
        'File': ['folder', 'folder_open', 'insert_drive_file', 'cloud_upload', 'cloud_download'],
        'Hardware': ['memory', 'storage', 'memory', 'devices', 'smartphone', 'laptop'],
        'Image': ['image', 'photo_camera', 'palette', 'brush', 'color_lens'],
        'Maps': ['place', 'location_on', 'navigation', 'directions', 'map'],
        'Navigation': ['navigate_next', 'arrow_back', 'arrow_forward', 'menu', 'apps'],
        'Device': ['smartphone', 'laptop', 'tablet', 'desktop_windows', 'watch'],
        'Media': ['play_arrow', 'pause', 'volume_up', 'mic', 'videocam'],
        'Notification': ['notifications', 'notifications_active', 'add_alert', 'warning'],
        'Places': ['home', 'business', 'school', 'work', 'apartment'],
        'Social': ['people', 'person', 'group', 'person_add', 'account_circle'],
        'Toggle': ['toggle_on', 'toggle_off', 'check_circle', 'radio_button_checked']
      }
      
      return categoryMap[this.selectedCategory] || this.iconList
    }
  },
  methods: {
    selectIcon(icon) {
      this.selectedIcon = icon
      this.$emit('icon-selected', icon)
    },
    
    copyIconName() {
      navigator.clipboard.writeText(this.selectedIcon)
      this.$emit('icon-copied', this.selectedIcon)
    }
  }
}
</script>

<style scoped>
.material-icons-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.icon-search {
  position: relative;
  margin-bottom: 2rem;
}

.search-input {
  width: 100%;
  padding: 1rem 3rem 1rem 1rem;
  border: 2px solid var(--border);
  border-radius: 12px;
  background: var(--background-primary);
  font-size: 1rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.search-icon {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 1.25rem;
}

.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 2rem;
}

.category-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: 2px solid var(--border);
  border-radius: 25px;
  background: var(--background-primary);
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
}

.category-tab:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
}

.category-tab.active {
  border-color: var(--primary);
  background: var(--primary-light);
  color: var(--primary);
}

.icons-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1.5rem 1rem;
  border: 2px solid var(--border);
  border-radius: 12px;
  background:_var(--background-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.icon-item:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}

.icon-item.selected {
  border-color: var(--primary);
  background: var(--primary-light);
}

.icon-item .material-icons {
  font-size: 2.5rem;
  color: var(--text-primary);
  margin: 0;
}

.icon-item.selected .material-icons {
  color: var(--primary);
}

.icon-name {
  font-size: 0.8rem;
  color: var(--text-secondary);
  word-break: break-word;
  max-width: 100%;
}

.icon-item.selected .icon-name {
  color: var(--primary);
  font-weight: 600;
}

.selected-display {
  padding: 2rem;
  border: 2px solid var(--primary);
  border-radius: 12px;
  background: var(--primary-light);
  text-align: center;
  margin-top: 2rem;
}

.selected-display h3 {
  color: var(--primary);
  margin-bottom: 1rem;
}

.selected-icon {
  margin: 1rem 0;
}

.selected-icon .material-icons {
  font-size: 4rem;
  color: var(--primary);
  margin: 0;
}

.selected-display p {
  color: var(--text-primary);
  margin: 1rem 0;
}

.selected-display code {
  background: var(--background-primary);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  color: var(--primary);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  background: var(--primary);
  color: white;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.btn:hover {
  background: var(--primary-dark);
  transform: translateY(-2px);
}

.btn-primary {
  background: var(--primary);
}

/* Material Icons Base Styling */
.material-icons {
  font-family: 'Material Icons';
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

/* Neumorphism Styling for Large Icons */
.material-icons.neumorphic {
  font-size: 3.5rem;
  color: var(--background-tertiary, #e0e5ec);
  filter: drop-shadow(3px 3px 2px #a3b1c6) drop-shadow(-3px -3px 2px #ffffff);
  margin: 1rem;
  transition: all 0.3s ease;
}

.material-icons.neumorphic:hover {
  cursor: pointer;
  filter: drop-shadow(-3px -3px 1px #a3b1c6) drop-shadow(3px 3px 1px #ffffff);
}

/* Responsive Design */
@media (max-width: 768px) {
  .icons-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  }
  
  .category-tabs {
    justify-content: center;
  }
  
  .category-tab {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
  }
  
  .material-icons-wrapper {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .icons-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
  
  .icon-item {
    padding: 1rem 0.5rem;
  }
  
  .icon-item .material-icons {
    font-size: 2rem;
  }
}
</style>
