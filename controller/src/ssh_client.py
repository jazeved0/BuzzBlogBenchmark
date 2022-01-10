# Copyright (C) 2020 Georgia Tech Center for Experimental Research in Computer
# Systems

import datetime

import paramiko
import scp


class SSHClient:
  """A wrapper around paramiko.SSHClient."""

  def __init__(self, hostname, port, username, key_filename, log_filename, connect_timeout=None):
    """Initialize an SSH client."""
    self._hostname = hostname
    self._client = paramiko.SSHClient()
    self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    self._client.connect(hostname=hostname, port=port, username=username,
        key_filename=key_filename, timeout=connect_timeout,
        banner_timeout=connect_timeout, auth_timeout=connect_timeout)
    self._log_filename = log_filename

  def exec(self, command):
    """Execute command remotely.

    Data written to stdout and stderr are appended to files named with the
    log_filename attribute and extensions '.out' and '.err', respectively.
    """
    print("[{ts}][{hostname}] {command}".format(
        ts=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        hostname=self._hostname, command=command))
    _, stdout, stderr = self._client.exec_command(command)
    stdout.channel.recv_exit_status()
    with open(self._log_filename + ".out", "ab+") as stdout_log_file:
      stdout_b = stdout.read()
      stdout_log_file.write(stdout_b)
    with open(self._log_filename + ".err", "ab+") as stderr_log_file:
      stderr_b = stderr.read()
      stderr_log_file.write(stderr_b)
    return (stdout_b, stderr_b)

  def copy(self, remote_path, local_path=""):
    """Copy remote file to the local machine."""
    with scp.SCPClient(self._client.get_transport(), sanitize=lambda x: x) as \
        scp_client:
      scp_client.get(remote_path, local_path, recursive=True)
