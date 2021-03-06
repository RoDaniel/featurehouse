import re
import sys
import time
import email
import types
import socket
import thread
import imaplib
import unittest
import asyncore
import StringIO
import sb_test_support
sb_test_support.fix_sys_path()
from spambayes import message
from spambayes import Dibbler
from spambayes.Options import options
from spambayes.classifier import Classifier
from sb_imapfilter import run, BadIMAPResponseError, LoginFailure
from sb_imapfilter import IMAPSession, IMAPMessage, IMAPFolder, IMAPFilter
IMAP_PORT = 8143
IMAP_USERNAME = "testu"
IMAP_PASSWORD = "testp"
IMAP_FOLDER_LIST = ["INBOX", "unsure", "ham_to_train", "spam",
                    "spam_to_train"]
SB_ID_1 = "test@spambayes.invalid"
SB_ID_2 = "14102004"
IMAP_MESSAGES = {
    101 : """Subject: Test\r
Message-ID: <%s>\r
\r
Body test.""" % (SB_ID_1,),
    102 : """Subject: Test2\r
Message-ID: <%s>\r
%s: %s\r
\r
Another body test.""" % (SB_ID_1, options["Headers", "mailid_header_name"],
                         SB_ID_2),
    103 : """Received: from noisy-2-82-67-182-141.fbx.proxad.net(82.67.182.141)
 via SMTP by mx1.example.com, id smtpdAAAzMayUR; Tue Apr 27 18:56:48 2004
Return-Path: " Freeman" <XLUPSYGSHLBAPN@runbox.com>
Received: from  rly-xn05.mx.aol.com (rly-xn05.mail.aol.com [172.20.83.138]) by air-xn02.mail.aol.com (v98.10) with ESMTP id MAILINXN22-6504043449c151; Tue, 27 Apr 2004 16:57:46 -0300
Received: from 132.16.224.107 by 82.67.182.141; Tue, 27 Apr 2004 14:54:46 -0500
From: " Gilliam" <.@doramail.com>
To: To: user@example.com
Subject: Your Source For Online Prescriptions....Soma-Watson..VALIUM-Roche    .		
Date: Wed, 28 Apr 2004 00:52:46 +0500
Mime-Version: 1.0
Content-Type: multipart/alternative;
        boundary=""
X-Mailer: AOL 7.0 for Windows US sub 118
X-AOL-IP: 114.204.176.98
X-AOL-SCOLL-SCORE: 1:XXX:XX
X-AOL-SCOLL-URL_COUNT: 2
Message-ID: <@XLUPSYGSHLBAPN@runbox.com>
--
Content-Type: text/html;
        charset="iso-8859-1"
Content-Transfer-Encoding: quoted-printable
<strong><a href=3D"http://www.ibshels454drugs.biz/c39/">ENTER HERE</a> to
ORDER MEDS Online, such as XANAX..VALIUM..SOMA..Much MORE SHIPPED
OVERNIGHT,to US and INTERNATIONAL</strong>
---
""",
    104 : """Subject: Test2\r
\r
Yet another body test.""",
    }
IMAP_UIDS = {1 : 101, 2: 102, 3:103, 4:104}
UNDELETED_IDS = (1,2)
class TestListener(Dibbler.Listener):
    """Listener for TestIMAP4Server."""
    def __init__(self, socketMap=asyncore.socket_map):
        Dibbler.Listener.__init__(self, IMAP_PORT, TestIMAP4Server,
                                  (socketMap,), socketMap=socketMap)
