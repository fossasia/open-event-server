# Testing the database

Our project Open-Event has grown into a big, working application with a huge database set up in postgresql. It consists
of large number of tables and relations hence it becomes extremely important to test the database if there are any slow components
in it.

### The database tests

We have written tests which create a large number of events, sessions and users in order to simulate the real world application.
When the application is used there will be, no doubt, large number of database entries and hence it may happen that the database
queries slow down. Hence we have tested the database by simulating the environment with a large number of entries.


For testing events:

```sh
def test_db_events(self):
        with app.test_request_context():
            for i in range(1, 10000):
                event = ObjectMother.get_event()
                event.name = 'Event' + str(i)
                db.session.add(event)
            db.session.commit()
            url = url_for('sadmin_events.index_view')
            start = time.clock()
            self.app.get(url, follow_redirects=True)
            print time.clock() - start
            with open("output_events.txt", "w") as text_file:
                for query in get_debug_queries():
                    if query.duration >= ProductionConfig.DATABASE_QUERY_TIMEOUT:
                        text_file.write("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (
                            query.statement, query.parameters, query.duration, query.context))
                        text_file.write("\n")
```


In the above code the loop creates 10k events and adds it to the session. At the end of the loop all the events are added to the
database and committed. After this the url for the events page in Admin section is accessed using a GET query. We start a timer
to calculate the time taken in executing the query using the following

```sh
start = time.clock()
            self.app.get(url, follow_redirects=True)
            print time.clock() - start
```


Thus after that we create a txt file "output_events.txt" in which we record all the slow queries along with their information.

```sh
with open("output_events.txt", "w") as text_file:
                for query in get_debug_queries():
                    if query.duration >= ProductionConfig.DATABASE_QUERY_TIMEOUT:
                        text_file.write("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (
                            query.statement, query.parameters, query.duration, query.context))
                        text_file.write("\n")
```

We have similar tests for testing users and sessions

```sh
def test_db_sessions(self):
        with app.test_request_context():
            for i in range(1, 10000):
                session = ObjectMother.get_session()
                session.name = 'Session' + str(i)
                db.session.add(session)
            db.session.commit()
            url = url_for('sadmin_sessions.display_my_sessions_view')
            start = time.clock()
            self.app.get(url, follow_redirects=True)
            print time.clock() - start
            with open("output_session.txt", "w") as text_file:
                for query in get_debug_queries():
                    if query.duration >= ProductionConfig.DATABASE_QUERY_TIMEOUT:
                        text_file.write("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (
                            query.statement, query.parameters, query.duration, query.context))
                        text_file.write("\n")

    def test_db_users(self):
        with app.test_request_context():
            for i in range(1, 10000):
                user = ObjectMother.get_user()
                user.email = 'User' + str(i)
                db.session.add(user)
            db.session.commit()
            url = url_for('sadmin_users.index_view')
            start = time.clock()
            self.app.get(url, follow_redirects=True)
            print time.clock() - start
            with open("output_users.txt", "w") as text_file:
                for query in get_debug_queries():
                    if query.duration >= ProductionConfig.DATABASE_QUERY_TIMEOUT:
                        text_file.write("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (
                            query.statement, query.parameters, query.duration, query.context))
                        text_file.write("\n")

```


### Overall Testing

The above tests were written only for specific actions. However if we need to test the overall performance of the application
then we have some frameworks for testing it. We have used Profiling for determining how much time does each query call take
and which functions are slow to execute.

```sh
if app.config['TESTING']:
        # Profiling
        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
```

This gives a detailed information as to how much time is taken in executing each query or a request. This even checks
how much time is taken in loading the template pages.
