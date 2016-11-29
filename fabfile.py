from fabric.api import env
from fabric.contrib.project import upload_project
from fabric.operations import put, run, sudo, local

env.hosts = ["web.mgmt.fwilson.me"]

def deploy():
    put("config/*.nginx.conf", "/etc/nginx/servers.d", use_sudo=True)
    put("config/*.supervisor.ini", "/etc/supervisor.d", use_sudo=True)

    sudo("rm -rf /home/app/deployed/paste")
    sudo("mkdir -p /home/app/deployed/paste")
    local("tar -czf /tmp/deploy.tar.gz app")
    put("/tmp/deploy.tar.gz", "/tmp/deploy.tar.gz")
    sudo("tar xzf /tmp/deploy.tar.gz -C /home/app/deployed/paste")
    local("rm /tmp/deploy.tar.gz")
    run("rm /tmp/deploy.tar.gz")
    sudo("chown -R app /home/app/deployed/paste")

    sudo("supervisorctl update")
    sudo("supervisorctl restart paste")
    sudo("systemctl reload nginx")

def deprovision():
    sudo("supervisorctl stop paste")
    sudo("rm /etc/nginx/servers.d/paste.nginx.conf")
    sudo("rm /etc/supervisor.d/paste.supervisor.ini")
    sudo("rm -rf /home/app/deployed/paste")
    sudo("supervisorctl update")
    sudo("systemctl reload nginx")

def ssl():
    sudo("certbot certonly --webroot --webroot-path /srv/web/static -d paste.fwilson.me")
