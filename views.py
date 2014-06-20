from datetime import datetime
from flask import redirect, url_for, abort
from flask.globals import g, request
from flask.templating import render_template
from flask.views import MethodView
from forms import JobForm
from travispy import TravisPy


#===================================================================================================
# user_required
#===================================================================================================
def user_required(f):
    '''
    Checks whether user is logged in or redirects to login page.
    '''

    def decorator(*args, **kwargs):
        if not g.travispy:
            return redirect(url_for('index'))
        else:
            return f(*args, **kwargs)

    return decorator


#===================================================================================================
# forbidden_repo
#===================================================================================================
def forbidden_repo(f):
    '''
    Check if current user has access to desired repository.
    It should be used with "user_required" decorator.
    '''

    def decorator(*args, **kwargs):
        repo_id = kwargs.get('repo_id')
        if repo_id is not None:
            travispy = g.travispy
            github_user = travispy.user()

            repos = travispy.repos(member=github_user.login, active=True)
            repo_ids = [repo.id for repo in repos]

            if repo_id not in repo_ids:
                abort(403)

        return f(*args, **kwargs)

    return decorator


#===================================================================================================
# run_build
#===================================================================================================
def run_build(user_id, repo_id):
    from models import User
    from database import db_session

    db_session()

    filename = '%d_%d.log' % (user_id, repo_id,)
    with open(filename, 'a') as f:
        try:
            user = User.query.get(user_id)

            travispy = TravisPy.github_auth(user.github_access_token)
            repo = travispy.repo(repo_id)
            build = travispy.build(repo.last_build_id)
            build.restart()

        except Exception as e:
            f.write('%s\n' % str(e))

        else:
            f.write('Success\n')

    db_session.remove()


#===================================================================================================
# RepositoriesAPI
#===================================================================================================
class RepositoriesAPI(MethodView):

    decorators = [user_required]

    def get(self):
        travispy = g.travispy
        github_user = travispy.user()
        repos = travispy.repos(member=github_user.login, active=True)
        return render_template('repositories.html', user=github_user, repos=repos)


#===================================================================================================
# JobsAPI
#===================================================================================================
class JobsAPI(MethodView):

    decorators = [user_required, forbidden_repo]

    def get(self, repo_id):
        from database import db_session
        from models import Job

        travispy = g.travispy
        github_user = travispy.user()
        repo = travispy.repo(repo_id)
        jobs = db_session.query(Job).filter(Job.repository_id == repo_id).order_by(Job.created_datetime)
        
        return render_template('jobs.html', user=github_user, jobs=list(jobs), repo_id=repo_id, slug=repo.slug)


#===================================================================================================
# NewJobAPI
#===================================================================================================
class NewJobAPI(MethodView):

    decorators = [user_required, forbidden_repo]

    def get(self, repo_id):
        form = JobForm(request.form)

        travispy = g.travispy
        repo = travispy.repo(repo_id)

        return render_template('job_form.html', form=form, repo_id=repo_id, command='new', slug=repo.slug)


    def post(self, repo_id):
        from database import db_session
        from models import Job
        from scheduler import scheduler

        form = JobForm(request.form)
        if form.validate():
            user = g.user
            aps_job = scheduler.add_cron_job(
                run_build,
                None,
                request.form['month'] or None,
                request.form['day'] or None,
                request.form['week'] or None,
                request.form['day_of_week'] or None,
                request.form['hour'] or None,
                request.form['minute'] or None,
                args=[user.id, repo_id],
            )
            scheduler._real_add_job(aps_job, 'default', False)

            now = datetime.now()

            job = Job()
            job.aps_job_id = aps_job.id
            job.repository_id = repo_id
            job.created_datetime = now
            job.updated_datetime = now

            db_session.add(job)
            db_session.commit()

            return redirect(url_for('jobs', repo_id=repo_id))

        else:
            travispy = g.travispy
            repo = travispy.repo(repo_id)
            return render_template('job_form.html', form=form, repo_id=repo_id, command='new', slug=repo.slug)


#===================================================================================================
# DeleteJobAPI
#===================================================================================================
class DeleteJobAPI(MethodView):

    decorators = [user_required, forbidden_repo]

    def get(self, repo_id, job_id):
        from database import db_session
        from models import Job
        from scheduler import scheduler

        job = Job.query.get(job_id)
        aps_job_id = job.aps_job_id
        
        for aps_job in scheduler.get_jobs():
            if aps_job.id == aps_job_id:
                scheduler.unschedule_job(aps_job)
                db_session.delete(job)
                db_session.commit()
                break
        
        return redirect(url_for('jobs', repo_id=repo_id))
