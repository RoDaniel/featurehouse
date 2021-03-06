from xpcom import components, verbose
"""
Interfaces we need to provide
** nsIWebBrowserChrome **
The nsIWebBrowserChrome interface corresponds to the top-level, outermost window containing an embedded Gecko web browser. You associate it with the WebBrowser through the nsIWebBrowser interface. It provides control over window setup and whether or not the window is modal. It must be implemented.
nsIEmbeddingSiteWindow
The nsIEmbeddingSiteWindow interface provides Gecko with the means to call up to the host to resize the window, hide or show it and set/get its title. It must be implemented.
** nsIWebProgressListener **
The nsIWebProgressListener interface provides information on the progress of loading documents. It is added to the WebBrowser through the nsIWebBrowser interface. It must be implemented. As of this writing (8/19/02), it is not frozen.
** nsISHistoryListener **
The nsISHistoryListener interface is implemented by embedders who wish to receive notifications about activities in session history. A history listener is notified when pages are added, removed and loaded from session history. It is associated with Gecko through the nsIWebBrowser interface. Implementation is optional.
** nsIContextMenuListener **
The nsIContextMenuListener interface is implemented by embedders who wish to receive notifications for context menu events, i.e. generated by a user right-mouse clicking on a link. It should be implemented on the web browser chrome object associated with the window for which notifications are required. When a context menu event occurs, the browser will call this interface if present. Implementation is optional.
** nsIPromptService **
The nsIPromptServices interface allows the embedder to override Mozilla's standard prompts: alerts, dialog boxes, and check boxes and so forth. The class that implements these embedder specific prompts must be registered with the Component Manager using the same CID and contract ID that the Mozilla standard prompt service normally uses. Implementation is optional. As of this writing (8/19/02), this interface is not frozen.
"""
nsIWebBrowserChrome    = components.interfaces.nsIWebBrowserChrome
nsIEmbeddingSiteWindow = components.interfaces.nsIEmbeddingSiteWindow
nsIWebProgressListener = components.interfaces.nsIWebProgressListener
nsISHistoryListener    = components.interfaces.nsISHistoryListener
nsIContextMenuListener = components.interfaces.nsIContextMenuListener
nsIPromptService       = components.interfaces.nsIPromptService
DEBUG = True
class WebBrowserChromeBase(object):
    """Base class that implements the
    nsIWebBrowserChrome interface
    Allowing gecko to control its window
    """
    _com_interfaces_ = (nsIWebBrowserChrome,)
    def __init__(self, webBrowser):
        """
        Pass it a reference to an nsIWebBrowser
        """
        self.webBrowser = webBrowser
    def setStatus(self, statusType, status):
        """
        Called when the status text in the chrome needs to be updated (e.g., when mousing over a link).
        C Decl:
            void nsIWebBrowserChrome::setStatus(in unsigned long statusType, in wstring status) 
        Parameters:
            statusType: What is setting the text. See Constants below for possible values.
            status: The status string. null is an acceptable value, meaning no status.
        Result:
            NS_OK if successful.
        Possible status vals:
            nsIWebBrowserChrome.STATUS_SCRIPT
            nsIWebBrowserChrome.STATUS_SCRIPT_DEFAULT
            nsIWebBrowserChrome.STATUS_LINK
        """
        if DEBUG:
            print 'setStatus', statusType, status
    def destroyBrowserWindow(self):
        """
        Destroys the window associated with the WebBrowser object.
        Syntax:
            void nsIWebBrowserChrome::destroyBrowserWindow() 
        Parameters:
            None.
        nsresult :
            NS_OK if successful.
        """
        if DEBUG:
            print 'destroyBrowserWindow'
        self.window.destroy()
    def sizeBrowserTo(self, aCX, aCY):
        """
        Resizes the chrome so that the browser will be the specified size.
        Syntax:
            void nsIWebBrowserChrome::sizeBrowserTo(in long aCX, in long aCY) 
        Parameters:
            aCX: The new width of the browser.
            aCY: The new height of the browser.
        nsresult:
            NS_OK if successful.
        """
        if DEBUG:
            print 'sizeBrowserTo', aCX, aCY
    def showAsModal(self):
        """
        Shows the window as a modal window.
        Syntax:
            void nsIWebBrowserChrome::showAsModal() 
        Parameters:
            None.
        nsresult:
            A result code specified in exitModalEventLoop below. Usually NS_OK if successful.
        """
        if DEBUG:
            print 'showAsModal'
    def isWindowModal(self):
        """
        Indicates if the window is currently executing a modal loop.
        Syntax:
            boolean nsIWebBrowserChrome::isWindowModal() 
        Parameters:
            None.
        Returns:
            TRUE if the window is modal.
            FALSE otherwise.
        """
        if DEBUG:
            print 'isWindowModal'
        return False
    def exitModalEventLoop(self, aStatus):
        """
        Exits a modal event loop if one is active. The implementation should also exit the loop if the window is destroyed.
        Syntax:
            void nsIWebBrowserChrome::exitModalEventLoop(in nsresult aStatus)
        Parameters:
            aStatus: The result code to return from showAsModal above.
        Returns:
            NS_OK if successful.
        """
        if DEBUG:
            print 'exitModalEventLoop', aStatus
    webBrowser = None
    chromeFlags = nsIWebBrowserChrome.CHROME_DEFAULT
