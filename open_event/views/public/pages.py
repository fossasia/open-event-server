from flask_admin import BaseView, expose


class BasicPagesView(BaseView):
    @expose('/', methods=('GET', 'POST'))
    def index(self):
        pass

    @expose('/how_it_works', methods=('GET', 'POST'))
    def how_it_works(self):
        title = "How it works"
        return self.render('/gentelella/guest/page.html', title=title)

    @expose('/pricing', methods=('GET', 'POST'))
    def pricing(self):
        title = "Pricing"
        return self.render('/gentelella/guest/page.html', title=title)

    @expose('/mobile_apps', methods=('GET', 'POST'))
    def mobile_apps(self):
        title = "Mobile Apps"
        return self.render('/gentelella/guest/page.html', title=title)

    @expose('/sitemap', methods=('GET', 'POST'))
    def sitemap(self):
        title = "SiteMap"
        return self.render('/gentelella/guest/page.html', title=title)

    @expose('/about', methods=('GET', 'POST'))
    def about(self):
        title = "About"
        return self.render('/gentelella/guest/page.html', title=title)

    @expose('/blog', methods=('GET', 'POST'))
    def blog(self):
        title = "Blog"
        return self.render('/gentelella/guest/page.html', title=title)

    @expose('/support', methods=('GET', 'POST'))
    def support(self):
        title = "Help"
        return self.render('/gentelella/guest/page.html', title=title)

    @expose('/press', methods=('GET', 'POST'))
    def press(self):
        title = "Press"
        return self.render('/gentelella/guest/page.html', title=title)

    @expose('/security', methods=('GET', 'POST'))
    def security(self):
        title = "Security"
        return self.render('/gentelella/guest/page.html', title=title)

    @expose('/developers', methods=('GET', 'POST'))
    def developers(self):
        title = "Developers"
        return self.render('/gentelella/guest/page.html', title=title)

    @expose('/privacy', methods=('GET', 'POST'))
    def privacy(self):
        title = "Privacy"
        return self.render('/gentelella/guest/page.html', title=title)

    @expose('/cookies', methods=('GET', 'POST'))
    def cookies(self):
        title = "Cookies"
        return self.render('/gentelella/guest/page.html', title=title)