FAIL_NEXT = False
class TestIMAP4Server(Dibbler.BrighterAsyncChat):
    """Minimal IMAP4 server, for testing purposes.  Accepts a limited
    subset of commands, and also a KILL command, to terminate."""
    def __init__(self, clientSocket, socketMap):
        Dibbler.BrighterAsyncChat.__init__(self)
        Dibbler.BrighterAsyncChat.set_socket(self, clientSocket, socketMap)
        self.set_terminator('\r\n')
        self.okCommands = ['NOOP', 'LOGOUT', 'CAPABILITY', 'KILL']
        self.handlers = {'LIST' : self.onList,
                         'LOGIN' : self.onLogin,
                         'SELECT' : self.onSelect,
                         'FETCH' : self.onFetch,
                         'SEARCH' : self.onSearch,
                         'UID' : self.onUID,
                         'APPEND' : self.onAppend,
                         'STORE' : self.onStore,
                         }
        self.push("* OK [CAPABILITY IMAP4REV1 AUTH=LOGIN] " \
                  "localhost IMAP4rev1\r\n")
        self.request = ''
        self.next_id = 0
        self.in_literal = (0, None)
    def collect_incoming_data(self, data):
        """Asynchat override."""
        if self.in_literal[0] > 0:
            self.request = "%s\r\n%s" % (self.request, data)
        else:
            self.request = self.request + data
    def found_terminator(self):
        """Asynchat override."""
        global FAIL_NEXT
        if self.in_literal[0] > 0:
            if len(self.request) >= self.in_literal[0]:
                self.push(self.in_literal[1](self.request,
                                             *self.in_literal[2]))
                self.in_literal = (0, None)
                self.request = ''
            return
        id, command = self.request.split(None, 1)
        if FAIL_NEXT:
            FAIL_NEXT = False
            self.push("%s NO Was told to fail.\r\n" % (id,))
        if ' ' in command:
            command, args = command.split(None, 1)
        else:
            args = ''
        command = command.upper()
        if command in self.okCommands:
            self.push("%s OK (we hope)\r\n" % (id,))
            if command == 'LOGOUT':
                self.close_when_done()
            if command == 'KILL':
                self.socket.shutdown(2)
                self.close()
                raise SystemExit()
        else:
            handler = self.handlers.get(command, self.onUnknown)
            self.push(handler(id, command, args, False))  # Or push_slowly for testing
        self.request = ''
    def push_slowly(self, response):
        """Useful for testing."""
        for c in response:
            self.push(c)
            time.sleep(0.02)
    def onLogin(self, id, command, args, uid=False):
        """Log in to server."""
        username, password = args.split(None, 1)
        username = username.strip('"')
        password = password.strip('"')
        if username == IMAP_USERNAME and password == IMAP_PASSWORD:
            return "%s OK [CAPABILITY IMAP4REV1] User %s " \
                   "authenticated.\r\n" % (id, username)
        return "%s NO LOGIN failed\r\n" % (id,)
    def onList(self, id, command, args, uid=False):
        """Return list of folders."""
        base = '\r\n* LIST (\\NoInferiors \\UnMarked) "/" '
        return "%s%s\r\n%s OK LIST completed\r\n" % \
               (base[2:], base.join(IMAP_FOLDER_LIST), id)
    def onStore(self, id, command, args, uid=False):
        return "%s OK STORE completed\r\n" % (id,)
    def onSelect(self, id, command, args, uid=False):
        exists = "* %d EXISTS" % (len(IMAP_MESSAGES),)
        recent = "* 0 RECENT"
        uidv = "* OK [UIDVALIDITY 1091599302] UID validity status"
        next_uid = "* OK [UIDNEXT 23] Predicted next UID"
        flags = "* FLAGS (\Answered \Flagged \Deleted \Draft \Seen)"
        perm_flags = "* OK [PERMANENTFLAGS (\* \Answered \Flagged " \
                     "\Deleted \Draft \Seen)] Permanent flags"
        complete = "%s OK [READ-WRITE] SELECT completed" % (id,)
        return "%s\r\n" % ("\r\n".join([exists, recent, uidv, next_uid,
                                        flags, perm_flags, complete]),)
    def onAppend(self, id, command, args, uid=False):
        folder, args = args.split(None, 1)
        if ')' in args:
            flags, args = args.split(')', 1)
            flags = flags[1:]
        unused, date, args = args.split('"', 2)
        if '{' in args:
            size = int(args[2:-1])
            self.in_literal = (size, self.appendLiteral, (id,))
            return "+ Ready for argument\r\n"
        return self.appendLiteral(args[1:], id)
    def appendLiteral(self, message, command_id):
        while True:
            id = self.next_id
            self.next_id += 1
            if id not in IMAP_MESSAGES:
                break
        IMAP_MESSAGES[id] = message
        return "* APPEND %s\r\n%s OK APPEND succeeded\r\n" % \
               (id, command_id)
    def onSearch(self, id, command, args, uid=False):
        args = args.upper()
        results = ()
        if args.find("UNDELETED") != -1:
            for msg_id in UNDELETED_IDS:
                if uid:
                    results += (IMAP_UIDS[msg_id],)
                else:
                    results += (msg_id,)
        if uid:
            command_string = "UID " + command
        else:
            command_string = command
        return "%s\r\n%s OK %s completed\r\n" % \
               ("* SEARCH " + ' '.join([str(r) for r in results]), id,
                command_string)
    def onFetch(self, id, command, args, uid=False):
        msg_nums, msg_parts = args.split(None, 1)
        msg_nums = msg_nums.split()
        response = {}
        for msg in msg_nums:
            response[msg] = []
        if msg_parts.find("UID") != -1:
            if uid:
                for msg in msg_nums:
                    response[msg].append("FETCH (UID %s)" % (msg,))
            else:
                for msg in msg_nums:
                    response[msg].append("FETCH (UID %s)" %
                                         (IMAP_UIDS[int(msg)]))
        if msg_parts.find("BODY.PEEK[]") != -1:
            for msg in msg_nums:
                if uid:
                    msg_uid = int(msg)
                else:
                    msg_uid = IMAP_UIDS[int(msg)]
                response[msg].append(("FETCH (BODY[] {%s}" %
                                     (len(IMAP_MESSAGES[msg_uid])),
                                     IMAP_MESSAGES[msg_uid]))
        if msg_parts.find("RFC822.HEADER") != -1:
            for msg in msg_nums:
                if uid:
                    msg_uid = int(msg)
                else:
                    msg_uid = IMAP_UIDS[int(msg)]
                msg_text = IMAP_MESSAGES[msg_uid]
                headers, unused = msg_text.split('\r\n\r\n', 1)
                response[msg].append(("FETCH (RFC822.HEADER {%s}" %
                                      (len(headers),), headers))
        if msg_parts.find("FLAGS INTERNALDATE") != -1:
            for msg in msg_nums:
                response[msg].append('FETCH (FLAGS (\Seen \Deleted) '
                                     'INTERNALDATE "27-Jul-2004 13:1'
                                     '1:56 +1200')
        for msg in msg_nums:
            try:
                simple = " ".join(response[msg])
            except TypeError:
                simple = []
                for part in response[msg]:
                    if isinstance(part, types.StringTypes):
                        simple.append(part)
                    else:
                        simple.append('%s\r\n%s)' % (part[0], part[1]))
                simple = " ".join(simple)
            response[msg] = "* %s %s" % (msg, simple)
        response_text = "\r\n".join(response.values())
        return "%s\r\n%s OK FETCH completed\r\n" % (response_text, id)
    def onUID(self, id, command, args, uid=False):
        actual_command, args = args.split(None, 1)
        handler = self.handlers.get(actual_command, self.onUnknown)
        return handler(id, actual_command, args, uid=True)
    def onUnknown(self, id, command, args, uid=False):
        """Unknown IMAP4 command."""
        return "%s BAD Command unrecognised: %s\r\n" % (id, repr(command))
