__author__ = 'sohje'

from fabric.api import task, env, roles, run, settings, sudo

env.roledefs = {
    'bb2-w3': [
        '192.168.22.101', '192.168.5.102', '192.168.8.103', '192.168.231.104',
        '192.168.31.111', '192.168.6.112', '192.168.9.121', '192.168.231.122',
        '192.168.4.131', '192.168.231.132'
    ],
    'blackbox-1': ['10.0.4.23', '10.0.3.23', '10.0.5.25', '10.0.5.26'],
    'blackbox-2': ['10.0.4.22', '10.0.3.12', '10.0.5.23', '10.0.5.28'],
    'blackbox-3': ['10.0.4.29', '10.0.3.24', '10.0.5.254', '10.0.5.24'],
    'dns': ['10.0.1.1', '10.0.2.13'],
    'ip-test': ['10.10.40.19'],
}

@roles('bb2-w3')
@task
def deploy_bb2_w3(revision='HEAD'):
    """ Update all bb2 w3 """
    with settings(warn_only=True):
        sudo('service bbw-w3 stop', pty=False)
        sudo('cat /dev/null > /var/log/public.log')
        sudo('svn up -r %s /var/lib/bbw-w3/' % revision)
        sudo('service bbw-w3 start', pty=False)


@roles('dns')
@task
def deploy_dns():
    """ Update dns """
    sudo("svn up /var/named/")
    sudo("svn up /etc/")
    sudo("service named restart")

@roles('blackbox-1', 'blackbox-2', 'blackbox-3', 'blackbox-4')
@task
def deploy_prod_be(revision='HEAD'):
    """
        Deploys production
    """
    with settings(warn_only=True):
        sudo('/etc/init.d/httpd stop', pty=False)
        sudo(
            "svn up --force --non-interactive -r %s /www/domain2.tld /www/domain.tld" % revision,
            user='webme'
        )
        sudo('/etc/init.d/httpd start', pty=False)

@roles('blackbox-1', 'blackbox-2', 'blackbox-3', 'blackbox-4')
@task
def deploy_sendmail():
    """
        Update sendmail on servers
    """
    with settings(warn_only=True):
        sudo('service sendmail stop')
        sudo('svn up --force /etc/mail/')
        sudo('service sendmail start')

@roles('dns')
@task
def nipsy():
    """
        Uptime and kernel version on DNS servers
    """
    run('uname -a')
    run('uptime')
