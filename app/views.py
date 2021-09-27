from flask import render_template, flash, redirect, session, url_for, request, g
from flask import make_response

from flask import abort

from app import app, db, admin
# call database model
from .models import User, Post, Follow,Comment,Role,Permission
# forms
from .forms import UserLoginForm, UserRegisterForm,PostForm,CommentForm
from .forms import PasswordResetForm,EditProfileForm,SearchForm,EidtProfilePicForm,SetModeratorForm
# app
from flask import current_app
from flask_login import LoginManager, current_user,login_user, login_required, logout_user
from app import login_manager
from werkzeug.urls import url_parse

# cookie duration time
from datetime import timedelta

# permission
from .models import Permission
# users with roles
from .role_decorators import admin_required,permission_required
from flask_admin.contrib.sqla import ModelView


from os import path
from sqlalchemy import func

from flask_sqlalchemy import get_debug_queries

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    app.logger.debug('load user by id %s', user_id)
    app.logger.info('load user by id %s', user_id)
    return user

@app.before_request
def before_request():
    if current_user.is_authenticated:
        app.logger.debug('current user has logined')
        # refresh latest visit time
        current_user.ping()
        app.logger.debug('refresh visit time of %s', current_user.username)
        app.logger.info('refresh visit time of %s', current_user.username)
        # get search form before request
        # g.search_form = SearchForm()
        # flask_whooshalchemyplus.index_one_model(Post)

@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['SLOW_DB_QUERY_TIME']:
            current_app.logger.warnig(
                'slow query: %s\nParameters: %s\nDuration: %f\nContext: %s\n'%
                (query.statement, query.parameters,query.duration,query.context)
            )
    return response

# root page
# get URL
@app.route("/")
def index():
    app.logger.debug("trigger function 'index'")
    app.logger.info("trigger function 'index'")
    posts=Post.query.order_by(Post.create_time.desc()).limit(5)
    app.logger.debug("assign pagination object")
    app.logger.debug('read data from model Post in database ')
    app.logger.info('read data from model Post in database ')
    return render_template('index.html',
                           title='homepage',
                           posts=posts
                           )


