# PR Preview Deployment Setup

This repository is configured to automatically deploy PR previews using Render.com.

## How It Works

When you open a pull request:
1. GitHub Actions automatically deploys your PR to a preview environment on Render
2. A bot comments on the PR with the preview URL
3. The preview updates automatically when you push new commits
4. The preview is deleted when the PR is closed

## Setup Instructions

### 1. Create a Render Account

1. Go to [render.com](https://render.com) and sign up (free tier available)
2. Connect your GitHub account

### 2. Get Render API Key

1. Go to [Account Settings > API Keys](https://dashboard.render.com/u/settings#api-keys)
2. Click "Create API Key"
3. Copy the key (you won't see it again)

### 3. Add GitHub Secret

1. Go to your repository's Settings > Secrets and variables > Actions
2. Click "New repository secret"
3. Name: `RENDER_API_KEY`
4. Value: Paste the API key from step 2
5. Click "Add secret"

### 4. Optional: Configure OAuth and Storage

For full functionality in preview environments:

1. Go to your Render service dashboard
2. Navigate to Environment variables
3. Add:
   - `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
   - `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
   - Update `ALLOWED_HOSTS` to include your Render URL

Note: Preview environments use SQLite by default. For production, upgrade to PostgreSQL in Render dashboard.

## Preview Environment Details

- **Platform**: Render.com (free tier)
- **Database**: SQLite (ephemeral, resets on redeploy)
- **URL Format**: `https://imageoptimizer-pr-{number}.onrender.com`
- **Cold Start**: First load may take 30-60 seconds
- **Auto-cleanup**: Deleted when PR is closed

## Alternative: Railway.app

If you prefer Railway instead of Render:

1. Create a Railway account at [railway.app](https://railway.app)
2. Get your Railway API token from the dashboard
3. Add it as `RAILWAY_TOKEN` secret in GitHub
4. Update the workflow file to use Railway API instead

## Troubleshooting

**Preview not deploying?**
- Check that `RENDER_API_KEY` secret is set correctly
- Verify the GitHub Actions workflow ran successfully
- Check Render dashboard for deployment logs

**Preview URL not working?**
- Wait 30-60 seconds for cold start
- Check service logs in Render dashboard
- Verify environment variables are set

**OAuth not working?**
- Add preview URL to Google OAuth redirect URIs
- Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in Render

## Cost

- **Free tier**: Sufficient for PR previews (spins down after 15 min of inactivity)
- **Paid tier**: $7/month for always-on service (not required for previews)

## Security Note

Preview environments should use minimal/mock credentials. Do not use production credentials in preview deployments.