class BaseIMAPFilterTest(unittest.TestCase):
    def setUp(self):
        self.imap = IMAPSession("localhost", IMAP_PORT)
    def tearDown(self):
        try:
            self.imap.logout()
        except imaplib.error:
            pass
class IMAPSessionTest(BaseIMAPFilterTest):
    def testConnection(self):
        self.assert_(self.imap.connected)
    def testGoodLogin(self):
        self.imap.login(IMAP_USERNAME, IMAP_PASSWORD)
        self.assert_(self.imap.logged_in)
    def testBadLogin(self):
        print "\nYou should see a message indicating that login failed."
        self.assertRaises(LoginFailure, self.imap.login, IMAP_USERNAME,
                          "wrong password")
    def test_check_response(self):
        test_data = "IMAP response data"
        response = ("OK", test_data)
        data = self.imap.check_response("", response)
        self.assertEqual(data, test_data)
        response = ("NO", test_data)
        self.assertRaises(BadIMAPResponseError, self.imap.check_response,
                          "", response)
    def testSelectFolder(self):
        self.imap.login(IMAP_USERNAME, IMAP_PASSWORD)
        self.assertRaises(BadIMAPResponseError, self.imap.SelectFolder, "")
        self.imap.SelectFolder("Inbox")
        response = self.imap.response('OK')
        self.assertEquals(response[0], "OK")
        self.assert_(response[1] != [None])
        self.imap.SelectFolder("Inbox")
        response = self.imap.response('OK')
        self.assertEquals(response[0], "OK")
        self.assertEquals(response[1], [None])
    def test_folder_list(self):
        global FAIL_NEXT
        self.imap.login(IMAP_USERNAME, IMAP_PASSWORD)
        folders = self.imap.folder_list()
        correct = IMAP_FOLDER_LIST[:]
        correct.sort()
        self.assertEqual(folders, correct)
        print "\nYou should see a message indicating that getting the " \
              "folder list failed."
        FAIL_NEXT = True
        self.assertEqual(self.imap.folder_list(), [])
    def test_extract_fetch_data(self):
        response = "bad response"
        self.assertRaises(BadIMAPResponseError,
                          self.imap.extract_fetch_data, response)
        message_number = "123"
        uid = "5432"
        response = ("%s (UID %s)" % (message_number, uid),)
        data = self.imap.extract_fetch_data(response)
        self.assertEqual(data[message_number]["message_number"],
                         message_number)
        self.assertEqual(data[message_number]["UID"], uid)
        flags = r"(\Seen \Deleted)"
        date = '"27-Jul-2004 13:11:56 +1200"'
        response = ("%s (FLAGS %s INTERNALDATE %s)" % \
                   (message_number, flags, date),)
        data = self.imap.extract_fetch_data(response)
        self.assertEqual(data[message_number]["message_number"],
                         message_number)
        self.assertEqual(data[message_number]["FLAGS"], flags)
        self.assertEqual(data[message_number]["INTERNALDATE"], date)
        rfc = "Subject: Test\r\n\r\nThis is a test message."
        response = (("%s (RFC822 {%s}" % (message_number, len(rfc)), rfc),)
        data = self.imap.extract_fetch_data(response)
        self.assertEqual(data[message_number]["message_number"],
                         message_number)
        self.assertEqual(data[message_number]["RFC822"], rfc)
        headers = "Subject: Foo\r\nX-SpamBayes-ID: 1231-1\r\n"
        response = (("%s (RFC822.HEADER {%s}" % (message_number,
                                                len(headers)), headers),)
        data = self.imap.extract_fetch_data(response)
        self.assertEqual(data[message_number]["RFC822.HEADER"], headers)
        peek = "Subject: Test2\r\n\r\nThis is another test message."
        response = (("%s (BODY[] {%s}" % (message_number, len(peek)),
                    peek),)
        data = self.imap.extract_fetch_data(response)
        self.assertEqual(data[message_number]["BODY[]"], peek)
        uid = '3018'
        flags = '(\\Seen \\Deleted)'
        headers = "Return-Path: <tameyer@ihug.co.nz>\r\nX-Original-To" \
                  ": david@leinbach.name\r\nDelivered-To: dleinbac@ma" \
                  "il2.majro.dhs.org\r\nReceived: from its-mail1.mass" \
                  "ey.ac.nz (its-mail1.massey.ac.nz [130.123.128.11])" \
                  "\r\n\tby mail2.majro.dhs.org (Postfix) with ESMTP " \
                  "id 7BC5018FE22\r\n\tfor <david@leinbach.name>; Mon" \
                  ", 13 Dec 2004 22:46:05 -0800 (PST)\r\nReceived: fr" \
                  "om its-mm1.massey.ac.nz (its-mm1 [130.123.128.45])" \
                  "\r\n\tby its-mail1.massey.ac.nz (8.9.3/8.9.3) with" \
                  "ESMTP id TAA12081;\r\n\tTue, 14 Dec 2004 19:45:56 " \
                  "+1300 (NZDT)\r\nReceived: from its-campus2.massey." \
                  "ac.nz (Not Verified[130.123.48.254]) by its-mm1.ma" \
                  "ssey.ac.nz with NetIQ MailMarshal\r\n\tid <B003745" \
                  "788>; Tue, 14 Dec 2004 19:45:56 +1300\r\nReceived:" \
                  "from it029048 (it029048.massey.ac.nz [130.123.238." \
                  "51])\r\n\tby its-campus2.massey.ac.nz (8.9.3/8.9.3" \
                  ") with ESMTP id TAA05881;\r\n\tTue, 14 Dec 2004 19" \
                  ':45:55 +1300 (NZDT)\r\nFrom: "Tony Meyer"  <tameye' \
                  'r@ihug.co.nz>\r\nTo: "\'David Leinbach\'" <david@l' \
                  "einbach.name>, <spambayes@python.org>\r\nSubject: " \
                  "RE: [Spambayes] KeyError in sp_imapfilter\r\nDate:" \
                  "Tue, 14 Dec 2004 19:45:25 +1300\r\nMessage-ID: <EC" \
                  "BA357DDED63B4995F5C1F5CBE5B1E86C3872@its-xchg4.mas" \
                  "sey.ac.nz>\r\nMIME-Version: 1.0\r\nContent-Type: t" \
                  'ext/plain;\r\n\tcharset="us-ascii"\r\nContent-Tran' \
                  "sfer-Encoding: quoted-printable\r\nX-Priority: 3 (" \
                  "Normal)\r\nX-MSMail-Priority: Normal\r\nX-Mailer: " \
                  "Microsoft Outlook, Build 10.0.4510\r\nIn-Reply-To:" \
                  "<ECBA357DDED63B4995F5C1F5CBE5B1E801A49168@its-xchg" \
                  ".massey.ac.nz>\r\nX-Habeas-SWE-1: winter into spri" \
                  "ng\r\nX-Habeas-SWE-2: brightly anticipated\r\nX-Ha" \
                  "beas-SWE-3: like Habeas SWE (tm)\r\nX-Habeas-SWE-4" \
                  ": Copyright 2002 Habeas (tm)\r\nX-Habeas-SWE-5: Se" \
                  "nder Warranted Email (SWE) (tm). The sender of thi" \
                  "s\r\nX-Habeas-SWE-6: email in exchange for a licen" \
                  "se for this Habeas\r\nX-Habeas-SWE-7: warrant mark" \
                  "warrants that this is a Habeas Compliant\r\nX-Habe" \
                  "as-SWE-8: Message (HCM) and  not spam. Please repo" \
                  "rt use of this\r\nX-Habeas-SWE-9: mark in spam to " \
                  "<http://www.habeas.com/report/>.\r\nX-MimeOLE: Pro" \
                  "duced By Microsoft MimeOLE V6.00.2900.2180\r\nImpo" \
                  "rtance: Normal\r\n\r\n"
        response = ['1 (FLAGS %s)' % flags,
                    ('2 (UID %s RFC822.HEADER {%d}' % (uid, len(headers)),
                     headers), ')'] 
        data = self.imap.extract_fetch_data(response)
        self.assertEqual(data['1']["message_number"], '1')
        self.assertEqual(data['2']["message_number"], '2')
        self.assertEqual(data['1']["FLAGS"], flags)
        self.assertEqual(data['2']["UID"], uid)
        self.assertEqual(data['2']["RFC822.HEADER"], headers)
        headers = 'Return-Path: <eleinbach@gmail.com>\r\n' \
                  'X-Original-To: david@leinbach.name\r\n' \
                  'Delivered-To: dleinbac@mail2.majro.dhs.org\r\n' \
                  'Received: from cressida (unknown [70.70.206.137])' \
                  '\r\n\tby mail2.majro.dhs.org (Postfix) with ESMTP' \
                  'id AAD451CD28E\r\n\tfor <david@leinbach.name>; Mo' \
                  'n,  6 Dec 2004 11:49:41 -0800 (PST)\r\n' \
                  'From: "Erin Leinbach" <eleinbach@gmail.com>\r\n' \
                  'To: "Dave" <david@leinbach.name>\r\n' \
                  'Subject: Goo goo dolls songs\r\n' \
                  'Date: Mon, 6 Dec 2004 11:51:07 -0800\r\n' \
                  'Message-ID: <000001c4dbcc$ed6188a0$6801a8c0@cre' \
                  'ssida>\r\nMIME-Version: 1.0\r\n' \
                  'Content-Type: text/plain;\r\n' \
                  '\tcharset="Windows-1252"\r\n' \
                  'Content-Transfer-Encoding: 7bit\r\n' \
                  'X-Priority: 3 (Normal)\r\n' \
                  'X-MSMail-Priority: Normal\r\n' \
                  'X-Mailer: Microsoft Outlook, Build 10.0.2616\r\n' \
                  'Importance: Normal\r\n' \
                  'X-MimeOLE: Produced By Microsoft MimeOLE V6.00.29' \
                  '00.2180\r\nX-Spambayes-Classification: ham\r\n' \
                  'X-Spambayes-MailId: 000001\r\n\r\n'
        uid = '3086'
        flags = '(\\Seen \\Deleted)'
        response = [('5 (UID %s RFC822.HEADER {839}' % (uid,), headers),
                    ')', '5 (FLAGS %s)' % (flags,)]
        data = self.imap.extract_fetch_data(response)
        self.assertEqual(data['5']["message_number"], '5')
        self.assertEqual(data['5']["FLAGS"], flags)
        self.assertEqual(data['5']["UID"], uid)
        self.assertEqual(data['5']["RFC822.HEADER"], headers)
    def _counter(self, size):
        self._count += 1
        return self._imap_file_read(size)
    def test_safe_read(self):
        saved_file = self.imap.file
        self.imap.file = StringIO.StringIO()
        self.imap.file.write("".join(IMAP_MESSAGES.values()*10))
        self.imap.file.seek(0)
        try:
            self.assertEqual(len(self.imap.read(\
                self.imap.MAXIMUM_SAFE_READ-1)),
                             self.imap.MAXIMUM_SAFE_READ-1)
            self.assertEqual(len(self.imap.read(\
                self.imap.MAXIMUM_SAFE_READ+1)),
                             self.imap.MAXIMUM_SAFE_READ+1)
            self._count = 0
            self._imap_file_read = self.imap.file.read
            self.imap.file.read = self._counter
            self.imap.read(self.imap.MAXIMUM_SAFE_READ-1)
            self.assertEqual(self._count, 1)
            self._count = 0
            self.imap.read(self.imap.MAXIMUM_SAFE_READ+1)
            self.assertEqual(self._count, 2)
        finally:
            self.imap.file = saved_file
