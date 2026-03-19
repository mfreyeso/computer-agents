import logging
import os
import uuid

import docker
from src.core.config import settings

logger = logging.getLogger(__name__)

class DockerProvisionerService:
    def __init__(self):
        try:
            self.client = docker.from_env()
        except Exception as e:
            logger.warning(f"Could not connect to Docker daemon: {e}")
            self.client = None

        self.image = "ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest"

    def spawn_vnc_environment(self, session_id: uuid.UUID) -> dict:
        """
        Spawns a new VNC environment container over the Docker daemon for a given session.
        Returns the container name and the dynamically exposed noVNC host port.
        """
        if not self.client:
            raise RuntimeError("Docker daemon connection failed")

        container_name = f"vnc_env_{str(session_id)}"
        
        host_pwd = getattr(settings, "HOST_PWD", os.environ.get("HOST_PWD", "."))
        
        volumes = {
            f"{host_pwd}/scripts/tool_server.py": {
                "bind": "/opt/tool_server.py",
                "mode": "ro"
            },
            f"{host_pwd}/scripts/vnc_start.sh": {
                "bind": "/opt/vnc_start.sh",
                "mode": "ro"
            }
        }
        
        environment = {
            "ANTHROPIC_API_KEY": settings.ANTHROPIC_API_KEY,
            "WIDTH": "1024",
            "HEIGHT": "768",
        }

        # Let Docker assign random free ports for noVNC so they don't collide
        ports = {
            "6080/tcp": None
        }

        logger.info(f"Provisioning dynamically orchestrating container {container_name}...")
        
        try:
            container = self.client.containers.run(
                image=self.image,
                name=container_name,
                entrypoint="/opt/vnc_start.sh",
                environment=environment,
                volumes=volumes,
                ports=ports,
                network="energent_code_default",
                detach=True,
                remove=True  # Automatically removes container when stopped
            )
            
            # Retrieve the assigned host port for noVNC (6080)
            container.reload()
            assigned_port = container.attrs['NetworkSettings']['Ports']['6080/tcp'][0]['HostPort']
            
            return {
                "container_name": container_name,
                "websockify_port": int(assigned_port)
            }
        except Exception as e:
            logger.error(f"Failed to spawn VNC environment container: {e}")
            raise

    def cleanup_environment(self, container_name: str):
        """Stops the container, which also triggers auto-removal."""
        if not self.client:
            return
            
        try:
            container = self.client.containers.get(container_name)
            container.stop(timeout=2)
            logger.info(f"Stopped and removed VNC environment {container_name}")
        except docker.errors.NotFound:
            pass  # Already cleaned up
        except Exception as e:
            logger.error(f"Error cleaning up VNC environment {container_name}: {e}")

docker_provisioner = DockerProvisionerService()
