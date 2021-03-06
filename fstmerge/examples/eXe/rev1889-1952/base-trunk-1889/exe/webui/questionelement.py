"""
QuestionElement is responsible for a block of option.  Used by MultichoiceBlock
"""
import logging
from exe.webui import common
log = logging.getLogger(__name__)
class QuestionElement(object):
    """
    QuestionElment is responsible for a block of question. 
    Used by CasestudyBlock.
    """
    def __init__(self, index, idevice, question):
        """
        Initialize
        'index' is our number in the list of questions
        'idevice' is a case study idevice
        'question' is a exe.engine.casestudyidevice.Question instance
        """
        self.index      = index
        self.id         = "q" + unicode(index) + "b" + idevice.id        
        self.idevice    = idevice
        self.question   = question
        self.quesId     = "quesQuestion" + unicode(index) + "b" + idevice.id
        self.feedbackId = "quesFeedback" + unicode(index) + "b" + idevice.id
    def process(self, request):
        """
        Process arguments from the web server.  Return any which apply to this
        element.
        """
        log.debug("process " + repr(request.args))
        if self.quesId in request.args:
            self.question.question = request.args[self.quesId][0]
        if self.feedbackId in request.args:
            self.question.feedback = request.args[self.feedbackId][0]
        if "action" in request.args and request.args["action"][0] == self.id:
            self.idevice.questions.remove(self.question)
    def renderEdit(self):
        """
        Returns an XHTML string for editing this question element
        """
        html  = "<tr><td><b>%s</b>\n" % _("Activity")
        html += common.elementInstruc(self.idevice.questionInstruc)
        html += common.richTextArea(self.quesId, self.question.question)
        html += "<b>%s</b>\n" % _("Feedback")
        html += common.elementInstruc(self.idevice.feedbackInstruc)
        html += common.richTextArea(self.feedbackId, self.question.feedback)
        html += "</td><td>\n"
        html += common.submitImage(self.id, self.idevice.id, 
                                   "/images/stock-cancel.png",
                                   _("Delete question"))
        html += "</td></tr>\n"
        return html
    def renderView(self):
        """
        Returns an XHTML string for viewing and previewing this question element
        """
        log.debug("renderView called")
        html  = self.question.question 
        if self.question.feedback <> "":
            html += '<div id="view%s" style="display:block;">' % self.id
            html += common.feedbackButton('btnshow' + self.id,
                        _(u"Click Here"),
                        onclick = "showAnswer('%s',1)" % self.id)
            html += '</div>'
            html += '<div id="hide%s" style="display:none;">' % self.id
            html += common.feedbackButton('btnhide' + self.id,
                        _(u"Hide"),
                        onclick = "showAnswer('%s',0)" % self.id)
            html += '</div>'
            html += '<div id="s%s" class="feedback" style=" ' % self.id
            html += 'display: none;">'
            html += self.question.feedback
            html += "</div><br/>\n"
        return html
