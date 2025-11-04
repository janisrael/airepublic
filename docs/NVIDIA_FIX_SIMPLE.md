# Simple NVIDIA Driver Fix

## Current Situation

✅ **Done:**
- nouveau blacklisted (`/etc/modprobe.d/blacklist-nouveau.conf`)
- NVIDIA drivers installed (akmod-nvidia-580.95.05)

❌ **Problem:**
- Running kernel: `6.17.4-200.fc42.x86_64`
- Available kernel-devel: `6.14.0-63` and `6.17.5-200`
- **No kernel-devel for 6.17.4** → Can't build modules

---

## Simplest Solution: Reboot to Matching Kernel

You have `kernel-devel-6.14.0-63` installed. Reboot to kernel `6.14.0-63`:

```bash
# Option 1: Reboot and select 6.14.0 kernel at GRUB menu
sudo reboot

# At GRUB menu, select: "Fedora Linux (6.14.0-63.fc42.x86_64)"
```

Then after boot:
```bash
# Build NVIDIA modules
sudo akmods --force

# Reboot again
sudo reboot
```

---

## Alternative: Use 6.17.5 Kernel

If you want to use the newer kernel:

```bash
# Install 6.17.5 kernel (if not already installed)
sudo dnf install kernel-6.17.5-200.fc42.x86_64

# Reboot to 6.17.5
sudo reboot
```

Then build modules:
```bash
sudo akmods --force
sudo reboot
```

---

## Quick Fix Script

```bash
# 1. Rebuild for 6.14.0 kernel (has matching devel)
sudo akmods --kernels 6.14.0-63.fc42.x86_64 --force

# 2. Reboot to that kernel
sudo reboot
```

After reboot, check:
```bash
nvidia-smi
```

---

## Status

- ✅ nouveau blacklisted (will prevent loading on reboot)
- ⏳ Need to build modules for a kernel with matching kernel-devel
- ⏳ Need to reboot to that kernel

**Recommendation:** Reboot to kernel `6.14.0-63` since it has matching kernel-devel installed.



