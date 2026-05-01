import paramiko

VPS_IP = "194.87.115.67"
VPS_USER = "root"
VPS_PASSWORD = "ТВОЙ_ПАРОЛЬ"


def run_ssh(cmd: str) -> str:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(
            hostname=VPS_IP,
            username=VPS_USER,
            password=VPS_PASSWORD,
            look_for_keys=False,
            allow_agent=False,
            auth_timeout=20,
            banner_timeout=20
        )

        transport = ssh.get_transport()
        if not transport or not transport.is_active():
            raise Exception("No SSH transport")

        stdin, stdout, stderr = ssh.exec_command(cmd)

        out = stdout.read().decode().strip()
        err = stderr.read().decode().strip()

        ssh.close()

        if err and "Warning" not in err:
            raise Exception(err)

        return out

    except Exception as e:
        try:
            ssh.close()
        except:
            pass

        raise Exception(f"SSH error: {e}")