class EmbeddingSiteWindowBase(object):
    """
    Implements nsIEmbeddingSiteWindow (for pygtk).
    The nsIEmbeddingSiteWindow interface provides Gecko with the means to
    call up to the host to resize the window, hide or show it and set/get
    its title. It must be implemented.
    This interface is implemented by the embedder to provide Gecko with the 
    means to call up to the host to resize the window, hide or show it and 
    set/get its title. This interface is scriptable except as noted below.
    """
    _com_interfaces_ = (nsIEmbeddingSiteWindow,)
    def __init__(self, window):
        """
        'window' is a pygtk window
        """
        self.window = window
    def setDimensions(self, flags, x, y, cx, cy):
        """
        Sets the dimensions for the window, both its position and size. The
        flags indicate what the caller wants to set and whether the size refers
        to the inner or outer area. The inner area refers to just the embedded
        area, wheras the outer area can also include any surrounding chrome,
        window frame, title bar, and so on.
        'flags' can contain:
        'nsIEmbeddingSiteWindow.DIM_FLAGS_POSITION' indicates that position of the top left corner of the outer area is required/specified.
        'nsIEmbeddingSiteWindow.DIM_FLAGS_SIZE_INNER' indicates that the size of the inner area is required/specified.
        Syntax:
            void nsIEmbeddingSiteWindow::setDimensions(
                in unsigned long flags,in long x,in long y, 
                in long cx, in long cy) 
        Parameters:
            flags: Combination of position, inner and outer size flags.
            x: Left hand corner of the outer area.
            y: Top corner of the outer area.
            cx: Width of the inner or outer area.
            cy: Height of the inner or outer area.
        nsresult:
        NS_OK if operation was performed correctly.
        NS_ERROR_UNEXPECTED if window could not be destroyed.
        NS_ERROR_INVALID_ARG for bad flag combination or illegal dimensions.
        """
        if flags & nsIEmbeddingSiteWindow.DIM_FLAGS_SIZE_INNER:
            pass
        else:
            self.window.move(x, y)
            self.window.resize(cx, cy)
    def getDimensions(self, flags):
        """
        Gets the dimensions of the window. The caller may pass nsnull for any value it is uninterested in receiving.
        Syntax:
            void nsIEmbeddingSiteWindow::getDimensions(
                in unsigned long flags,out long x,out long y,
                out long cx,out long cy) 
        Parameters:
            flags: Combination of position, inner and outer size flag .
            x: [out] Left hand corner of the outer area; or nsnull.
            y: [out]Top corner of the outer area; or nsnull.
            cx: [out] Width of the inner or outer area; or nsnull.
            cy: [out] Height of the inner or outer area; or nsnull.
        nsresult:
            (x, y, cx, cy) in python
            NS_OK if successful.
        """
        x, y = self.window.get_position()
        w, h = self.window.get_size()
        return x, y, w, h
    def setFocus(self):
        """
        Gives the window focus.
        Syntax:
            void nsIEmbeddingSiteWindow::setFocus()  
        Parameters:
            None.
        nsresult:
            NS_OK if successful
        """
        def get_visibility(self):
            return self._visibility 
        def set_visibility(self, value):
            self._visibility = value
        _visibility = False
        visibility = property(get_visibility, set_visibility, None, 'Gets and sets the visibility of the window.')
        def get_title(self):
            return self._title 
        def set_title(self, value):
            self._title = value
        _title = u''
        title = property(get_title, set_title, None, 'Gets and sets the title of the window.')
        def get_siteWindow(self):
            return self._siteWindow 
        _siteWindow = u''
        siteWindow = property(get_siteWindow, None, None, 'Gets the native window for the site\'s window.')
