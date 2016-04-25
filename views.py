from bson.objectid import ObjectId
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
# run_newest_build
#===================================================================================================
def run_newest_build(user_id, repo_id):
    '''
    Method responsible for restarting newest build for the given repo_id.
    Given user_id must have access to the repository.
    '''
    from database import users, jobs

    user_id = ObjectId(user_id)
    user = users.find_one({'_id': user_id})
    travispy = TravisPy.github_auth(user['github_access_token'])

    # When GitHub token is invalid user and jobs created under such token will be removed.
    if travispy is None:
        for job in jobs.find({'user_id': user_id, 'repo_id': repo_id}):
            remove_job(str(job['_id']))
        users.remove(user_id)
        return

    # Run newest build.
    builds = travispy.builds(repository_id=repo_id)
    if builds:
        builds[0].restart()


#===================================================================================================
# remove_job
#===================================================================================================
def remove_job(job_id):
    '''
    Method responsible for removing a job from database.

    :param str job_id:
        ID of the job that must be removed.

    :rtype: boolean
    :returns:
        True when job is removed successfuly.
    '''
    from database import jobs
    from scheduler import scheduler

    job = jobs.find_one({'_id': ObjectId(job_id)})
    aps_job_id = job['aps_job_id']

    for aps_job in scheduler.get_jobs():
        if aps_job.id == aps_job_id:
            scheduler.unschedule_job(aps_job)
            jobs.remove(job)
            return True

    return False


#===================================================================================================
# RepositoriesAPI
#===================================================================================================
class RepositoriesAPI(MethodView):
    '''
    View responsible for showing all Travis CI repositories that current user has access.
    '''

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
    '''
    View responsible for list jobs for repository currently selected.
    '''

    decorators = [user_required, forbidden_repo]

    def get(self, repo_id):
        from database import database, jobs

        travispy = g.travispy
        github_user = travispy.user()
        repo = travispy.repo(repo_id)

        aps_jobs = database['aps_jobs']

        tronci_jobs = []
        for job in jobs.find({'repo_id': repo_id}).sort('created_datetime'):
            job['aps_job'] = aps_jobs.find_one({'_id': job['aps_job_id']})
            tronci_jobs.append(job)

        return render_template('jobs.html', user=github_user, jobs=tronci_jobs, repo_id=repo_id, slug=repo.slug)


#===================================================================================================
# NewJobAPI
#===================================================================================================
class NewJobAPI(MethodView):
    '''
    View responsible for providing a form to setup a job and save it.
    '''

    decorators = [user_required, forbidden_repo]

    def get(self, repo_id):
        form = JobForm(request.form)

        travispy = g.travispy
        repo = travispy.repo(repo_id)

        return render_template('job_form.html', form=form, repo_id=repo_id, command='new', slug=repo.slug)
