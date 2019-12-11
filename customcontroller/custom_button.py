from customcontroller.extended_trigger import ExtendedTrigger

class CustomButton(ExtendedTrigger):
	""" This class provides a way to create a custom button with any bool function.
		You can pass in more than one trigger and all of them will be checked.
		"""

	triggers = None

	def __call__(self):
		"""Calls get() on this object.

		:returns: value of get()
		"""

		if self.triggers == None:
			raise RuntimeError("This object has not been initialized")
		return self.get()

	def __init__(self, *triggers):
		"""Creates a CustomButton with the triggers that are checked.

		:param *triggers: comma separated callables to check for
		"""

		if len(triggers) == 0:
			raise ValueError("No Triggers have been passed in!")

		for trigger in triggers:
			if not callable(trigger):
				raise ValueError("A trigger passed into this custom button is not a function!")

		self.triggers = triggers
		#super.__init__()

	def get(self):
		"""
		Checks if all triggers are True

		:returns: if all triggers are True
		"""

		for trigger in self.triggers:
			if not trigger():
				return False
		return True
