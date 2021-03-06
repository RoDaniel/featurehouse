"""
TrueFalseElement is responsible for a block of question. Used by TrueFalseBlock.
"""
import logging
from exe.webui         import common
from exe.webui.element import TextAreaElement
log = logging.getLogger(__name__)
class TrueFalseElement(object):
    """
    TrueFalseElement is responsible for a block of question. 
    Used by TrueFalseBlock.
    """
    def __init__(self, index, idevice, question):
        """
        Initialize
        """
        self.index      = index
        self.id         = unicode(index) + "b" + idevice.id        
        self.idevice    = idevice
        self.question   = question
        self.question_question = TextAreaElement(question.question)
        self.question_feedback = TextAreaElement(question.feedback)
        self.question_hint = TextAreaElement(question.hint)
        self.question_isCorrect = question.isCorrect
        self.questionId = "question"+ unicode(index) + "b" + idevice.id
        self.keyId      = "Key" + unicode(index) + "b" + idevice.id       
        self.feedbackId = "feedback" + unicode(index) + "b" + idevice.id 
        self.hintId     = "hint" + unicode(index) + "b" + idevice.id 
        self.question_question.id = self.questionId
        self.question_feedback.id = self.feedbackId
        self.question_hint.id = self.hintId
    def process(self, request):
        """
        Process arguments from the web server.  Return any which apply to this 
        element.
        """
        log.debug("process " + repr(request.args))
        if self.questionId in request.args:
            self.question_question.process(request)
        if self.hintId in request.args:
            self.question_hint.process(request)
        if self.keyId in request.args:
            if request.args[self.keyId][0] == "true":
                self.question_isCorrect = True 
                log.debug("question " + repr(self.question_isCorrect))
            else:
                self.question_isCorrect = False        
        if self.feedbackId in request.args:
            self.question_feedback.process(request)
        if "action" in request.args and request.args["action"][0] == self.id:
            self.idevice.questions.remove(self.question)
    def renderEdit(self):
        """
        Returns an XHTML string for editing this option element
        """
        html  = common.formField('richTextArea',_(u'Question:'),'',
                                self.questionId, self.idevice.questionInstruc,
                                self.question_question.field.content)
        html += _("True") + " " 
        html += common.option(self.keyId, self.question_isCorrect, "true") 
        html += _("False") + " " 
        html += common.option(self.keyId, not self.question_isCorrect, "false") 
        html += "<br/><br/>\n"
        html += common.elementInstruc(self.idevice.keyInstruc)
        html += common.formField('richTextArea',_(u'Feedback'),'',
                                self.feedbackId, self.idevice.feedbackInstruc,
                                self.question_feedback.field.content)
        html += common.formField('richTextArea',_(u'Hint'),'',
                                self.hintId, self.idevice.hintInstruc,
                                self.question_hint.field.content)
        html += common.submitImage(self.id, self.idevice.id, 
                                   "/images/stock-cancel.png",
                                   _("Delete question"))
        html += "<br/><br/>\n"
        return html
    def renderQuestionView(self):
        """
        Returns an XHTML string for viewing this question element
        """
        is_preview = 0
        html  = self.renderQuestion(is_preview)
        if self.question_hint: 
            html += u'<span '
            html += u'style="background-image:url(\'panel-amusements.png\');">'
            html += u'\n<a onmousedown="Javascript:updateCoords(event);'
            html += u'showMe(\'%s\', 350, 100);" ' % self.hintId
            html += u'style="cursor:help;align:center;vertical-align:middle;" '
            html += u'title="%s" \n' % _(u"Hint")
            html += u'href="javascript:void(0);">&nbsp;&nbsp;&nbsp;&nbsp;</a>'
            html += u'</span>'
            html += u'<div id="'+self.hintId+'" '
            html += u'style="display:none; z-index:99;">'
            html += u'<div style="float:right;" >'
            html += u'<img alt="%s" ' % _('Close')
            html += u'src="stock-stop.png" title="%s"' % _('Close')
            html += u" onmousedown=\"Javascript:hideMe();\"/></div>"
            html += u'<div class="popupDivLabel">'
            html += _(u"Hint")
            html += u'</div>\n'
            html += self.question_hint.renderView()
            html += u"</div>\n"
        return html
    def renderQuestionPreview(self):
        """
        Returns an XHTML string for previewing this question element
        """
        is_preview = 1
        html  = self.renderQuestion(is_preview)
        html += " &nbsp;&nbsp;\n"
        html += common.elementInstruc(self.question_hint.field.content, 
                                      "panel-amusements.png", "Hint")
        return html
    def renderQuestion(self, is_preview):
        """
        Returns an XHTML string for viewing and previewing this question element
        """
        log.debug("renderPreview called in the form of renderQuestion")
        html  = u"<br/><br/><b>" +unicode(self.index + 1) + ". " 
        if is_preview:
            html += self.question_question.renderPreview() + "</b><br/><br/>" 
        else: 
            html += self.question_question.renderView() + "</b><br/><br/>"
        html += _("True") + " " 
        html += self.__option(0, 2, "true") + " \n"
        html += _("False") + " " 
        html += self.__option(1, 2, "false") + "\n"
        return html
    def __option(self, index, length, true):
        """Add a option input"""
        html  = u'<input type="radio" name="option%s" ' % self.id
        html += u'id="%s%s" ' % (true, self.id)
        html += u'onclick="getFeedback(%d,%d,\'%s\',\'truefalse\')"/>' % (
                index, length, self.id)
        return html
    def renderFeedbackPreview(self):
        """
        Merely a quick and easy front-end to renderFeedbackView(),
        that sets the is_preview value to 1, true!
        Note: this won't really matter all that much, since these won't
        show up in exported printouts, BUT at least the image paths will be correct.
        """
        is_preview=1
        return self.renderFeedbackView(is_preview)
    def renderFeedbackView(self, is_preview=0):
        """
        return xhtml string for display this option's feedback
        """
        if is_preview:
            feedbackStr1 = _(u"Correct!") + " " + self.question_feedback.renderPreview()
        else: 
            feedbackStr1 = _(u"Correct!") + " " + self.question_feedback.renderView()
        if is_preview:
            feedbackStr2 = _(u"Incorrect!") + " " + self.question_feedback.renderPreview()
        else: 
            feedbackStr2 = _(u"Incorrect!") + " " + self.question_feedback.renderView()
        if not self.question_isCorrect:
            feedbackStr1, feedbackStr2 = feedbackStr2, feedbackStr1 
        feedbackId1 = "0" + "b" + self.id
        feedbackId2 = "1" + "b" + self.id
        html  = u'<div id="s%s" style="color: rgb(0, 51, 204);' % feedbackId1
        html += u'display: none;">' 
        html += feedbackStr1 + '</div>\n'
        html += u'<div id="s%s" style="color: rgb(0, 51, 204);' % feedbackId2
        html += u'display: none;">' 
        html += feedbackStr2 + '</div>\n'
        return html
