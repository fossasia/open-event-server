# Signals

Refer: http://flask.pocoo.org/docs/0.12/signals/ .

The Library used for signals is [blinker](https://github.com/jek/blinker), docs for which are [here](https://pythonhosted.org/blinker/)

### List of Signals:
- `event_json_modified` (core changes related to the event, excludes changes in speakers, microlocations, etc)
- `sessions_modified`
- `speakers_modified`
- `microlocations_modified`

### Conventions to follow

- Declare all your signals in `app/helpers/signals.py`, but do not put any signal handler in the said file. Each signal handler should be the file related to which it is performing its functionality.
- When sending signals, signals accept only one positional argument (the sender), rest have to be keyword arguments.
- Thus, for the sender, From http://flask.pocoo.org/docs/0.12/signals/#sending-signals,
  `Try to always pick a good sender. If you have a class that is emitting a signal, pass self as sender. If you are emitting a signal from a random function, you can pass current_app._get_current_object() as sender.`
- We will be using `current_app._get_current_object()` as sender throughout the project.

- **Signal handlers**:
  - When sending the signal, the signal may be sending lots of information, which your signal may or may not want.
  - Thus format your signal handler in the form of: ` def name(app, **kwargs): `
  - The above format will allow future devs to attach other extra information to the signal without affecting you existing handler. Also with this format, you will not be accepting (explicitly, of course) any parameters you don't need.

- **Design principles for signals**:
  - signals/signal handler should be independent of the function they reside in.
  - When sending the signal, if the code in the function after sending the signal depends on successful execution of the signal, use a function call instead.
  - Please provide separate unit tests for signals handlers, none of the signal handlers will be called via the signal in testing mode.
