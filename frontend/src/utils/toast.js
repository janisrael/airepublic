/**
 * Toast Notification Service
 * Provides consistent toast notifications across the application
 */

class ToastService {
  constructor() {
    this.container = null
    this.init()
  }

  init() {
    // Create toast container if it doesn't exist
    this.container = document.getElementById('toast-container')
    if (!this.container) {
      this.container = document.createElement('div')
      this.container.id = 'toast-container'
      this.container.className = 'toast-container'
      this.container.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        pointer-events: none;
      `
      
      // Add CSS animations if not already added
      if (!document.getElementById('toast-animations')) {
        const style = document.createElement('style')
        style.id = 'toast-animations'
        style.textContent = `
          @keyframes slideInRight {
            from {
              transform: translateX(100%);
              opacity: 0;
            }
            to {
              transform: translateX(0);
              opacity: 1;
            }
          }
          
          @keyframes slideOutRight {
            from {
              transform: translateX(0);
              opacity: 1;
            }
            to {
              transform: translateX(100%);
              opacity: 0;
            }
          }
          
          .toast-container .toast {
            animation: slideInRight 0.3s ease-out;
          }
          
          .toast-container .toast.fade {
            animation: slideOutRight 0.3s ease-in;
          }
        `
        document.head.appendChild(style)
      }
      document.body.appendChild(this.container)
    }
  }

  show(message, type = 'info', duration = 2000) {
    const toastId = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    
    // Toast configuration
    const config = {
      success: {
        icon: 'check_circle',
        iconColor: '#4caf50',
        bgClass: 'bg-success',
        borderColor: '#4caf50'
      },
      error: {
        icon: 'error',
        iconColor: '#f44336',
        bgClass: 'bg-danger',
        borderColor: '#f44336'
      },
      warning: {
        icon: 'warning',
        iconColor: '#ff9800',
        bgClass: 'bg-warning',
        borderColor: '#ff9800'
      },
      info: {
        icon: 'info',
        iconColor: '#2196f3',
        bgClass: 'bg-info',
        borderColor: '#2196f3'
      }
    }

    const toastConfig = config[type] || config.info

    // Create toast HTML
    const toastHTML = `
      <div id="${toastId}" class="toast fade show shadow-inset" role="alert" aria-live="assertive" aria-atomic="true" style="pointer-events: auto; margin-bottom: 8px; max-width: 400px;">
        <div class="toast-header text-dark" style="border-bottom: 2px solid ${toastConfig.borderColor};">
          <span class="material-icons-round mr-2" style="color: ${toastConfig.iconColor}; font-size: 20px;">
            ${toastConfig.icon}
          </span>
          <strong class="mr-auto">${this.getTitle(type)}</strong>
          <button type="button" class="ml-2 mb-1 close" onclick="document.getElementById('${toastId}').remove()" aria-label="Close">
            <span aria-hidden="true" style="font-size: 18px;">×</span>
          </button>
        </div>
        <div class="toast-body text-dark">
          ${message}
        </div>
      </div>
    `

    // Add toast to container
    this.container.insertAdjacentHTML('beforeend', toastHTML)

    // Auto remove after duration
    setTimeout(() => {
      const toast = document.getElementById(toastId)
      if (toast) {
        toast.classList.remove('show')
        toast.classList.add('fade')
        setTimeout(() => {
          if (toast.parentElement) {
            toast.remove()
          }
        }, 150)
      }
    }, duration)
  }

  getTitle(type) {
    const titles = {
      success: 'Success',
      error: 'Error',
      warning: 'Warning',
      info: 'Info'
    }
    return titles[type] || 'Notification'
  }

  // Convenience methods
  success(message, duration = 2000) {
    this.show(message, 'success', duration)
  }

  error(message, duration = 3000) {
    this.show(message, 'error', duration)
  }

  warning(message, duration = 2500) {
    this.show(message, 'warning', duration)
  }

  info(message, duration = 2000) {
    this.show(message, 'info', duration)
  }
}

// Create global instance
const toast = new ToastService()

// Export for use in components
export default toast

// Also make it available globally
window.toast = toast
