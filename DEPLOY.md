# Render Deployment Troubleshooting

## Current Issue: Port Binding to localhost instead of 0.0.0.0

If you're seeing "Detected open ports on localhost" error, follow these steps:

## Step 1: Verify Render Dashboard Settings

1. Go to your Render service dashboard
2. Click on **Settings** tab
3. Scroll to **"Start Command"** section
4. **IMPORTANT**: Make sure it shows:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. **DO NOT** have any of these:
   - `--reload` (development only)
   - `127.0.0.1` or `localhost`
   - `--host 127.0.0.1`
   - Port number like `:8000` (must use `$PORT`)

## Step 2: Check Environment Variables

1. In Render dashboard, go to **Environment** tab
2. Verify these are set:
   - `SUPABASE_URL` (your Supabase URL)
   - `SUPABASE_KEY` (your Supabase service role key)
   - `PORT` (automatically set by Render, don't add manually)

## Step 3: Manual Override

If `render.yaml` isn't being used:

1. In Render dashboard → **Settings**
2. **Clear** the "Start Command" field if it has wrong values
3. **Set it to**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Save and redeploy

## Step 4: Verify Files Are Committed

Make sure these files are in your repository:
- `render.yaml` (in root)
- `Procfile` (in root)
- `requirements.txt` (in root)
- `main.py` (in root)

## Step 5: Rebuild

1. In Render dashboard, go to **Manual Deploy** → **Clear build cache & deploy**
2. Or push a new commit to trigger auto-deploy

## Common Mistakes

❌ **Wrong**: `uvicorn main:app --reload`
❌ **Wrong**: `uvicorn main:app --host 127.0.0.1 --port 8000`
❌ **Wrong**: `uvicorn main:app --port 8000`
✅ **Correct**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Still Not Working?

1. Check the **Logs** tab in Render dashboard for startup errors
2. Verify the build completed successfully
3. Make sure the service type is "Web Service" not "Background Worker"



