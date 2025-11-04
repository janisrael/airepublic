// Test the toast system
console.log('Testing toast notifications...')

// Test different toast types
setTimeout(() => {
  if (window.toast) {
    window.toast.success('✅ Toast system is working!')
  }
}, 1000)

setTimeout(() => {
  if (window.toast) {
    window.toast.info('ℹ️ This is an info message')
  }
}, 2000)

setTimeout(() => {
  if (window.toast) {
    window.toast.warning('⚠️ This is a warning message')
  }
}, 3000)

setTimeout(() => {
  if (window.toast) {
    window.toast.error('❌ This is an error message')
  }
}, 4000)
