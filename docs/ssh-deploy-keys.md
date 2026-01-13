## Access to private GitHub repos with SSH Deploy Keys

### Creating Deploy Keys

1. Generate an SSH key pair (if you don't have one):

   ```bash
   ssh-keygen -t ed25519 -C "crdm-tools-deploy-key" -f ~/.ssh/crdm_deploy_key
   ```

2. Add the public key as a deploy key to both repositories:
   - Go to `https://github.com/uclh-criu/omop_es/settings/keys`
   - Click "Add deploy key"
   - Paste contents of `~/.ssh/crdm_deploy_key.pub`
   - Grant read-only access
   - Repeat for `https://github.com/uclh-criu/omop-cascade`

### Local Development Setup

For both Docker builds and runtime operations to work, ensure your SSH key is loaded:

```bash
# Start SSH agent
eval "$(ssh-agent -s)"

# Add your key
ssh-add ~/.ssh/crdm_deploy_key

# Verify access
ssh -T git@github.com

# Build with SSH forwarding (BuildKit must be enabled)
DOCKER_BUILDKIT=1 docker compose build omop_es

# Run container (SSH agent is automatically forwarded at runtime)
docker compose run omop_es
```

Docker BuildKit automatically forwards your SSH agent to build containers when enabled with
`DOCKER_BUILDKIT=1`. At runtime, the `SSH_AUTH_SOCK` environment variable is mounted into the
container to allow git operations (e.g., fetching updates, checking out refs).

### GAE Setup

On each GAE instance:

1. Copy the private key to the GAE:

   ```bash
   scp ~/.ssh/crdm_deploy_key user@gae-host:~/.ssh/id_ed25519
   ```

2. Set proper permissions:

   ```bash
   chmod 600 ~/.ssh/id_ed25519
   ```

3. Add to SSH agent:

   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

4. For persistent agent across reboots, create a systemd user service or add to shell profile:

   ```bash
   # Add to ~/.bashrc or ~/.profile
   if [ -z "$SSH_AUTH_SOCK" ]; then
       eval "$(ssh-agent -s)"
       ssh-add ~/.ssh/id_ed25519 2>/dev/null
   fi
   ```

   **Important**: The SSH agent must be running before starting Docker containers, as the
   `SSH_AUTH_SOCK` socket is mounted into containers at runtime for git operations.

### GitHub Actions Setup

The deploy key private key is stored as a GitHub Actions secret (`OMOP_ES_DEPLOY_KEY`). This is
automatically configured in CI/CD workflows.
