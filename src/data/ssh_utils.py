import os
import tempfile
from contextlib import contextmanager

import sshtunnel


@contextmanager
def ssh_tunnel(settings):
    """
    Establishes an SSH tunnel to a remote server and yields the tunnel object.

    Parameters
    ----------
    settings : Settings
        A configuration object containing necessary SSH connection details such as host, port, username, and key.

    Yields
    ------
    sshtunnel.SSHTunnelForwarder
        An SSHTunnelForwarder object representing the active SSH tunnel.

    Raises
    ------
    Exception
        Any exceptions raised during the SSH tunnel setup or teardown will propagate upwards.

    Notes
    -----
    This function creates a temporary file to store the SSH private key securely.
    It sets the appropriate permissions on the key file before establishing the tunnel.
    The tunnel is stopped and the key file is deleted when the context manager exits, ensuring cleanup.
    """
    temp_key_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
    try:
        temp_key_file.write(settings.DWH_SSH_KEY)
        temp_key_file.close()
        os.chmod(temp_key_file.name, 0o600)

        tunnel = sshtunnel.open_tunnel(
            (settings.DWH_SSH_HOST, int(settings.DWH_SSH_PORT)),
            ssh_username=settings.DWH_SSH_USERNAME,
            ssh_pkey=temp_key_file.name,
            remote_bind_address=("localhost", int(settings.DWH_PORT)),
        )

        tunnel.start()
        yield tunnel
    finally:
        tunnel.stop()
        os.unlink(temp_key_file.name)
