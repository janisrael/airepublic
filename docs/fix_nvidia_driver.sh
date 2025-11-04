#!/bin/bash
# Fix NVIDIA Driver for Multi-Monitor Support
# Safe script - only modifies what's needed

set -e

echo "🔧 Fixing NVIDIA Driver for Multi-Monitor Support"
echo "=================================================="
echo ""

# Check if running as root for some operations
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Some operations require sudo"
    echo ""
fi

echo "Step 1: Blacklist nouveau driver"
echo "---------------------------------"
if [ ! -f /etc/modprobe.d/blacklist-nouveau.conf ]; then
    echo "Creating blacklist file..."
    sudo bash -c 'cat > /etc/modprobe.d/blacklist-nouveau.conf << EOF
# Blacklist nouveau to allow NVIDIA proprietary driver
blacklist nouveau
options nouveau modeset=0
EOF'
    echo "✅ Created blacklist file"
else
    echo "✅ Blacklist file already exists"
fi

echo ""
echo "Step 2: Rebuild NVIDIA kernel modules"
echo "--------------------------------------"
echo "Building NVIDIA modules for kernel $(uname -r)..."
sudo akmods --force

echo ""
echo "Step 3: Check module build status"
echo "-----------------------------------"
if find /lib/modules/$(uname -r)/extra/weak-updates/akmods/nvidia* 2>/dev/null | grep -q nvidia; then
    echo "✅ NVIDIA modules found"
else
    echo "⏳ Modules may still be building..."
    echo "   This can take a few minutes"
fi

echo ""
echo "Step 4: Unload nouveau (if possible without breaking display)"
echo "--------------------------------------------------------------"
if lsmod | grep -q nouveau; then
    echo "⚠️  nouveau is currently loaded"
    echo "   You may need to reboot for changes to take effect"
    echo "   Or restart your display manager manually"
else
    echo "✅ nouveau not loaded"
fi

echo ""
echo "=================================================="
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Reboot: sudo reboot"
echo "   2. After reboot, verify: nvidia-smi"
echo "   3. If still not working, check: dmesg | grep nvidia"
echo ""
echo "💡 To manually unload nouveau (if X server allows):"
echo "   sudo modprobe -r nouveau"
echo "   sudo modprobe nvidia"
echo ""