class WebProgressListenerBase(object):
    """
    The nsIWebProgressListener interface is implemented by clients wishing to
    listen in on the progress associated with the loading of asynchronous
    requests in the context of a nsIWebProgress instance as well as any child
    nsIWebProgress instances.  nsIWebProgress.idl describes the parent-child
    relationship of nsIWebProgress instances.
    Constants defined in nsIWebProgressListener:
    nsIWebProgressListener.STATE_START
    Progress state transition bits.
    These flags indicate the various states that documents and requests may transition through as they are being loaded.
    nsIWebProgressListener.STATE_REDIRECTING
    nsIWebProgressListener.STATE_TRANSFERRING
    nsIWebProgressListener.STATE_NEGOTIATING
    nsIWebProgressListener.STATE_STOP
    nsIWebProgressListener.STATE_IS_REQUEST
    Progress State type bits.
    These flags indicate whether the transition is occuring on a document or an individual request within the document.
    nsIWebProgressListener.STATE_IS_DOCUMENT
    nsIWebProgressListener.STATE_IS_NETWORK
    nsIWebProgressListener.STATE_IS_WINDOW
    nsIWebProgressListener.STATE_IS_INSECURE
    Security state bits.
    nsIWebProgressListener.STATE_IS_BROKEN
    nsIWebProgressListener.STATE_IS_SECURE
    nsIWebProgressListener.STATE_SECURE_HIGH
    nsIWebProgressListener.STATE_SECURE_MED
    nsIWebProgressListener.STATE_SECURE_LOW
    """
    _com_interfaces_ = (nsIWebProgressListener,)
    def onStateChange(self, aWebProgress, aRequest, aStateFlags, aStatus):
        """
        Notification indicating the state has changed for one of the requests associated with the document loaded.
        Syntax:
            void nsIWebProgressListener::onStateChange(
                    in nsIWebProgress aWebProgress,
                    in nsIRequest        aRequest,
                    in unsigned long  aStateFlags,
                    in nsresult        aStatus
                )      
        Parameters:
                aWebProgress The nsIWebProgress instance that fired the notification
                aRequest      The nsIRequest which has changed state.
                aStateFlags     Flags indicating the state change.
                aStatus      Error status code associated with the state change.
                             This parameter should be ignored unless the status
                             flag includes the STATE_STOP bit. The status code
                             will indicate success / failure of the request
                             associated with the state change.
        Result:
                NS_OK should always be returned. 
        """
        if DEBUG:
            print onStateChange, aWebProgress, aRequest, aStateFlags, aStatus
    def onProgressChange(self, aWebProgress, aRequest, aCurSelfProgress,
                         aMaxSelfProgress, aCurTotalProgress, aMaxTotalProgress):
        """
        Notification that the progress has changed for one of the requests being
        monitored.
        Syntax:
            void nsIWebProgressListener::onProgressChange(
                    in nsIWebProgress aWebProgress,
                    in nsIRequest        aRequest,
                    in long            aCurSelfProgress,
                    in long            aMaxSelfProgress,
                    in long            aCurTotalProgress,
                    in long            aMaxTotalProgress,
                )      
        Parameters:
                aWebProgress         The nsIWebProgress instance that fired the notification
                aRequest             The nsIRequest that has new progress.
                aCurSelfProgress     The current progress for aRequest.
                aMaxSelfProgress     The maximum progress for aRequest. If this
                                    value is not known then -1 is passed.
                aCurTotalProgress     The current progress for all the requests
                                    being monitored.
                aMaxTotalProgress     The total progress for all the requests
                                    being monitored. If this value is not known
                                    then -1 is passed.
        Returns:
                NS_OK should always be returned.
        """
        if DEBUG:
            print 'onProgressChange', aWebProgress, aRequest, aCurSelfProgress, aMaxSelfProgress, aCurTotalProgress, aMaxTotalProgress
    def onLocationChange(self):
        """
        Called when the window being watched changes the location that is currently.
        This is not when a load is requested, but rather once it is verified
        that the load is going to occur in the given window. For instance, a
        load that starts in a window might send progress and status messages,
        for the new site but it will not send the onLocationChange until we are
        sure we are loading this new page here.
        Syntax:
            void nsIWebProgressListener::onLocationChange      (       in nsIWebProgress         aWebProgress,
                    in nsIRequest        aRequest,
                    in nsIURI        location
                )      
        Parameters:
                location     The URI of the location that is being loaded.
        nsresult:
                NS_OK should always be returned. 
        """
        if DEBUG:
            print 'onLocationChange'
    def onStatusChange(self):
        """
        Notification that the status has changed.
        The status message is usually printed in the status bar of the browser.
        Syntax:
            void nsIWebProgressListener::onStatusChange      (       in nsIWebProgress         aWebProgress,
                    in nsIRequest        aRequest,
                    in nsresult        aStatus,
                    in wstring        aMessage
                )      
        Parameters:
                None
        nsresult:
                NS_OK should always be returned. 
        """
        if DEBUG:
            print 'onStatusChange'
    def onSecurityChange(self, aWebProgress, aRequest, state):
        """
        Notification called for security progress.
        This method will be called on security transitions (eg HTTP -> HTTPS,
        HTTPS -> HTTP, FOO -> https) and after document load completion. It
        might also be called if an error occurs during network loading.
        These notification will only occur if a security package is installed.
        Syntax:
            void nsIWebProgressListener::onSecurityChange(
                    in nsIWebProgress aWebProgress,
                    in nsIRequest        aRequest,
                    in unsigned long  state)      
        Parameters:
                None
        nsresult:
                NS_OK should always be returned. 
        """
        if DEBUG:
            print 'onSecurityChange', aWebProgress, aRequest, state
