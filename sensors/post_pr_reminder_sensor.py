import eventlet
from st2reactor.sensor.base import Sensor


class PostPRReminder(Sensor):
    def __init__(self, sensor_service, config):
        super(PostPRReminder, self).__init__(
            sensor_service=sensor_service, config=config
        )
        self._logger = self.sensor_service.get_logger(name=self.__class__.__name__)
        self._stop = False

    def setup(self):
        pass

    def run(self):
        while not self._stop:
            self._logger.debug("PostPRReminder dispatching trigger...")
            count = self.sensor_service.get_value("st2_cloud_chatops.count") or 0
            payload = {"channel": "chatops", "count": int(count) + 1}
            self.sensor_service.dispatch(
                trigger="st2_cloud_chatops.reminder_event", payload=payload
            )
            self.sensor_service.set_value("st2_cloud_chatops.count", payload["count"])
            eventlet.sleep(30)

    def cleanup(self):
        self._stop = True

    # Methods required for programmable sensors.
    def add_trigger(self, trigger):
        pass

    def update_trigger(self, trigger):
        pass

    def remove_trigger(self, trigger):
        pass
