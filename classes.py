import pilight


class Light(object):
    """docstring for Light."""

    def __init__(self, type, signal_arr):
        super(Light, self).__init__()
        self._type = type
        self._signal_arr = signal_arr
        self._current_state = 0

    def getState(self):
        return self._current_state

    def setState(self, state):
        if not self.verifyState(state):
            return False
        state = int(state)

        if self._type == 'toggle':
            if self._current_state == state:
                return True
            signal = self._signal_arr[0]
        else:
            signal = self._signal_arr[state]

        pilight.sendCode(signal)
        self._current_state = state
        return True

    def verifyState(self, state):
        try:
            if str(int(state)) in '01':
                return True
        except:
            pass
        return False


class Fan(object):
    """docstring for Fan."""

    def __init__(self, accessory):
        super(Fan, self).__init__()
        self._signal_arr = accessory['fan']['signals']
        self._current_speed = 0
        self._num_speed = len(self._signal_arr) - 1
        self.light = None
        self.name = accessory['room']

        if accessory.get('light', False):
            self.light = Light(
                accessory['light']['type'],
                accessory['light']['signals']
            )

    def getState(self):
        return self._current_speed

    def setState(self, state):
        if not self.verifyState(state):
            return False
        state = int(state)

        pilight.sendCode(self._signal_arr[state])
        return True

    def hasLight(self):
        if self.light != None:
            return True
        else:
            return False

    def verifyState(self, state):
        vstr = ''
        for i in range(self._num_speed + 1):
            vstr += str(i)
            pass
        try:
            if str(int(state)) in vstr:
                return True
        except:
            pass
        return False