class HistoryListenerBase(object):
    """
    This interface must be implemented by an object that wishes to receive
    notifications about activities in History. A history listener will be
    notified when pages are added, removed and loaded from session history. A
    listener to session history can be registered using the interface
    nsISHistory. This interface is scriptable.
    """
    _com_interfaces_ = (nsISHistoryListener,)
    def OnHistoryNewEntry(self, aNewURI):
        """
        Notifies a listener when a new document is added to session history. New
        documents are added to the session history by the docshell when new
        pages are loaded in a frame or content area.
        Syntax:
            void nsISHistoryListener::OnHistoryNewEntry(in nsIURI aNewURI) 
        Parameters:
            aNewURI: The URI of the document to be added to session history.
        nsresult:
            NS_OK if notification was sent out successfully.
        """
        if DEBUG:
            print 'OnHistoryNewEntry', aNewURI
    def OnHistoryGoBack(self, aBackUR):
        """
        Notifies a listener when the user presses the 'back' button of the
        browser OR when the user attempts to go back one page in history through
        other means, either through scripting or by using nsIWebNavigation.
        Syntax:
            boolean nsISHistoryListener::OnHistoryGoBack(in nsIURI aBackURI) 
        Parameters:
            aBackURI: The URI of the previous page, which is the page to be loaded.
        nsresult:
            aReturn A boolean flag returned by the listener to indicate if the
            back operation is to be aborted or continued. If the listener
            returns TRUE, it indicates that the back operation can be continued.
            If the listener returns FALSE, then the back operation will be
            aborted. This is a mechanism by which the listener can control the
            user's interaction with history.
        """
        if DEBUG:
            print 'OnHistoryGoBack', aBackUR
    def OnHistoryGoForward(self, aForwardURI):
        """
        Notifies a listener when the user presses the 'forward' button of the
        browser OR when the user attempts to go forward one page in history
        through other means, either through scripting or by using
        nsIWebNavigation.
        Syntax:
            boolean nsISHistoryListener::OnHistoryGoForward(in nsIURI aForwardURI) 
        Parameters:
            aForwardURI: The URI of the next page, which is the page to be loaded.
        nsresult:
            aReturn A boolean flag returned by the listener to indicate if the
            forward operation is to be aborted or continued. If the listener
            returns TRUE, it indicates that the forward operation can be
            continued. If the listener returns FALSE, then the forward operation
            will be aborted. This is a mechanism by which the listener can
            control the user's interaction with history.
        """
        if DEBUG:
            print 'OnHistoryGoForward', aForwardURI
    def OnHistoryReload(self, aReloadURI, aReloadFlags):
        """
        Notifies a listener when the user presses the 'reload' button of the
        browser OR when the user attempts to reload the current document through
        other means, either through scripting or by using nsIWebNavigation.
        Syntax:
            boolean nsISHistoryListener::OnHistoryReload(
                in nsIURI aReloadURI, in unsigned long aReloadFlags) 
        Parameters:
            aReloadURI: The URI of the current document, which is to be reloaded.
            aReloadFlags: Flags that indicate how the document is to be
            refreshed; from cache, for example, or bypassing the cache and/or
            proxy server.
        nsresult:
            aReturn A boolean flag returned by the listener to indicate if the
            reload operation is to be aborted or continued. If the listener
            returns TRUE, it indicates that the reload operation can be
            continued. If the listener returns FALSE, then the reload operation
            will be aborted. This is a mechanism by which the listener can
            control the user's interaction with history.
        """
        if DEBUG:
            print 'OnHistoryReload', aReloadURI, aReloadFlags
    def OnHistoryGotoIndex(self, aIndex, aGotoURI):
        """
        Notifies a listener when the user visits a page using the 'Go' menu of
        the browser OR when the user attempts to go to a page at a particular
        index through other means, like from JavaScript or using
        nsIWebNavigation.
        Syntax:
            boolean nsISHistoryListener::OnHistoryGotoIndex(
                in long aIndex,
                in nsIURI aGotoURI) 
        Parameters:
            aIndex: The index in history of the document to be loaded.
            aGotoURI : The URI of the document to be loaded.
        nsresult:
            aReturn A boolean flag returned by the listener to indicate if the
            GotoIndex operation is to be aborted or continued. If the listener
            returns TRUE, it indicates that the GotoIndex operation can be
            continued. If the listener returns FALSE, then the GotoIndex
            operation will be aborted. This is a mechanism by which the listener
            can control the user's interaction with history.
        """
        if DEBUG:
            print 'OnHistoryGotoIndex', aIndex, aGotoURI
    def OnHistoryPurge(self, aNumEntries):
        """
        Notifies a listener when documents are removed from session history.
        Documents can be removed from session history for various reasons. For
        example to control the memory usage of the browser, to prevent users
        from loading documents from history, to erase evidence of prior page
        loads etc. To purge documents from session history call
        nsISHistory::PurgeHistory.
        Syntax:
            boolean nsISHistoryListener::OnHistoryPurge(
                in long aNumEntries) 
        Parameters:
            aNumEntries: The number of documents to be removed from session history.
        nsresult:
            aReturn A boolean flag returned by the listener to indicate if the
            purge operation is to be aborted or continued. If the listener
            returns TRUE, it indicates that the purge operation can be
            continued. If the listener returns FALSE, then the purge operation
            will be aborted. This is a mechanism by which the listener can
            control the user's interaction with history.
        """
        if DEBUG:
            print 'OnHistoryPurge', aNumEntries
