# MMM-UniAssignments

MagicMirror² module to display university assignments from Todoist with Flask backend.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

- 📚 **Todoist Integration** - Sync assignments from Todoist project
- 📅 **Week View** - Display assignments for next 7 days
- 📊 **Module Overview** - Progress tracking per subject
- 🔄 **Auto-Sync** - Updates every 5 minutes
- 🎨 **Modern UI** - Clean, minimalist dark design
- ⚡ **Flask Backend** - Python API with JSON caching
- 🚀 **Systemd Service** - Automatic backend startup

## 🚀 Quick Start

```bash
cd ~/MagicMirror/modules
git clone https://github.com/FreakyLetsFail/MMM-UniAssignments.git
cd MMM-UniAssignments
./install.sh

# Configure Todoist token
nano backend/.env
# Add: TODOIST_API_TOKEN=your_token_here

# Setup systemd service
sudo ./setup-systemd.sh
```

## ⚙️ Configuration

Add to your `config/config.js`:

```javascript
{
  module: 'MMM-UniAssignments',
  position: 'top_right',
  config: {
    backendUrl: 'http://localhost:5000',
    updateInterval: 300000  // 5 minutes in ms
  }
}
```

## 📝 Todoist Setup

### 1. Create Project Structure

1. Create project "UNI" in Todoist
2. Add sections for your courses:
   - Mathematics
   - Computer Science
   - Physics
   - etc.

### 2. Create Label

1. Settings → Labels
2. Create label "abgabe"

### 3. Add Assignments

Create tasks with:
- Title: Assignment name
- Label: `#abgabe`
- Due date: Deadline
- Project: UNI > [Your Course]

Example:
```
Problem Set 2 #abgabe
Due: tomorrow 23:59
Project: UNI > Mathematics
```

### 4. Get API Token

1. Visit https://todoist.com/prefs/integrations
2. Copy your API token
3. Add to `backend/.env`:
   ```env
   TODOIST_API_TOKEN=your_token_here
   ```

## 🔧 Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `backendUrl` | `http://localhost:5000` | Flask backend URL |
| `updateInterval` | `300000` | Update interval in ms (5 min) |
| `animationSpeed` | `500` | Animation speed in ms |
| `maxAssignments` | `10` | Max assignments to display |
| `showProgress` | `true` | Show module progress bars |

## 📡 Backend API

### Endpoints

```bash
# Health check
GET http://localhost:5000/health

# Get all assignments
GET http://localhost:5000/api/assignments

# Get week assignments
GET http://localhost:5000/api/assignments/week

# Get module assignments
GET http://localhost:5000/api/assignments/module/:id

# Trigger manual sync
POST http://localhost:5000/api/sync
```

### Service Management

```bash
# Status
sudo systemctl status mmm-uni-assignments

# Restart
sudo systemctl restart mmm-uni-assignments

# Logs
sudo journalctl -u mmm-uni-assignments -f

# Manual start
./start-backend.sh
```

## 🎯 Display Views

### Week View
Shows assignments due in the next 7 days with:
- Module badges with colors
- Due date badges (urgent/warning/normal)
- Assignment titles and descriptions
- Sorted by due date

### Module View
Shows progress per course with:
- Completion percentage
- Progress bars with color coding
- Total vs completed assignments
- Upcoming assignments count

## 🔄 Updates

```bash
cd ~/MagicMirror/modules/MMM-UniAssignments
git pull
./update.sh
sudo systemctl restart mmm-uni-assignments
pm2 restart MagicMirror
```

## 🤝 Works Great With

- [MMM-WebhookTrigger](https://github.com/FreakyLetsFail/MMM-WebhookTrigger) - Control display via webhooks

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check logs
sudo journalctl -u mmm-uni-assignments -n 50

# Manual test
cd backend
source venv/bin/activate
python3 todoist_sync.py
```

### No assignments shown

```bash
# Manual sync
curl -X POST http://localhost:5000/api/sync

# Check if token is valid
cat backend/.env
```

### Tasks not syncing

Ensure tasks have:
- Label `#abgabe`
- Due date set
- In project "UNI"

## 📚 Documentation

- [docs/TODOIST_SETUP.md](docs/TODOIST_SETUP.md) - Detailed Todoist setup guide

## 📝 License

MIT © Justus Waechter

## 🐛 Issues

Report issues at: https://github.com/FreakyLetsFail/MMM-UniAssignments/issues
