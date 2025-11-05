# Deploying to Streamlit Cloud

This guide shows how to deploy your Youth Employment Policy Simulator to Streamlit Cloud for 24/7 public access.

## Prerequisites

✅ GitHub account
✅ Code pushed to GitHub repository
✅ Streamlit Cloud account (free - sign up with GitHub)

## Deployment Steps (5 minutes)

### 1. Push Code to GitHub

Your code should already be on GitHub. Make sure the latest changes are pushed:

```bash
git add -A
git commit -m "Add Streamlit web interface"
git push origin main
```

### 2. Sign Up for Streamlit Cloud

1. Go to **https://streamlit.io/cloud**
2. Click **"Sign up"**
3. Choose **"Continue with GitHub"**
4. Authorize Streamlit to access your repositories

### 3. Deploy Your App

1. Click **"New app"** button
2. Fill in the form:
   - **Repository:** `martar2277/ABM_policy_simulation`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
   - **App URL:** Choose a custom name (e.g., `youth-employment-sim`)

3. Click **"Deploy!"**

### 4. Wait for Deployment

- First deployment takes 2-3 minutes
- Streamlit will install dependencies from `requirements.txt`
- You'll see logs in real-time
- When complete, your app will be live!

### 5. Get Your URL

Your app will be available at:
```
https://[your-app-name].streamlit.app
```

For example: `https://youth-employment-sim.streamlit.app`

## Your App is Now Live 24/7! 🎉

✅ Always running (never shuts down)
✅ Serverless (no servers to manage)
✅ Free hosting
✅ Auto-updates when you push to GitHub

## Updating Your App

To update the live app, just push changes to GitHub:

```bash
# Make changes to streamlit_app.py or other files
git add -A
git commit -m "Update app"
git push origin main
```

Streamlit Cloud will automatically redeploy within 1-2 minutes.

## Sharing Your App

### Add to LinkedIn

1. Go to your LinkedIn profile
2. Click **"Add profile section"** → **"Featured"** → **"Add link"**
3. Paste your Streamlit URL
4. Add title: "Youth Employment Policy Simulator"
5. Add description: "Interactive tool demonstrating agent-based modeling for policy analysis"

### Share Directly

Just share the URL:
```
https://[your-app-name].streamlit.app
```

Anyone can access it - no login required!

## Monitoring Usage

Streamlit Cloud provides basic analytics:
- Go to **https://share.streamlit.io**
- Click on your app
- View **"Analytics"** tab
- See number of visitors, sessions, etc.

## Troubleshooting

### App won't start

Check the logs in Streamlit Cloud dashboard for errors.

Common issues:
- Missing dependencies in `requirements.txt` → Add them
- Python version mismatch → Create `.streamlit/config.toml` (see below)
- Import errors → Check file paths

### Custom Configuration

Create `.streamlit/config.toml` if needed:

```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
maxUploadSize = 200
```

### Slow Performance

If simulations are slow:
- Reduce default population sizes in the app
- Add a warning about computation time
- Consider caching results with `@st.cache_data`

## Cost

**FREE** for public apps!

Streamlit Cloud free tier includes:
- Unlimited public apps
- 1 GB RAM per app
- Community support

## Advanced: Custom Domain (Optional)

Streamlit Cloud allows custom domains on paid plans:
- **Starter**: $20/month - Custom domain, private apps
- **Teams**: $250/month - Multiple users, SSO

For now, the free `*.streamlit.app` URL is perfect for your marketing teaser!

## Support

- Streamlit Docs: https://docs.streamlit.io
- Community Forum: https://discuss.streamlit.io
- Your app dashboard: https://share.streamlit.io

---

## Quick Reference

| Action | Command/URL |
|--------|-------------|
| Deploy | https://streamlit.io/cloud → New app |
| Your apps | https://share.streamlit.io |
| Update app | `git push origin main` |
| View logs | App dashboard → "Manage app" → "Logs" |
| Restart app | App dashboard → "⋮" → "Reboot app" |

---

**That's it! Your app is now accessible 24/7 to anyone in the world.** 🌍