class ContextMenuListenerBase(object):
    """
    An optional interface for embedding clients who wish to receive
    notifications for context menu events, i.e. generated by a user right-mouse
    clicking on a link. The embedder implements this interface on the WebBrowser
    chrome object associated with the window for which notifications are
    required. When a context menu event occurs, the browser will call this
    interface if present. This interface is not scriptable.
    Constants:
    nsIContextMenuListener.CONTEXT_NONE     No context.
    nsIContextMenuListener.CONTEXT_LINK     Context is a link element.
    nsIContextMenuListener.CONTEXT_IMAGE    Context is an image element.
    nsIContextMenuListener.CONTEXT_DOCUMENT Context is the whole document.
    nsIContextMenuListener.CONTEXT_TEXT     Context is a text area element.
    nsIContextMenuListener.CONTEXT_INPUT    Context is an input element.
    """
    _com_interfaces_ = (nsIContextMenuListener,)
    def onShowContextMenu(self, aContextFlags, aEvent, aNode):
        """
        Called when the browser receives a context menu event (i.e. the user is
        right-mouse clicking somewhere on the document). The combination of
        flags, events and nodes provided in the call indicate where and what was
        clicked on.
        The following table describes what context flags and node combinations
        are possible.
        aContextFlag                 aNode
        CONTEXT_LINK                 <A>
        CONTEXT_IMAGE                <IMG>
        CONTEXT_IMAGE | CONTEXT_LINK <IMG> with an <A>
        CONTEXT_INPUT                <INPUT>
        CONTEXT_TEXT                 <TEXTAREA>
        CONTEXT_DOCUMENT             <HTML>
        Syntax:
            void nsIContextMenuListener::onShowContextMenu(
                in unsigned long aContextFlags,
                in nsIDOMEvent   aEvent,
                in nsIDOMNode    aNode) 
        Parameters:
            aContextFlags: Flags indicating the kind of context. See below.
            aEvent:The DOM context menu event.
            aNode: The DOM node most relevant to the context.
        nsresult:
            NS_OK always.
        """
        if DEBUG:
            print 'onShowContextMenu', aContextFlags, aEvent, aNode