# register
@app.route('/register', methods=['GET', 'POST'])
def register():
    app.logger.debug("trigger function 'register'")
    app.logger.info("trigger function 'register'")
    # check current user is authenticated, yes, go to homepage
    if current_user.is_authenticated:
        app.logger.debug('user %s has already logined but trigger register',current_user)
        return redirect(url_for('index'))

    form = UserRegisterForm()

    if form.validate_on_submit():
        app.logger.debug('UserRegisterForm validate_on_submit')
        app.logger.info('UserRegisterForm validate_on_submit')
        # create an instance of database model 'Users'
        user = User(username=form.username.data,
                    email=form.email.data,
                     password=form.password.data)
        if user is None:
            app.logger.debug('create an instance failed')
            app.logger.error('create an instance failed')
        else:
            app.logger.debug('create an instance of model Post')
        db.session.add(user)
        app.logger.debug('add instance to session')
        db.session.commit()
        app.logger.debug('commit instance to database')
        app.logger.info('add UserRegisterForm data to database')
        flash('Successfully create an account!','ok')

        return redirect('/login')
        app.logger.debug("redirect to '/login' failed")
        app.logger.error("redirect to '/login' failed")
    return render_template('register.html', title='Register', form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    app.logger.debug("trigger function 'login'")
    app.logger.info("trigger function 'login'")
    form = UserLoginForm()
    # Determine whether the current user is verified,
    # and if it passes, return to the home page.
    if current_user.is_authenticated:
        app.logger.debug('user %s has already logined but trigger login',current_user.username)
        return redirect(url_for('index'))
    # validate form data
    if form.validate_on_submit():
        app.logger.debug('UserLoginForm validate_on_submit')
        app.logger.info('UserLoginForm validate_on_submit')
        # find user by username
        # user = User.query.filter_by(username=form.username.data).first()
        # find user by email
        user = User.query.filter_by(email=form.email.data).first()
        app.logger.debug("find instance by 'filter_by'")
        # if username exist & password correct
        # login
        if user is not None and user.verify_password(form.password.data):
            app.logger.debug('Verified user password')
            app.logger.info('Verified user password')
            login_user(user,form.remember_me.data)
            app.logger.debug("call function'login_user()'")
            # store the previous URL that user visited
            next = request.args.get('next')
            app.logger.debug("get url that user visited before login")
            # if address of next page not exist
            if next is None or not next.startswith('/'):
                next = url_for('index')
                app.logger.debug("set 'next' url to 'index'")
            return redirect(next)
            app.logger.debug("redirect to 'next' failed")
            app.logger.error("redirect to 'next' failed")
        else:
            app.logger.debug('can not find user in database')
            app.logger.warning('can not find user in database')
            flash('Invalid username or password','err')
        # set cookie time  default:31 days
        session.permanent = True
        # set cookie time 5 hours
        app.permanent_session_lifetime = timedelta(hours=5)

    # template for login page
    return render_template('login.html',title='login',form=form)


# logout user
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    app.logger.debug("trigger function 'logout'")
    app.logger.info("trigger function 'logout'")
    logout_user()
    app.logger.debug('logout user')
    app.logger.info('logout user')
    if current_user.is_authenticated:
        app.logger.debug('logout user failed')
        app.logger.error('logout user failed')
    else:
        app.logger.debug('logout user successfully')
        app.logger.info('logout user successfully')
        flash('You have been logged out','ok')
    return redirect(url_for('index'))


# 404 error
@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("trigger function 'page_not_found'")
    app.logger.debug('404 error')
    app.logger.warning('404 error')
    return render_template('404.html',title='Page Not Found'), 404
# 500 error
@app.errorhandler(500)
def internal_server_error(error):
    app.logger.debug("trigger function 'internal_sever_error'")
    app.logger.debug('500 error')
    app.logger.warning('500 error')
    return render_template('500.html',title='Internal Server Error'), 500

# 403 error
@app.errorhandler(403)
def forbidden_error(error):
    app.logger.debug("trigger function 'forbidden_error'")
    app.logger.debug('403 error')
    app.logger.warning('403 error')
    return render_template('403.html',title='Forbidden Error'), 500
# # ------------------------------------------

# board
@app.route('/user/<username>/')
@login_required
def user(username):
    app.logger.debug("trigger function 'user(username)'")
    app.logger.info("trigger function 'user(username)'")
    user = User.query.filter_by(username=username).first_or_404()
    app.logger.debug("find instance by 'filter_by'")
    app.logger.info("find instance by 'filter_by'")
    if user is None:
        app.logger.debug("no user satisfied 'filter_by'")
        app.logger.warning("no user satisfied 'filter_by'")
        abort(404)
    # posts = user.posts.order_by(Post.create_time.desc()).all()

    # pages
    # get page number from request.args
    # default page number  1
    # if type is not int, return page number 1
    page=request.args.get('page',1,type=int)
    # each page 10 posts
    pagination=user.posts.order_by(Post.create_time.desc()).paginate(
        page, per_page=10,error_out=False
    )
    app.logger.debug("assign pagination object")
    posts=pagination.items
    app.logger.debug("get pagination item")
    app.logger.info("get pagination item")

    return render_template('user.html',user=user,posts=posts,pagination=pagination)

# popular users
@app.route('/all_author')
def all_author():
    app.logger.debug("trigger function 'all_author()'")
    app.logger.info("trigger function 'all_author()'")
    page = request.args.get('page', 1, type=int)
    # each page 10 posts
    pagination = User.query.order_by(User.id.desc()).paginate(
        page, per_page=10, error_out=False
    )
    app.logger.debug("assign pagination object")
    authors = pagination.items
    app.logger.debug("get pagination item")
    app.logger.info("get pagination item")

    return render_template('all_author.html', user=user, authors=authors, pagination=pagination)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    app.logger.debug("trigger function 'edit_profile()'")
    app.logger.info("trigger function 'edit_profile()'")
    form=EditProfileForm()
    if form.validate_on_submit():
        app.logger.debug('EditProfileForm validate_on_submit')
        app.logger.info('EditProfielForm validate_on_submit')
        current_user.location=form.location.data
        app.logger.debug('add data to current user')
        app.logger.info('add data to current user')
        # add information to database
        db.session.add(current_user._get_current_object())
        app.logger.debug('add instance to session')
        db.session.commit()
        app.logger.debug('commit instance to database')
        app.logger.info('add EditProfileForm data to database')
        # app.logger.warning('add EditProfileForm data to database')
        flash('Your profile has been updated.','ok')
        return redirect(url_for('.edit_profile',username=current_user.username))
        app.logger.debug("redirect to 'edit_profile' failed")
        app.logger.error("redirect to 'edit_profile' failed")
    form.location.data=current_user.location
    app.logger.debug('current user data put on form')
    app.logger.info('current user data put on form')

    # form.about_me=current_user.about_me
    return render_template('edit_profile.html',form=form)

@app.route('/edit_profile_pic', methods=['GET', 'POST'])
@login_required
def edit_profile_pic():
    app.logger.debug("trigger function 'edit_profile_pic()'")
    app.logger.info("trigger function 'edit_profile_pic()'")
    form=EidtProfilePicForm()
    if form.validate_on_submit():
        app.logger.debug('EidtProfilePicForm validate_on_submit')
        app.logger.info('EidtProfilePicForm validate_on_submit')

        # browse avatar from computer
        file = request.files['avatar_upload']
        if file is None:
            app.logger.debug("file by 'request.file' failed")
            app.logger.error("file by 'request.file' failed")
        else:
            app.logger.debug("file by 'request.file' succeed")
            app.logger.info("file by 'request.file' succeed")
        fname = file.filename
        if fname is None:
            app.logger.debug("file name is none")
            app.logger.error("file name is none")
        else:
            app.logger.debug("get file name")
            app.logger.info("get file name")
        UPLOAD_FOLDER = current_app.config['UPLOAD_FOLDER']
        if UPLOAD_FOLDER is None:
            app.logger.debug("upload url is none")
            app.logger.error("upload url is none")
        else:
            app.logger.debug("get upload url")
            app.logger.info("get upload url")
        ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
        flag = '.' in fname and fname.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
        if not flag:
            app.logger.debug("Wrong file type")
            app.logger.warning("Wrong file type")
            app.logger.debug("the filename suffix after '.' is not in allowed labels")
            flash('Wrong file type','error')

        # saving file & naming of uploaded file
        file.save('{}{}_{}'.format(UPLOAD_FOLDER, current_user.username,fname))
        app.logger.debug("save file with formatted name")
        current_user.real_avatar = '/static/img/avatar_uploads/{}_{}'.format(current_user.username,fname)
        if path.exists(current_user.real_avatar):
            app.logger.debug("upload file exisits")
            app.logger.info("upload file exisits")
        else:
            app.logger.debug("upload file not exisit")
            app.logger.error("upload file not exisit")
        # add information to database
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.','ok')
        return redirect(url_for('.edit_profile_pic',username=current_user.username))
    # form.location.data=current_user.location
    # form.about_me=current_user.about_me
    return render_template('edit_profile_pic.html',form=form)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    app.logger.debug("trigger function 'reset password()'")
    app.logger.info("trigger function 'reset password()'")
    # # if user is logined, deny the operation
    # if not current_user.is_anonymous:
    #     return redirect(url_for('.index'))
    # reset password
    form= PasswordResetForm()
    if form.validate_on_submit():
        app.logger.debug('PasswordResetForm validate_on_submit')
        app.logger.info('PasswordResetForm validate_on_submit')
        # check original password
        if current_user.verify_password(form.old_password.data):
            app.logger.debug('Verified user password')
            app.logger.info('Verified user password')
            current_user.password = form.password.data
            app.logger.debug('Set current user password')
            app.logger.info('Set current user password')
            db.session.add(current_user._get_current_object())
            app.logger.debug('add instance to session')
            db.session.commit()
            app.logger.debug('commit instance to database')
            app.logger.info('add PasswordResetForm data to database')
            # app.logger.warning('add PasswordResetForm data to database')
            flash('Your password has been updated.','ok')
            return redirect(url_for('.index'))
        else:
            app.logger.debug('password is wrong')
            app.logger.warning('password is wrong')
            flash('Wrong password.','err')
    return render_template("reset_password.html", form=form)


@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    app.logger.debug("trigger function 'create_post()'")
    app.logger.info("trigger function 'create_post()'")
    form = PostForm()
    if form.validate_on_submit():
        app.logger.debug('PostForm validate_on_submit')
        app.logger.info('PostForm validate_on_submit')
    # if current_user.can(Permission.WRITE) and form.validate_on_submit():
        author = current_user.id
        post = Post(title=form.title.data,
                    body=form.body.data,
                    author_id=author
                    )
        if post is None:
            app.logger.debug('create an instance failed')
            app.logger.error('create an instance failed')
        else:
            app.logger.debug('create an instance of model Post')
            app.logger.info('create an instance of model Post')
        db.session.add(post)
        app.logger.debug('add instance to session')
        db.session.commit()
        app.logger.debug('commit instance to database')
        app.logger.info('add PostForm data to database')
        app.logger.warning('add PostForm data to database')

        return redirect(url_for('.user', username=current_user.username))
        app.logger.debug("redirect to '/user/username' failed")
        app.logger.error("redirect to '/user/username' failed")

    return render_template('create_post.html', form=form)

@app.route('/delete_post/<int:id>')
@login_required
def delete_post(id):
    app.logger.debug("trigger function 'delete_post(id)'")
    app.logger.info("trigger function 'delete_post(id)'")
    post = Post.query.get(id)
    db.session.delete(post)
    if Post.query.get(id) is None:
        app.logger.debug("delete Post data in session")
        app.logger.info("delete Post data in session")
        app.logger.warnig("delete Post data in session")
    else:
        app.logger.debug("delete Post data failed")
        app.logger.error("delete Post data failed")

    db.session.commit()
    app.logger.debug("commit delete data operation to dataset")
    app.logger.info("commit delete data operation to dataset")
    return redirect(url_for('.user', username=current_user.username))

@app.route('/all_posts')
def all_posts():
    app.logger.debug("trigger function 'all_posts()'")
    app.logger.info("trigger function 'all_posts()'")
    # if type is not int, return page number 1
    page = request.args.get('page', 1, type=int)
    # each page 10 posts
    pagination = Post.query.order_by(Post.create_time.desc()).paginate(
        page, per_page=10, error_out=False
    )
    app.logger.debug("assign pagination object")
    posts = pagination.items
    app.logger.debug("get pagination item")
    app.logger.info("get pagination item")
    return render_template('all_posts.html',posts=posts, pagination=pagination)

@app.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    app.logger.debug("trigger function 'post(id)'")
    app.logger.info("trigger function 'post(id)'")
    post = Post.query.get_or_404(id)
    app.logger.debug("get Post instance by id")
    form = CommentForm()
    if form.validate_on_submit():
        app.logger.debug('CommentForm validate_on_submit')
        app.logger.info('CommentForm validate_on_submit')
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        if comment is None:
            app.logger.debug('create an instance failed')
            app.logger.error('create an instance failed')
        else:
            app.logger.debug('create an instance of model Comment')
            app.logger.info('create an instance of model Comment')
        db.session.add(comment)
        app.logger.debug('add instance to session')
        db.session.commit()
        app.logger.debug('commit instance to database')
        app.logger.info('add CommentForm data to database')
        app.logger.warning('add CommentForm data to database')
        flash('Your comment has been published.','ok')
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) // 10 + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=10,
        error_out=False)
    app.logger.debug("assign pagination object")
    comments = pagination.items
    app.logger.debug("get pagination item")
    app.logger.info("get pagination item")

    # return render_template('post.html',posts=[post],title='Post')
    return render_template('post.html',title='Post',posts=[post], form=form,
                           comments=comments, pagination=pagination)

