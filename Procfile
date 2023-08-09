# Run web app
web: gunicorn --chdir src config.wsgi:application --log-file - --timeout 120

# post-deploy tasks
postdeploy: bash src/bin/post_deploy