class PromptServiceBase(object):
    """
    Member Data Documentation
    Puts up a dialog with up to 3 buttons and an optional checkbox.
    Parameters:
        dialogTitle     
        text     
        buttonFlags     Title flags for each button.
        button0Title     Used when button 0 uses TITLE_IS_STRING
        button1Title     Used when button 1 uses TITLE_IS_STRING
        button2Title     Used when button 2 uses TITLE_IS_STRING
        checkMsg         null if no checkbox
        checkValue     
    Returns:
        buttonPressed
    Buttons are numbered 0 - 2. The implementation can decide whether the
    sequence goes from right to left or left to right. Button 0 will be the
    default button.
    A button may use a predefined title, specified by one of the constants
    below. Each title constant can be multiplied by a position constant to
    assign the title to a particular button. If BUTTON_TITLE_IS_STRING is used
    for a button, the string parameter for that button will be used. If the
    value for a button position is zero, the button will not be shown.
    nsIPromptService.BUTTON_POS_0
    nsIPromptService.BUTTON_POS_1
    nsIPromptService.BUTTON_POS_2
    nsIPromptService.BUTTON_TITLE_OK
    nsIPromptService.BUTTON_TITLE_CANCEL
    nsIPromptService.BUTTON_TITLE_YES
    nsIPromptService.BUTTON_TITLE_NO
    nsIPromptService.BUTTON_TITLE_SAVE
    nsIPromptService.BUTTON_TITLE_DONT_SAVE
    nsIPromptService.BUTTON_TITLE_REVERT
    nsIPromptService.BUTTON_TITLE_IS_STRING
    nsIPromptService.STD_OK_CANCEL_BUTTONS
    """
    _com_interfaces_ = (nsIPromptService,)
    def alert(self, parent, dialogTitle, text):
        """
        Puts up an alert dialog with an OK button. 
        Syntax:
            void nsIPromptService.alert(
                in nsIDOMWindow   parent,
                in wstring        dialogTitle,
                in wstring        text)      
        """
        if DEBUG:
            print 'alert', parent, dialogTitle, text
    def alertCheck(self, parent, dialogTitle, text, checkMsg, checkValue):
        """
        Puts up an alert dialog with an OK button and a message with a checkbox.
        Syntax:
            void nsIPromptService::alertCheck(
                in nsIDOMWindow   parent,
                in wstring        dialogTitle,
                in wstring        text,
                in wstring        checkMsg,
                inout boolean        checkValue)      
        """
        if DEBUG:
            print 'alertCheck', parent, dialogTitle, text, checkMsg, checkValue
    def confirm(self, parent, dialogTitle, text):
        """
        Puts up a dialog with OK and Cancel buttons.
        Syntax:
            boolean nsIPromptService::confirm(
                    in nsIDOMWindow   parent,
                    in wstring        dialogTitle,
                    in wstring        text)      
        Parameters:
                None
        nsresult:
                True for OK, False for Cancel 
        """
        if DEBUG:
            print 'confirm', parent, dialogTitle, text
    def confirmCheck(self, parent, dialogTitle, text, checkMsg, checkValue):
        """
        Puts up a dialog with OK and Cancel buttons, and a message with a single checkbox.
        Syntax:
            boolean nsIPromptService::confirmCheck(
                    in nsIDOMWindow   parent,
                    in wstring        dialogTitle,
                    in wstring        text,
                    in wstring        checkMsg,
                    inout boolean        checkValue,)      
            nsresult:
                True for OK, False for Cancel
        """
        if DEBUG:
            print 'confirmCheck', parent, dialogTitle, text, checkMsg, checkValue
    def confirmEx(self, parent, dialogTitle, text, buttonFlags, button0Title,
                  button1Title, button2Title, checkMsg, checkValue):
        """
        This is the doco text
        Syntax:
            PRInt32 nsIPromptService::confirmEx(
                    in nsIDOMWindow   parent,
                    in wstring        dialogTitle,
                    in wstring        text,
                    in unsigned long  buttonFlags,
                    in wstring        button0Title,
                    in wstring        button1Title,
                    in wstring        button2Title,
                    in wstring        checkMsg,
                    inout boolean        checkValue)  
        """
        if DEBUG:
            print 'confirmEx', parent, dialogTitle, text, buttonFlags, button0Title, button1Title, button2Title, checkMsg, checkValue
    def prompt(self, parent, dialogTitle, text, value, checkMsg, checkValue):
        """
        Puts up a dialog with an edit field and an optional checkbox.
        Syntax:
            boolean nsIPromptService::prompt(
                    in nsIDOMWindow   parent,
                    in wstring        dialogTitle,
                    in wstring        text,
                    inout wstring        value,
                    in wstring        checkMsg,
                    inout boolean        checkValue)      
        Parameters:
                dialogTitle     
                text     
                value     in: Pre-fills the dialog field if non-null out: If
                            result is true, a newly allocated string. If result
                            is false, in string is not touched.
                checkMsg     if null, check box will not be shown
                checkValue     
        nsresult:
                true for OK, false for Cancel 
        """
        if DEBUG:
            print 'prompt', parent, dialogTitle, text, value, checkMsg, checkValue
    def promptUsernameAndPassword(self, parent, dialogTitle, text, username,
                                  password, checkMsg, checkValue):
        """
        Puts up a dialog with an edit field, a password field, and an optional checkbox.
        Syntax:
            boolean nsIPromptService::promptUsernameAndPassword(
                    in nsIDOMWindow   parent,
                    in wstring        dialogTitle,
                    in wstring        text,
                    inout wstring        username,
                    inout wstring        password,
                    in wstring        checkMsg,
                    inout boolean        checkValue)      
        Parameters:
                dialogTitle     
                text     
                username     in: Pre-fills the dialog field if non-null out: If
                                result is true, a newly allocated string. If
                                result is false, in string is not touched.
                password     in: Pre-fills the dialog field if non-null out: If
                                result is true, a newly allocated string. If
                                result is false, in string is not touched.
                checkMsg     if null, check box will not be shown
                checkValue     
        nsresult:
                True for OK, False for Cancel 
        """
        if DEBUG:
            print 'promptUsernameAndPassword', parent, dialogTitle, text, username, password, checkMsg, checkValue
    def promptPassword(self, parent, dialogTitle, text, password, checkMsg):
        """
        Puts up a dialog with a password field and an optional checkbox.
        Syntax:
            boolean nsIPromptService::promptPassword(
                    in nsIDOMWindow   parent,
                    in wstring        dialogTitle,
                    in wstring        text,
                    inout wstring        password,
                    in wstring        checkMsg,
                    inout boolean        checkValue)
        Parameters:
                dialogTitle     
                text     
                password     in: Pre-fills the dialog field if non-null out: If
                                result is true, a newly allocated string. If
                                result is false, in string is not touched.
                checkMsg     if null, check box will not be shown
                checkValue     
        nsresult:
                true for OK, false for Cancel
        """
        if DEBUG:
            print 'promptPassword', parent, dialogTitle, text, password, checkMsg
    def select(self, parent, dialogTitle, text, count, selectList, outSelection):
        """
        Puts up a dialog box which has a list box of strings. 
        Syntax:
            boolean nsIPromptService::select(
                    in nsIDOMWindow   parent,
                    in wstring        dialogTitle,
                    in wstring        text,
                    in PRUint32        count,
                    [array, size_is(count)] in wstring        selectList,
                    out long        outSelection)
        """
        if DEBUG:
            print 'select', parent, dialogTitle, text, count, selectList, outSelection
class BrowserImpl(WebBrowserChromeBase, 
                  EmbeddingSiteWindowBase,
                  WebProgressListenerBase,
                  HistoryListenerBase,
                  ContextMenuListenerBase,
                  PromptServiceBase):
    _com_interfaces_ = (nsIWebBrowserChrome,
                        nsIEmbeddingSiteWindow,
                        nsIWebProgressListener,
                        nsISHistoryListener,
                        nsIContextMenuListener,
                        nsIPromptService)
    _reg_clsid_ = "{0d1962b7-e433-409e-ad91-f5884c46330e}"
    _reg_contractid_ = "EXE.BrowserImpl"
    def __init__(self, window, webBrowser):
        EmbeddingSiteWindowBase.__init__(self, window)
        WebBrowserChromeBase.__init__(self, webBrowser)
