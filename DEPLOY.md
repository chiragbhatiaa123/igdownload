# Deploying Instagram Downloader Bot

This guide explains how to deploy your bot to a server so it runs 24/7.

## Prerequisites

- A [GitHub](https://github.com/) account (to host your code).
- Your `TELEGRAM_BOT_TOKEN` (get it from @BotFather).

## Option 1: Railway (Recommended)

Railway is very easy to use and often has a free trial or low cost.

1.  **Push your code to GitHub**:
    - Create a new repository on GitHub.
    - Push all your files (`src/`, `Dockerfile`, `requirements.txt`, etc.) to it.

2.  **Create a Project on Railway**:
    - Go to [railway.app](https://railway.app/).
    - Click "New Project" -> "Deploy from GitHub repo".
    - Select your repository.

3.  **Configure Variables**:
    - Once the project is created, go to the **Variables** tab.
    - Add a new variable:
        - Key: `TELEGRAM_BOT_TOKEN`
        - Value: `your_actual_bot_token_here`

4.  **Deploy**:
    - Railway will automatically detect the `Dockerfile` and build your bot.
    - Wait a few minutes. You should see "Active" and your bot will be online!

## Option 2: Render

Render offers a free tier for web services (though for persistent bots, the paid "Background Worker" or "Web Service" is better to avoid sleep).

1.  **Push to GitHub** (same as above).
2.  **Create a Service on Render**:
    - Go to [render.com](https://render.com/).
    - Click "New" -> "Blueprints" OR "Web Service".
    - Connect your GitHub repo.
3.  **Settings**:
    - **Runtime**: Docker
    - **Environment Variables**: Add `TELEGRAM_BOT_TOKEN` with your token.
4.  **Deploy**: Click "Create Service".

## Option 3: Local / VPS (Docker)

If you have your own server (DigitalOcean, AWS, or just your PC), use Docker.

1.  **Build the image**:
    ```bash
    docker-compose build
    ```

2.  **Run in background**:
    ```bash
    docker-compose up -d
    ```

3.  **View Logs**:
    ```bash
    docker-compose logs -f
    ```

4.  **Stop**:
    ```bash
    docker-compose down
    ```

## Troubleshooting

- **Bot not responding**: Check logs on your platform.
- **Login Required**: Instagram might block server IPs. If you see "Login required", you might need to supply a session file or cookies, but simple public posts usually work.
- **Updates**: If you change code, just push to GitHub. Railway/Render will auto-redeploy.
