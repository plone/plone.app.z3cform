from Products.Five import BrowserView


class AriaHelperView(BrowserView):

    def describedby(self):
    	if self.context.field.description and self.context.mode != 'hidden':
    		return 'formfield-%s-formHelp' % self.context.id
    	return None

    def required(self):
    	return str(self.context.required and \
    			self.context.mode == 'input').lower()
