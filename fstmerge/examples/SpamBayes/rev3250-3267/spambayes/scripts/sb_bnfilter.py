"""Usage: %(program)s [options]
Where:
    -h
        show usage and exit
*   -f
        filter (default if no processing options are given)
*   -g
        [EXPERIMENTAL] (re)train as a good (ham) message
*   -s
        [EXPERIMENTAL] (re)train as a bad (spam) message
*   -t
        [EXPERIMENTAL] filter and train based on the result -- you must
        make sure to untrain all mistakes later.  Not recommended.
*   -G
        [EXPERIMENTAL] untrain ham (only use if you've already trained
        this message)
*   -S
        [EXPERIMENTAL] untrain spam (only use if you've already trained
        this message)
    -k FILE
        Unix domain socket used to communicate with a short-lived server
        process. Default is ~/.sbbnsock-<hostname>
    These options will not take effect when connecting to a preloaded server:
    -p FILE
        use pickle FILE as the persistent store.  loads data from this file
        if it exists, and saves data to this file at the end.
    -d FILE
        use DBM store FILE as the persistent store.
    -o section:option:value
        set [section, option] in the options database to value
    -a seconds
        timeout in seconds between requests before this server terminates
    -A number
        terminate this server after this many requests
"""

import sys, getopt, socket, errno, os, time

def usage(code, msg=''):

    """Print usage message and sys.exit(code)."""

    if msg:

        print(msg, file=sys.stderr)

        print(file=sys.stderr)

    print(__doc__, file=sys.stderr)

    sys.exit(code)
 def main():

    try:

        opts, args = getopt.getopt(sys.argv[1:], 'hfgstGSd:p:o:a:A:k:')

    except getopt.error as msg:

        usage(2, msg)

    filename = os.path.expanduser('~/.sbbnsock-'+socket.gethostname())

    action_options = []

    server_options = []

    for opt, arg in opts:

        if opt == '-h':

            usage(0)

        elif opt in ('-f', '-g', '-s', '-t', '-G', '-S'):

            action_options.append(opt)

        elif opt in ('-d', '-p', '-o', '-a', '-A'):

            server_options.append(opt)

            server_options.append(arg)

        elif opt == '-k':

            filename = arg

    if args:

        usage(2)

    server_options.append(filename)

    s = make_socket(server_options, filename)

    w_file = s.makefile('w')

    r_file = s.makefile('r')

    w_file.write(' '.join(action_options)+'\n')

    while 1:

        b = sys.stdin.read(1024*64)

        if not b:

            break

        w_file.write(b)

    w_file.flush()

    w_file.close()

    s.shutdown(1)

    error = int(r_file.readline())

    expected_size = int(r_file.readline())

    if error:

        output = sys.stderr

    else:

        output = sys.stdout

    total_size = 0

    while 1:

        b = r_file.read(1024*64)

        if not b:

            break

        output.write(b)

        total_size += len(b)

    output.flush()

    if total_size != expected_size:

        print('size mismatch %d != %d' % (total_size,
                                                         expected_size), file=sys.stderr)

        sys.exit(3)

    if error:

        sys.exit(error)
 def make_socket(server_options, filename):

    refused_count = 0

    no_server_count = 0

    while 1:

        try:

            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

            s.connect(filename)

        except socket.error as e:

            if e[0] == errno.EAGAIN:

                pass

            elif e[0] == errno.ENOENT or not os.path.exists(filename):

                no_server_count += 1

                if no_server_count > 4:

                    raise

                refused_count = 0

                fork_server(server_options)

            elif e[0] == errno.ECONNREFUSED:

                refused_count += 1

                if refused_count == 4:

                    try:

                        os.unlink(filename)

                    except EnvironmentError:

                        pass

                elif refused_count > 6:

                    raise

            else:

                raise 

            time.sleep(0.2 * 2.0**no_server_count * 2.0**refused_count)

        else:

            return s
 def fork_server(options):

    if os.fork():

        return

    os.close(0)

    sys.stdin = sys.__stdin__ = open("/dev/null")

    os.close(1)

    sys.stdout = sys.__stdout__ = open("/dev/null", "w")

    os.setsid()

    os.execv(sys.executable, [sys.executable,
                              os.path.join(os.path.split(sys.argv[0])[0],
                                           'sb_bnserver.py') ]+options)

    sys._exit(1)
 if __name__ == "__main__":

    main()

 if __name__ == "__main__":

    main()



