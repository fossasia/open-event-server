class AppCreator(object):
    def __init__(self, api_link, app_name, email):
        self.api_link = api_link
        self.app_name = app_name
        self.email = email


class WebAppCreator(object):
    def __init__(self, api_link, app_name, email):
        super(WebAppCreator, self).__init__(api_link, app_name, email)

    def create(self):
        pass

    def __save(self):
        pass


class AndroidAppCreator(object):
    def __init__(self, api_link, app_name, email):
        super(AndroidAppCreator, self).__init__(api_link, app_name, email)

    def create(self):
        pass

    def __save(self):
        pass
