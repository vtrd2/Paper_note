import os, sys
import click
from flask_migrate import Migrate, upgrade
from app import create_app, db
from app.models import User, Note

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Note=Note)


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


def profile(length, profile_dir):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)

    app.run()

def start_profile():
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'profile':
            profile(25, None)

start_profile()

@app.cli.command('deploy')
def deploy():
    """Run deployments tasks."""
    upgrade()
