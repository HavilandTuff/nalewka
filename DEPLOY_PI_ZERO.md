# Deploying Nalewka on Raspberry Pi Zero

This guide explains how to deploy the Nalewka application on a Raspberry Pi Zero.

## Prerequisites

1. Raspberry Pi Zero (W or WH recommended for WiFi connectivity)
2. MicroSD card (8GB or larger recommended)
3. Power supply for Pi Zero
4. WiFi network credentials (if using Pi Zero W/WH)

## Setup Instructions

### 1. Prepare the Raspberry Pi

1. Install Raspberry Pi OS Lite on your microSD card using the [Raspberry Pi Imager](https://www.raspberrypi.org/software/)
2. Enable SSH by creating an empty file named `ssh` in the boot partition
3. If using WiFi, create a `wpa_supplicant.conf` file in the boot partition with your network credentials:
```
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="YourNetworkName"
    psk="YourPassword"
}
```

### 2. First Boot and Configuration

1. Insert the microSD card and power on your Pi Zero
2. Connect via SSH (default username: `pi`, password: `raspberry`):
   ```
   ssh pi@raspberrypi.local
   ```
3. Run the initial setup:
   ```
   sudo raspi-config
   ```
   - Change password
   - Set hostname (optional)
   - Configure WiFi country (if needed)
   - Expand filesystem
   - Reboot when prompted

### 3. Deploy Nalewka

1. Copy the Nalewka files to your Pi Zero:
   ```
   scp -r /path/to/nalewka/* pi@raspberrypi.local:~/nalewka/
   ```

2. Make the deployment script executable and run it:
   ```
   chmod +x ~/nalewka/deploy-pi-zero.sh
   ~/nalewka/deploy-pi-zero.sh
   ```

### 4. Run the Application

You can run the application manually:
```
cd ~/nalewka
source venv/bin/activate
flask run --host=0.0.0.0 --port=5000
```

### 5. Run as a Service (Optional)

To run the application automatically on boot:

1. Copy the service file to the systemd directory:
   ```
   sudo cp ~/nalewka/nalewka.service /etc/systemd/system/
   ```

2. Enable and start the service:
   ```
   sudo systemctl enable nalewka.service
   sudo systemctl start nalewka.service
   ```

3. Check the service status:
   ```
   sudo systemctl status nalewka.service
   ```

## Performance Considerations for Pi Zero

1. The Pi Zero has limited resources (single-core CPU, 512MB RAM)
2. We use SQLite instead of PostgreSQL for better performance on resource-constrained devices
3. We use Flask's built-in server instead of Gunicorn to reduce memory usage
4. Database files are stored in the application directory for simplicity

## Accessing the Application

Once running, access the application at:
```
http://[PI_ZERO_IP]:5000
```

Replace `[PI_ZERO_IP]` with your Pi Zero's IP address. You can find it with:
```
ip addr show
```

## Default Credentials (if using sample data)

Username: `admin`
Password: `password123`

## Updating the Application

To update the application:

1. Stop the service (if running):
   ```
   sudo systemctl stop nalewka.service
   ```

2. Pull the latest code:
   ```
   cd ~/nalewka
   git pull
   ```

3. Update dependencies if needed:
   ```
   source venv/bin/activate
   pip install -r requirements-pi-zero.txt
   ```

4. Run database migrations:
   ```
   flask db upgrade
   ```

5. Restart the service:
   ```
   sudo systemctl start nalewka.service
   ```
