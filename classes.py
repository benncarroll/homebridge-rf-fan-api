import pilight


class Light(object):
    """docstring for Light."""

    def __init__(self, signal_type, signal_arr):
        super(Light, self).__init__()
        self._type = signal_type
        self._signal_arr = signal_arr
        self._current_state = 0

    def getState(self):
        return self._current_state

    def setState(self, state):
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


class Fan(object):
    """docstring for Fan."""

    def __init__(self, accessory):
        super(Fan, self).__init__()
        self._signal_arr = accessory['fan']['signals']
        self._current_speed = 0
        self._current_power = 0
        self._num_speed = len(self._signal_arr) - 1
        self.light = None
        self.name = accessory['room']

        if accessory.get('light', False):
            self.light = Light(
                accessory['light']['type'],
                accessory['light']['signals']
            )

    def getSpeed(self, percent=False):
        speed = self._current_speed
        if percent:
            rough = (100 / self._num_speed) * self._current_speed
            speed = min([0, 25, 33, 50, 66, 75, 100],
                        key=lambda x: abs(x-rough))
        return speed

    def setSpeed(self, speed):
        if speed > self._num_speed:
            speed = round(speed / (100 / self._num_speed))
        self._current_speed = int(speed)
        return

    def getOn(self):
        return self._current_power

    def setOn(self, power):
        self._current_power = int(power)
        return

    def setState(self, sync):

        speed = sync["fan-speed"]
        power = sync["fan-on"]
        light = sync["light-on"]

        self.light.setState(light)

        self.setSpeed(speed)
        self.setOn(power)

        if self.getOn():
            pilight.sendCode(self._signal_arr[self.getSpeed()])
        else:
            pilight.sendCode(self._signal_arr[0])

        return True
