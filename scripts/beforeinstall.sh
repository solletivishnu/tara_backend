echo "🐳 Cleaning Docker (containers & images only, skipping volumes)..."
docker builder prune -af || true
docker image prune -af
echo "[BeforeInstall] ✅ Done."