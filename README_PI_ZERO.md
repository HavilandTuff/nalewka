# Nalewka on Raspberry Pi Zero

This directory contains files specifically optimized for deploying Nalewka on a Raspberry Pi Zero.

## Files

- `requirements-pi-zero.txt` - Minimal dependencies for Pi Zero
- `deploy-pi-zero.sh` - Automated deployment script
- `nalewka.service` - Systemd service file for automatic startup
- `run_pi_zero.py` - Optimized startup script for Pi Zero
- `DEPLOY_PI_ZERO.md` - Detailed deployment instructions

## Quick Start

1. Copy all files to your Pi Zero
2. Run the deployment script:
   ```
   chmod +x deploy-pi-zero.sh
   ./deploy-pi-zero.sh
   ```
3. Start the application:
   ```
   flask run --host=0.0.0.0 --port=5000
   ```

For detailed instructions, see `DEPLOY_PI_ZERO.md`.
