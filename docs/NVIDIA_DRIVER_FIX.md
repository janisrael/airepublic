# NVIDIA Driver Fix for Multi-Monitor Support

## Status: ✅ Partially Fixed

### Completed:
1. ✅ **Blacklisted nouveau** - `/etc/modprobe.d/blacklist-nouveau.conf` created
2. ✅ **NVIDIA drivers installed** - akmod-nvidia-580.95.05

### Issue:
- Kernel version mismatch: Running `6.17.4` but kernel-devel is for `6.14.0`
- NVIDIA modules cannot be built until kernel-devel matches current kernel

---

## Solution Options

### Option 1: Install Matching Kernel-Dev (Recommended)

```bash
# Install kernel-devel for current kernel
sudo dnf install kernel-devel-$(uname -r)

# If not available, update system and reboot to newer kernel with matching devel
sudo dnf update kernel kernel-devel
sudo reboot
```

### Option 2: Reboot to Kernel with Matching Kernel-Dev

If `kernel-devel-6.14.0` is installed:
```bash
# Reboot and select kernel 6.14.0 at GRUB menu
sudo reboot
```

### Option 3: Build Modules After Kernel-Dev Install

Once kernel-devel matches:
```bash
# Rebuild NVIDIA modules
sudo akmods --force

# This may take 5-10 minutes
```

---

## Verification After Reboot

```bash
# Check NVIDIA driver is loaded
nvidia-smi

# Should show GPU info if working
# If shows error, check:
lsmod | grep nvidia
dmesg | grep -i nvidia | tail -20
```

---

## Current Configuration

**Blacklist File:** `/etc/modprobe.d/blacklist-nouveau.conf`
```
# Blacklist nouveau to allow NVIDIA proprietary driver
blacklist nouveau
options nouveau modeset=0
```

This will prevent nouveau from loading on next boot.

---

## Next Steps

1. **Install matching kernel-devel OR reboot**
2. **Rebuild NVIDIA modules** (if needed): `sudo akmods --force`
3. **Reboot** to load NVIDIA drivers
4. **Verify**: `nvidia-smi` should work after reboot

---

**Note:** Multi-monitor will work once NVIDIA drivers are loaded properly. The blacklist ensures nouveau doesn't interfere.



