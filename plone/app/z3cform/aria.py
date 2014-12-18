from Products.Five import BrowserView


class AriaHelperView(BrowserView):

    def describedby(self):
        """Identifies the element that describes the field input.
        """
        if self.context.field.description and self.context.mode != 'hidden':
        	return 'formfield-%s-formHelp' % self.context.id
        return None

    def required(self):
        """Indicates that user input is required on the element before a form may be submitted.
        """
        return str(self.context.required and \
            self.context.mode == 'input').lower()
