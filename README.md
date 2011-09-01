Twinsects : Simple app for follower overlap "analysis"
=====

Twinsects tries to visualize follower overlaps w/ Venn diagrams. These are rendered for 2-4 accounts, otherwise a stats table is displayed.

Setup
-----

To install all dependecies just try:

    pip install -r requirements.pip

To setup the app, just edit your settings either in settings/base.py (used both on dev and production), settings/production.py or settings/local_empty.py to suit your needs. If you edit local_empty.py be sure to copy it as local.py in order to get loaded during development.

The WSGI file should work w/out any tuning. Consult your web server docs to make wsgi work with your server. Sample vhost file for Apache would look like this:

    root@kosmik1:/home/starenka# cat /etc/apache2/sites-available/twinsects
        <VirtualHost 127.0.0.1:80>
            ServerName twinsects
                WSGIDaemonProcess twinsects user=starenka group=starenka threads=5
                WSGIScriptAlias / /www/twinsects/twinsects.wsgi

                <Directory /www/twinsects>
                    WSGIProcessGroup twinsects
                    WSGIApplicationGroup %{GLOBAL}
                    WSGIScriptReloading On
                    Order deny,allow
                    Allow from all
                </Directory>
        </VirtualHost>

As for nginx and uWSGI & supervisor your config would look like this:

supervisor:
---

    [program:twinsects.starenka.net]
    command=/usr/local/bin/uwsgi
      --socket /www/twinsects/uwsgi.sock
      --pythonpath /www/twinsects
      --touch-reload /www/twinsects/app.wsgi
      --chmod-socket 666
      --uid starenka
      --gid starenka
      --processes 1
      --master
      --no-orphans
      --max-requests 5000
      --module twinsects
      --callable app
    directory=/www/twinsects/
    stdout_logfile=/www/twinsects/uwsgi.log
    user=starenka
    autostart=true
    autorestart=true
    redirect_stderr=true
    stopsignal=QUIT

nginx:
---

    server {
            listen       80;
            server_name  twinsects.starenka.net;
            root    /www/twinsects/;

            access_log  /www/twinsects/access.log;
            error_log /www/twinsects/error.log;

            location / {
                    uwsgi_pass unix:///www/twinsects/uwsgi.sock;
                    include        uwsgi_params;
            }

            location /static {
                    alias /www/twinsects/static;
            }
    }


Have fun!