class IMAPMessageTest(BaseIMAPFilterTest):
    def setUp(self):
        BaseIMAPFilterTest.setUp(self)
        self.msg = IMAPMessage()
        self.msg.imap_server = self.imap
    def test_extract_time_no_date(self):
        date = self.msg.extractTime()
        self.assertEqual(date, imaplib.Time2Internaldate(time.time()))
    def test_extract_time_date(self):
        self.msg["Date"] = "Wed, 19 May 2004 20:05:15 +1200"
        date = self.msg.extractTime()
        self.assertEqual(date, '"19-May-2004 20:05:15 +1200"')
    def test_extract_time_bad_date(self):
        self.msg["Date"] = "Mon, 06 May 0102 10:51:16 -0100"
        date = self.msg.extractTime()
        self.assertEqual(date, imaplib.Time2Internaldate(time.time()))
    def test_as_string_invalid(self):
        content = "This is example content.\nThis is more\r\n"
        self.msg.invalid = True
        self.msg.invalid_content = content
        as_string = self.msg.as_string()
        self.assertEqual(self.msg._force_CRLF(content), as_string)
    def testMoveTo(self):
        fol1 = "Folder1"
        fol2 = "Folder2"
        self.msg.MoveTo(fol1)
        self.assertEqual(self.msg.folder, fol1)
        self.msg.MoveTo(fol2)
        self.assertEqual(self.msg.previous_folder, fol1)
        self.assertEqual(self.msg.folder, fol2)
    def test_get_full_message(self):
        self.assertRaises(AssertionError, self.msg.get_full_message)
        self.msg.id = "unittest"
        self.assertRaises(AttributeError, self.msg.get_full_message)
        self.msg.imap_server.login(IMAP_USERNAME, IMAP_PASSWORD)
        self.msg.imap_server.select()
        response = self.msg.imap_server.fetch(1, "UID")
        self.assertEqual(response[0], "OK")
        self.msg.uid = response[1][0][7:-1]
        self.msg.folder = IMAPFolder("Inbox", self.msg.imap_server, None)
        new_msg = self.msg.get_full_message()
        self.assertEqual(new_msg.folder, self.msg.folder)
        self.assertEqual(new_msg.previous_folder, self.msg.previous_folder)
        self.assertEqual(new_msg.uid, self.msg.uid)
        self.assertEqual(new_msg.id, self.msg.id)
        self.assertEqual(new_msg.rfc822_key, self.msg.rfc822_key)
        self.assertEqual(new_msg.rfc822_command, self.msg.rfc822_command)
        self.assertEqual(new_msg.imap_server, self.msg.imap_server)
        id_header = options["Headers", "mailid_header_name"]
        self.assertEqual(new_msg[id_header], self.msg.id)
        new_msg2 = new_msg.get_full_message()
        self.assert_(new_msg is new_msg2)
    def test_get_bad_message(self):
        self.msg.id = "unittest"
        self.msg.imap_server.login(IMAP_USERNAME, IMAP_PASSWORD)
        self.msg.imap_server.select()
        self.msg.uid = 103 # id of malformed message in dummy server
        self.msg.folder = IMAPFolder("Inbox", self.msg.imap_server, None)
        print "\nWith email package versions less than 3.0, you should " \
              "see an error parsing the message."
        new_msg = self.msg.get_full_message()
        has_header = new_msg.as_string().find("X-Spambayes-Exception: ") != -1
        has_defect = hasattr(new_msg, "defects") and len(new_msg.defects) > 0
        self.assert_(has_header or has_defect)
    def test_get_memory_error_message(self):
        pass
    def test_Save(self):
        pass
