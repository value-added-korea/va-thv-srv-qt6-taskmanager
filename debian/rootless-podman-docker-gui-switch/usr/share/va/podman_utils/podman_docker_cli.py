#!/usr/bin/env python3
import subprocess
import sys
import argparse

def run_cmd(cmd):
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def podman_target():
    return ["systemctl", "--user"]

def enable_podman():
    run_cmd(podman_target() + ["start", "podman.socket"])
    run_cmd(podman_target() + ["start", "podman.service"])

def disable_podman():
    run_cmd(podman_target() + ["stop", "podman.socket"])
    run_cmd(podman_target() + ["stop", "podman.service"])

def enable_docker():
    run_cmd(podman_target() + ["start", "docker.socket"])
    run_cmd(podman_target() + ["start", "docker.service"])

def disable_docker():
    run_cmd(podman_target() + ["stop", "docker.socket"])
    run_cmd(podman_target() + ["stop", "docker.service"])

def is_podman_active():
    res = subprocess.run(podman_target() + ["is-active", "podman.socket"], capture_output=True, text=True)
    if res.returncode == 0: return True
    res = subprocess.run(podman_target() + ["is-active", "podman.service"], capture_output=True, text=True)
    return res.returncode == 0

def is_docker_active():
    res = subprocess.run(podman_target() + ["is-active", "docker.socket"], capture_output=True, text=True)
    if res.returncode == 0: return True
    res = subprocess.run(podman_target() + ["is-active", "docker.service"], capture_output=True, text=True)
    return res.returncode == 0

def action_podman_only():
    enable_podman()
    disable_docker()

def action_docker_only():
    enable_docker()
    disable_podman()

def action_both_enabled():
    enable_podman()
    enable_docker()

def action_both_disabled():
    disable_podman()
    disable_docker()

def get_status():
    podman = is_podman_active()
    docker = is_docker_active()
    return {"podman": podman, "docker": docker}

def main():
    parser = argparse.ArgumentParser(
        description="Switch between Podman and Docker rootless user services.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Verbose Help:
This application allows you to strictly control the rootless service endpoints
for both Podman and Docker in the user space.

When executing commands, the utility interacts with `systemctl --user` to
start or stop the `podman.socket`, `podman.service`, `docker.socket`,
and `docker.service` units accordingly.

Available Actions:
  --podman-only     Starts Podman engine, stops Docker engine
  --docker-only     Starts Docker engine, stops Podman engine
  --both-enabled    Starts both Podman and Docker engines
  --both-disabled   Stops both Podman and Docker engines
  --status          Outputs current run status as a JSON object

Example Usage:
  la_toolhive_thv_ui.py --podman-only
  la_toolhive_thv_ui.py --status

Author: System Utilities
"""
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--podman-only", action="store_true", help="Enable Podman, disable Docker")
    group.add_argument("--docker-only", action="store_true", help="Enable Docker, disable Podman")
    group.add_argument("--both-enabled", action="store_true", help="Enable both Podman and Docker")
    group.add_argument("--both-disabled", action="store_true", help="Disable both Podman and Docker")
    group.add_argument("--status", action="store_true", help="Print current status in JSON")

    args = parser.parse_args()

    if args.podman_only:
        action_podman_only()
    elif args.docker_only:
        action_docker_only()
    elif args.both_enabled:
        action_both_enabled()
    elif args.both_disabled:
        action_both_disabled()
    elif args.status:
        import json
        print(json.dumps(get_status()))

if __name__ == "__main__":
    main()
