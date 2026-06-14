container_id=$(docker ps -q -f ancestor=ghcr.io/all-hands-ai/openhands:main)
docker exec $container_id bash -c "tail -n 100 -f /proc/\$(pgrep -f docker-buildx)/fd/2" >> /home/albin/projects/pme/backend/logs/REQ-001.log &