class IMAPFolderTest(BaseIMAPFilterTest):
    def setUp(self):
        BaseIMAPFilterTest.setUp(self)
        self.imap.login(IMAP_USERNAME, IMAP_PASSWORD)
        self.folder = IMAPFolder("testfolder", self.imap, None)
    def test_cmp(self):
        folder2 = IMAPFolder("testfolder", self.imap, None)
        folder3 = IMAPFolder("testfolder2", self.imap, None)
        self.assertEqual(self.folder, folder2)
        self.assertNotEqual(self.folder, folder3)
    def test_iter(self):
        keys = self.folder.keys()
        for msg in self.folder:
            msg = msg.get_full_message()
            msg_correct = email.message_from_string(IMAP_MESSAGES[int(keys[0])],
                                                    _class=message.Message)
            id_header_name = options["Headers", "mailid_header_name"]
            if msg_correct[id_header_name] is None:
                msg_correct[id_header_name] = msg.id
            self.assertEqual(msg.as_string(), msg_correct.as_string())
            keys = keys[1:]
    def test_keys(self):
        keys = self.folder.keys()
        correct_keys = [str(IMAP_UIDS[id]) for id in UNDELETED_IDS]
        self.assertEqual(keys, correct_keys)
    def test_getitem_new_style(self):
        id_header_name = options["Headers", "mailid_header_name"]
        msg1 = self.folder[101]
        self.assertEqual(msg1.id, SB_ID_1)
        msg1 = msg1.get_full_message()
        msg1_correct = email.message_from_string(IMAP_MESSAGES[101],
                                                 message.Message)
        self.assertNotEqual(msg1[id_header_name], None)
        msg1_correct[id_header_name] = SB_ID_1
        self.assertEqual(msg1.as_string(), msg1_correct.as_string())
    def test_getitem_old_style(self):
        id_header_name = options["Headers", "mailid_header_name"]
        msg2 = self.folder[102]
        self.assertEqual(msg2.id, SB_ID_2)
        msg2 = msg2.get_full_message()
        self.assertNotEqual(msg2[id_header_name], None)
        self.assertEqual(msg2.as_string(), IMAP_MESSAGES[102])
    def test_getitem_new_id(self):
        id_header_name = options["Headers", "mailid_header_name"]
        msg3 = self.folder[104]
        self.assertNotEqual(msg3[id_header_name], None)
        msg_correct = email.message_from_string(IMAP_MESSAGES[104],
                                                message.Message)
        msg_correct[id_header_name] = msg3.id
        self.assertEqual(msg3.as_string(), msg_correct.as_string())
    def test_generate_id(self):
        print "\nThis test takes slightly over a second."
        id1 = self.folder._generate_id()
        id2 = self.folder._generate_id()
        id3 = self.folder._generate_id()
        time.sleep(1)
        id4 = self.folder._generate_id()
        self.assertEqual(id2, id1 + "-2")
        self.assertEqual(id3, id1 + "-3")
        self.assertNotEqual(id1, id4)
        self.assertNotEqual(id2, id4)
        self.assertNotEqual(id3, id4)
        self.assert_('-' not in id4)
    def test_Train(self):
        pass
    def test_Filter(self):
        pass