@app.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    app.logger.debug("trigger function 'edit_post(id)'")
    app.logger.info("trigger function 'edit_post(id)'")
    post = Post.query.get_or_404(id)
    if user is None:
        app.logger.debug('create an instance failed')
        app.logger.error('create an instance failed')
    else:
        app.logger.debug('create an instance of model Post')
        app.logger.info('create an instance of model Post')
    # if current_user != post.author and \
    #         not current_user.can(Permission.ADMIN):
    if current_user != post.author:
        app.logger.debug('current user has no permission to edit the post')
        app.logger.info('current user has no permission to edit the post')
        abort(403)
    form = PostForm()
    form.title.data = post.title
    if form.title.data is None:
        app.logger.debug('assign data failed')
        app.logger.error('create an instance failed')
    if form.validate_on_submit():
        app.logger.debug('PostForm validate_on_submit')
        app.logger.info('PostForm validate_on_submit')
        post.body = form.body.data
        if post.body is None:
            app.logger.debug('assign empty post body')
            app.logger.warning('assign empty post body')
        app.logger.debug('create an instance of model Post')
        db.session.add(post)
        app.logger.debug('add instance to session')
        db.session.commit()
        app.logger.debug('commit instance to database')
        app.logger.info('add PostForm data to database')
        # app.logger.warning('add PostForm data to database')

        flash('The post has been updated.','ok')
        return redirect(url_for('.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form, title='Edit Post')

@app.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    app.logger.debug("trigger function 'follow(username)'")
    app.logger.info("trigger function 'follow(username)'")
    user = User.query.filter_by(username=username).first()
    if user is None:
        app.logger.debug("no user satisfied 'filter_by'")
        # app.logger.info("no user satisfied 'filter_by'")
        app.logger.error("no user satisfied 'filter_by'")
        flash('Invalid user.','err')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        app.logger.debug("current user follows %s",user.username)
        app.logger.warning("current user follows %s",user.username)
        flash('You have already followed this user.','warning')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    if current_user.is_following(user):
        app.logger.debug("current user now follows %s", user.username)
        app.logger.info("current user now follows %s", user.username)
    else:
        app.logger.debug("current user not follow %s", user.username)
        app.logger.error("current user not follow %s", user.username)
    db.session.commit()
    app.logger.debug('commit instance to database')
    app.logger.info('add user follow data to database')
    # app.logger.warning('add user follow data to database')
    flash('You are now following %s.' % username,'ok')
    return redirect(url_for('.user', username=username))

@app.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    app.logger.debug("trigger function 'unfollow(username)'")
    app.logger.info("trigger function 'unfollow(username)'")
    user = User.query.filter_by(username=username).first()
    if user is None:
        app.logger.debug("no user satisfied 'filter_by'")
        # app.logger.info("no user satisfied 'filter_by'")
        app.logger.waring("no user satisfied 'filter_by'")
        flash('Invalid user.','err')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        app.logger.debug("current user not follow %s", user.username)
        app.logger.info("current user not follow %s", user.username)
        flash('You are not following this user.','warning')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    if current_user.is_following(user):
        app.logger.debug("current user follows %s", user.username)
        app.logger.warning("current user follows %s", user.username)
    else:
        app.logger.debug("current user now not follow %s", user.username)
        app.logger.info("current user now not follow %s", user.username)
    db.session.commit()
    app.logger.debug('commit instance to database')
    app.logger.info('add user follow data to database')
    # app.logger.warning('add user follow data to database')
    flash('You are not following %s anymore.' % username,'ok')
    return redirect(url_for('.user', username=username))


@app.route('/follower/<username>')
def follower(username):
    app.logger.debug("trigger function 'follower(username)'")
    app.logger.info("trigger function 'follower(username)'")
    user = User.query.filter_by(username=username).first()
    if user is None:
        app.logger.debug("no user satisfied 'filter_by'")
        app.logger.info("no user satisfied 'filter_by'")

        flash('Invalid user.','err')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.follower.paginate(
        page, per_page=10,
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('follower.html', user=user, title="Followers of",
                           endpoint='.follower', pagination=pagination,
                           follows=follows)

@app.route('/followed_by/<username>')
def followed_by(username):
    app.logger.debug("trigger function 'followed_by(username)'")
    app.logger.info("trigger function 'followed_by(username)'")
    user = User.query.filter_by(username=username).first()
    if user is None:
        app.logger.debug("no user satisfied 'filter_by'")
        app.logger.info("no user satisfied 'filter_by'")
        flash('Invalid user.','err')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=10,
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('follower.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)

@app.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    app.logger.debug("trigger function 'moderate()'")
    app.logger.info("trigger function 'moderate()'")
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=10,
        error_out=False)
    comments = pagination.items
    if comments is None:
        print('comments none')
    app.logger.debug("get pagination item")
    app.logger.info("get pagination item")
    return render_template('moderate.html', comments=comments,
                           pagination=pagination,
                           page=page)


@app.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    app.logger.debug("trigger function 'moderate_enable(id)'")
    app.logger.info("trigger function 'moderate_enable(id)'")
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    app.logger.debug('add instance to session')
    db.session.commit()
    app.logger.debug('commit instance to database')
    app.logger.info('add comment data to database')
    # next = request.args.get('next')
    # app.logger.debug("get url that user visited before enable comment")
    # # app.logger.warning('add comment data to database')
    # # if address of next page not exist
    # if next is None or not next.startswith('/'):
    #     next = url_for('.all_comments')
    #     app.logger.debug("set 'next' url to 'all_comments'")
    # return redirect(next)

    return redirect(url_for('.all_comments',
                            page=request.args.get('page', 1, type=int)))


@app.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    app.logger.debug("trigger function 'moderate_disable(id)'")
    app.logger.info("trigger function 'moderate_disable(id)'")
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    app.logger.debug('add instance to session')
    db.session.commit()
    app.logger.debug('commit instance to database')
    app.logger.info('add comment data to database')
    # next = request.args.get('next')
    # app.logger.debug("get url that user visited before diable comment")
    # # if address of next page not exist
    # if next is None or not next.startswith('/'):
    #     next = url_for('.all_comments')
    #     app.logger.debug("set 'next' url to 'all_comments'")
    # return redirect(next)
    # app.logger.debug("redirect to 'next' failed")
    # app.logger.error("redirect to 'next' failed")
    # app.logger.warning('add comment data to database')
    return redirect(url_for('.all_comments',
                            page=request.args.get('page', 1, type=int)))

@app.route('/search', methods=['GET', 'POST'])
def search():
    app.logger.debug("trigger function 'search()'")
    app.logger.info("trigger function 'search()'")
    if not request.form['search']:
        app.logger.debug("no input for search")
        app.logger.info("no input for search")
        return redirect(url_for('index'))
    app.logger.debug("have input for search")
    app.logger.info("have input for search")
    return redirect(url_for('search_results', query=request.form['search']))

@app.route('/search_results/<query>')
def search_results(query):
    app.logger.debug("trigger function 'create_post()'")
    app.logger.info("trigger function 'create_post()'")
    # results = Post.query.whoosh_search(query, app.config['MAX_SEARCH_RESULTS'],like=True).all()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.whoosh_search(query, like=True).paginate(
        page, per_page=10,
        error_out=False)
    app.logger.debug("assign pagination object")
    results = pagination.items
    if results is None:
        app.logger.debug("get empty pagination item")
        app.logger.info("get empty pagination item")
    else:
        app.logger.debug("get pagination item")
        app.logger.info("get pagination item")
    return render_template('search_results.html',
                            query = query,
                            results = results,
                            pagination=pagination
                         )


@app.route('/delete_comment/<int:id>')
@login_required
def delete_comment(id):
    app.logger.debug("trigger function 'delete_comment(id)'")
    app.logger.info("trigger function 'delete_comment(id)'")
    comment = Comment.query.get(id)
    postid = comment.post_id
    db.session.delete(comment)
    if Comment.query.get(id) is None:
        app.logger.debug("delete Comment data in session")
        app.logger.info("delete Comment data in session")
        app.logger.warnig("delete Comment data in session")
    else:
        app.logger.debug("delete Comment data failed")
        app.logger.error("delete Comment data failed")

    db.session.commit()
    app.logger.debug("commit delete data operation to dataset")
    app.logger.info("commit delete data operation to dataset")
    return redirect(url_for('.post',id = postid))
@app.route('/all_comments')
def all_comments():
    app.logger.debug("trigger function 'all_comments()'")
    app.logger.info("trigger function 'all_comments()'")
    posts=Post.query.order_by(Post.create_time.desc()).all()
    # if type is not int, return page number 1
    page = request.args.get('page', 1, type=int)
    # each page 10 posts
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=10, error_out=False
    )
    app.logger.debug("assign pagination object")
    comments = pagination.items
    app.logger.debug("get pagination item")
    app.logger.info("get pagination item")
    return render_template('all_comments.html',
                           comments =comments,
                           pagination=pagination,
                           posts=posts)

# ---------------------------------------------

# reduce login operation with validator
# only administrator can enter the backstage
@app.route('/access_admin')
@login_required
@admin_required
def for_admin_only():
    app.logger.debug("trigger function for_admin_only()")
    app.logger.info("trigger function for_admin_only()")
    return redirect('/admin/')

@app.route('/set_moderator', methods=['GET', 'POST'])
@login_required
@admin_required
def set_moderator():
    app.logger.debug("trigger function set_moderator()")
    app.logger.info("trigger function set_moderator()")
    form = SetModeratorForm()
    if form.validate_on_submit():
        email=form.email.data
        moderator = User.query.filter_by(email=email).first()
        if moderator is None:
            app.logger.debug("can not find user by 'filter_by'")
            app.logger.warning("can not find user by 'filter_by'")
        else:
            app.logger.debug("find user by email")
            app.logger.info("find user by email")
        moderator_role = Role.query.filter_by(name='Moderator').first()
        moderator.role_id = moderator_role.id
        # moderator.role_id = 3
        if moderator.can(Permission.MODERATE) and not moderator.can(Permission.ADMIN):
            app.logger.debug("set moderator")
            app.logger.info("set moderator")
        else:
            app.logger.debug("set moderator failed")
            app.logger.warning("set moderator failed")

        db.session.add(moderator)
        app.logger.debug('add instance to session')
        db.session.commit()
        app.logger.debug('commit instance to database')
        app.logger.info('add PostForm data to database')
        flash('Set Moderator Successfully!','ok')

    return render_template('set_moderator.html',form=form, title='Set Moderator')