class IMAPFilterTest(BaseIMAPFilterTest):
    def setUp(self):
        BaseIMAPFilterTest.setUp(self)
        self.imap.login(IMAP_USERNAME, IMAP_PASSWORD)
        classifier = Classifier()
        self.filter = IMAPFilter(classifier, None)
        options["imap", "ham_train_folders"] = ("ham_to_train",)
        options["imap", "spam_train_folders"] = ("spam_to_train",)
    def test_Train(self):
        pass
    def test_Filter(self):
        pass
class SFBugsTest(BaseIMAPFilterTest):
    def test_802545(self):
        pass
    def test_816400(self):
        pass
    def test_818552(self):
        pass
    def test_842984(self):
        pass
    def test_886133(self):
        pass
class InterfaceTest(unittest.TestCase):
    def setUp(self):
        print "\nThis test takes slightly over one second."
        self.saved_server = options["imap", "server"]
        options["imap", "server"] = ""
        thread.start_new_thread(run, (True,))
        time.sleep(1)
    def tearDown(self):
        options["imap", "server"] = self.saved_server
        from urllib import urlopen, urlencode
        urlopen('http://localhost:%d/save' % options["html_ui", "port"],
                urlencode({'how': _('Save & shutdown')})).read()
    def test_UI(self):
        httpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        httpServer.connect(('localhost', options["html_ui", "port"]))
        httpServer.send("get / HTTP/1.0\r\n\r\n")
        response = ''
        while 1:
            packet = httpServer.recv(1024)
            if not packet: break
            response += packet
        self.assert_(re.search(r"(?s)<html>.*SpamBayes IMAP Filter.*</html>",
                               response))
def suite():
    suite = unittest.TestSuite()
    for cls in (IMAPSessionTest,
                IMAPMessageTest,
                IMAPFolderTest,
                IMAPFilterTest,
                SFBugsTest,
                InterfaceTest,
               ):
        suite.addTest(unittest.makeSuite(cls))
    return suite
if __name__=='__main__':
    def runTestServer():
        TestListener()
        asyncore.loop()
    thread.start_new_thread(runTestServer, ())
    sb_test_support.unittest_main(argv=sys.argv + ['suite'])
