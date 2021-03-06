

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Security.Principal;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using ProcessHacker.Base;
using ProcessHacker.Common;
using ProcessHacker.Common.Objects;
using ProcessHacker.Components;
using ProcessHacker.Native;
using ProcessHacker.Native.Api;
using ProcessHacker.Native.Objects;
using ProcessHacker.Native.Security;
using ProcessHacker.UI;

namespace ProcessHacker
{
    public static class Program
    {



        public static HackerWindow HackerWindow;
        public static IntPtr HackerWindowHandle;
        public static bool HackerWindowTopMost;

        public static ProcessAccess MinProcessQueryRights = ProcessAccess.QueryInformation;
        public static ProcessAccess MinProcessReadMemoryRights = ProcessAccess.VmRead;
        public static ProcessAccess MinProcessWriteMemoryRights = ProcessAccess.VmWrite | ProcessAccess.VmOperation;
        public static ProcessAccess MinProcessGetHandleInformationRights = ProcessAccess.DupHandle;
        public static ThreadAccess MinThreadQueryRights = ThreadAccess.QueryInformation;

        public static int CurrentProcessId;
        public static int CurrentSessionId;
        public static string CurrentUsername;




        public static IdGenerator ResultsIds = new IdGenerator() { Sort = true };

        public static Dictionary<string, Structs.StructDef> Structs = new Dictionary<string, ProcessHacker.Structs.StructDef>();

        public static bool MemoryEditorsThreaded = true;
        public static Dictionary<string, MemoryEditor> MemoryEditors = new Dictionary<string, MemoryEditor>();
        public static Dictionary<string, Thread> MemoryEditorsThreads = new Dictionary<string, Thread>();

        public static bool ResultsWindowsThreaded = true;
        public static Dictionary<string, ResultsWindow> ResultsWindows = new Dictionary<string, ResultsWindow>();
        public static Dictionary<string, Thread> ResultsThreads = new Dictionary<string, Thread>();

        public static bool PEWindowsThreaded = false;
        public static Dictionary<string, PEWindow> PEWindows = new Dictionary<string, PEWindow>();
        public static Dictionary<string, Thread> PEThreads = new Dictionary<string, Thread>();

        public static bool PWindowsThreaded = true;
        public static Dictionary<int, ProcessWindow> PWindows = new Dictionary<int, ProcessWindow>();
        public static Dictionary<int, Thread> PThreads = new Dictionary<int, Thread>();

        public delegate void ResultsWindowInvokeAction(ResultsWindow f);
        public delegate void MemoryEditorInvokeAction(MemoryEditor f);
        public delegate void ThreadWindowInvokeAction(ThreadWindow f);
        public delegate void PEWindowInvokeAction(PEWindow f);
        public delegate void PWindowInvokeAction(ProcessWindow f);
        public delegate void UpdateWindowAction(Form f);

        public static ProcessSystemProvider ProcessProvider;
        public static ServiceProvider ServiceProvider;
        public static NetworkProvider NetworkProvider;

        public static ApplicationInstance AppInstance;
        public static bool BadConfig = false;
        public static TokenElevationType ElevationType;
        public static ProcessHacker.Native.Threading.Mutant GlobalMutex;
        public static string GlobalMutexName = @"\BaseNamedObjects\ProcessHackerMutex";
        public static System.Collections.Specialized.StringCollection ImposterNames =
            new System.Collections.Specialized.StringCollection();
        public static int InspectPid = -1;
        public static bool NoKph = false;
        public static string SelectTab = "Processes";
        public static bool StartHidden = false;
        public static bool StartVisible = false;
        public static SharedThreadProvider SecondarySharedThreadProvider;
        public static SharedThreadProvider SharedThreadProvider;
        public static ProcessHacker.Native.Threading.Waiter SharedWaiter;

        private static object CollectWorkerThreadsLock = new object();




        [STAThread]
        public static void Main(string[] args)
        {
            Dictionary<string, string> pArgs = null;

            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);

            if (Environment.Version.Major < 2)
            {
                PhUtils.ShowError("You must have .NET Framework 2.0 or higher to use Process Hacker.");
                Environment.Exit(1);
            }



            Application.ThreadException += new ThreadExceptionEventHandler(Application_ThreadException);
            AppDomain.CurrentDomain.UnhandledException += new UnhandledExceptionEventHandler(CurrentDomain_UnhandledException);
            Application.SetUnhandledExceptionMode(UnhandledExceptionMode.CatchException, true);


            try
            {
                pArgs = ParseArgs(args);
            }
            catch
            {
                ShowCommandLineUsage();
                pArgs = new Dictionary<string, string>();
            }

            if (pArgs.ContainsKey("-h") || pArgs.ContainsKey("-help") || pArgs.ContainsKey("-?"))
            {
                ShowCommandLineUsage();
                return;
            }

            if (pArgs.ContainsKey("-recovered"))
            {
                ProcessHackerRestartRecovery.ApplicationRestartRecoveryManager.RecoverLastSession();
            }

            if (pArgs.ContainsKey("-elevate"))
            {
                StartProcessHackerAdmin();
                return;
            }


            try
            {
                if (pArgs.ContainsKey("-nokph"))
                    NoKph = true;
                if (Properties.Settings.Default.AllowOnlyOneInstance &&
                    !(pArgs.ContainsKey("-e") || pArgs.ContainsKey("-o") ||
                    pArgs.ContainsKey("-pw") || pArgs.ContainsKey("-pt"))
                    )
                    CheckForPreviousInstance();
            }
            catch
            { }


            try
            {
                if (Properties.Settings.Default.NeedsUpgrade)
                {
                    try
                    {
                        Properties.Settings.Default.Upgrade();
                    }
                    catch (Exception ex)
                    {
                        Logging.Log(ex);
                        PhUtils.ShowWarning("Process Hacker could not upgrade its settings from a previous version.");
                    }

                    Properties.Settings.Default.NeedsUpgrade = false;
                }
            }
            catch
            { }

            VerifySettings();

            ThreadPool.SetMinThreads(1, 1);
            ThreadPool.SetMaxThreads(2, 2);
            WorkQueue.GlobalWorkQueue.MaxWorkerThreads = 3;


            try
            {
                GlobalMutex = new ProcessHacker.Native.Threading.Mutant(GlobalMutexName);
            }
            catch (Exception ex)
            {
                Logging.Log(ex);
            }

            try
            {
                using (var thandle = ProcessHandle.GetCurrent().GetToken())
                {
                    try { thandle.SetPrivilege("SeDebugPrivilege", SePrivilegeAttributes.Enabled); }
                    catch { }
                    try { thandle.SetPrivilege("SeIncreaseBasePriorityPrivilege", SePrivilegeAttributes.Enabled); }
                    catch { }
                    try { thandle.SetPrivilege("SeLoadDriverPrivilege", SePrivilegeAttributes.Enabled); }
                    catch { }
                    try { thandle.SetPrivilege("SeRestorePrivilege", SePrivilegeAttributes.Enabled); }
                    catch { }
                    try { thandle.SetPrivilege("SeShutdownPrivilege", SePrivilegeAttributes.Enabled); }
                    catch { }
                    try { thandle.SetPrivilege("SeTakeOwnershipPrivilege", SePrivilegeAttributes.Enabled); }
                    catch { }

                    if (OSVersion.HasUac)
                    {
                        try { ElevationType = thandle.GetElevationType(); }
                        catch { ElevationType = TokenElevationType.Full; }

                        if (ElevationType == TokenElevationType.Default &&
                            !(new WindowsPrincipal(WindowsIdentity.GetCurrent())).
                                IsInRole(WindowsBuiltInRole.Administrator))
                            ElevationType = TokenElevationType.Limited;
                        else if (ElevationType == TokenElevationType.Default)
                            ElevationType = TokenElevationType.Full;
                    }
                    else
                    {
                        ElevationType = TokenElevationType.Full;
                    }
                }
            }
            catch (Exception ex)
            {
                Logging.Log(ex);
            }

            try
            {
                if (

                    IntPtr.Size == 4 &&
                    Properties.Settings.Default.EnableKPH &&
                    !NoKph &&

                    !pArgs.ContainsKey("-installkph") && !pArgs.ContainsKey("-uninstallkph")
                    )
                    KProcessHacker.Instance = new KProcessHacker("KProcessHacker");
            }
            catch
            { }

            MinProcessQueryRights = OSVersion.MinProcessQueryInfoAccess;
            MinThreadQueryRights = OSVersion.MinThreadQueryInfoAccess;

            if (KProcessHacker.Instance != null)
            {
                MinProcessGetHandleInformationRights = MinProcessQueryRights;
                MinProcessReadMemoryRights = MinProcessQueryRights;
                MinProcessWriteMemoryRights = MinProcessQueryRights;
            }

            try
            {
                CurrentUsername = System.Security.Principal.WindowsIdentity.GetCurrent().Name;
            }
            catch (Exception ex)
            {
                Logging.Log(ex);
            }

            try
            {
                CurrentProcessId = Win32.GetCurrentProcessId();
                CurrentSessionId = Win32.GetProcessSessionId(Win32.GetCurrentProcessId());
                System.Threading.Thread.CurrentThread.Priority = ThreadPriority.Highest;
            }
            catch (Exception ex)
            {
                Logging.Log(ex);
            }

            if (ProcessCommandLine(pArgs))
                return;

            Win32.FileIconInit(true);
            LoadProviders();
            Windows.GetProcessName = (pid) =>
                ProcessProvider.Dictionary.ContainsKey(pid) ?
                ProcessProvider.Dictionary[pid].Name :
                null;


            SharedWaiter = new ProcessHacker.Native.Threading.Waiter();

            new HackerWindow();
            Application.Run();
        }

        private static void ShowCommandLineUsage()
        {
            PhUtils.ShowInformation(
                "Option: \tUsage:\n" +
                "-a\tAggressive mode.\n" +
                "-elevate\tStarts Process Hacker elevated.\n" +
                "-h\tDisplays command line usage information.\n" +
                "-installkph\tInstalls the KProcessHacker service.\n" +
                "-ip pid\tDisplays the main window, then properties for the specified process.\n" +
                "-m\tStarts Process Hacker hidden.\n" +
                "-nokph\tDisables KProcessHacker. Use this if you encounter BSODs.\n" +
                "-o\tShows Options.\n" +
                "-pw pid\tDisplays properties for the specified process.\n" +
                "-pt pid\tDisplays properties for the specified process' token.\n" +
                "-t n\tShows the specified tab. 0 is Processes, 1 is Services and 2 is Network.\n" +
                "-uninstallkph\tUninstalls the KProcessHacker service.\n" +
                "-v\tStarts Process Hacker visible.\n" +
                ""
                );
        }

        private static void LoadProviders()
        {
            ProcessProvider = new ProcessSystemProvider();
            ServiceProvider = new ServiceProvider();
            NetworkProvider = new NetworkProvider();
            Program.SharedThreadProvider =
                new SharedThreadProvider(Properties.Settings.Default.RefreshInterval);
            Program.SharedThreadProvider.Add(ProcessProvider);
            Program.SharedThreadProvider.Add(ServiceProvider);
            Program.SharedThreadProvider.Add(NetworkProvider);
            Program.SecondarySharedThreadProvider =
                new SharedThreadProvider(Properties.Settings.Default.RefreshInterval);
        }

        private static void DeleteSettings()
        {
            if (System.IO.Directory.Exists(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData)
                + "\\wj32"))
                System.IO.Directory.Delete(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData)
                    + "\\wj32", true);
            if (System.IO.Directory.Exists(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData)
                + "\\wj32"))
                System.IO.Directory.Delete(Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData)
                    + "\\wj32", true);
        }

        private static void VerifySettings()
        {

            try
            {
                var a = Properties.Settings.Default.AlwaysOnTop;
            }
            catch (Exception ex)
            {
                Logging.Log(ex);

                try { ThemingScope.Activate(); }
                catch { }

                BadConfig = true;

                if (OSVersion.HasTaskDialogs)
                {
                    TaskDialog td = new TaskDialog();

                    td.WindowTitle = "Process Hacker";
                    td.MainInstruction = "Process Hacker could not initialize the configuration manager";
                    td.Content = "The Process Hacker configuration file is corrupt or the configuration manager " +
                        "could not be initialized. Do you want Process Hacker to reset your settings?";
                    td.MainIcon = TaskDialogIcon.Warning;
                    td.CommonButtons = TaskDialogCommonButtons.Cancel;
                    td.Buttons = new TaskDialogButton[]
                    {
                        new TaskDialogButton((int)DialogResult.Yes, "Yes, reset the settings and restart Process Hacker"),
                        new TaskDialogButton((int)DialogResult.No, "No, attempt to start Process Hacker anyway"),
                        new TaskDialogButton((int)DialogResult.Retry, "Show me the error message")
                    };
                    td.UseCommandLinks = true;
                    td.Callback = (taskDialog, args, userData) =>
                    {
                        if (args.Notification == TaskDialogNotification.ButtonClicked)
                        {
                            if (args.ButtonId == (int)DialogResult.Yes)
                            {
                                taskDialog.SetMarqueeProgressBar(true);
                                taskDialog.SetProgressBarMarquee(true, 1000);

                                try
                                {
                                    DeleteSettings();
                                    System.Diagnostics.Process.Start(Application.ExecutablePath);
                                }
                                catch (Exception ex2)
                                {
                                    taskDialog.SetProgressBarMarquee(false, 1000);
                                    PhUtils.ShowException("Unable to reset the settings", ex2);
                                    return true;
                                }

                                return false;
                            }
                            else if (args.ButtonId == (int)DialogResult.Retry)
                            {
                                InformationBox box = new InformationBox(ex.ToString());

                                box.ShowDialog();

                                return true;
                            }
                        }

                        return false;
                    };

                    int result = td.Show();

                    if (result == (int)DialogResult.No)
                    {
                        return;
                    }
                }
                else
                {
                    if (MessageBox.Show("Process Hacker cannot start because your configuration file is corrupt. " +
                        "Do you want Process Hacker to reset your settings?", "Process Hacker", MessageBoxButtons.YesNo,
                        MessageBoxIcon.Exclamation) == DialogResult.Yes)
                    {
                        try
                        {
                            DeleteSettings();
                            MessageBox.Show("Process Hacker has reset your settings and will now restart.", "Process Hacker",
                                MessageBoxButtons.OK, MessageBoxIcon.Information);
                            System.Diagnostics.Process.Start(Application.ExecutablePath);
                        }
                        catch (Exception ex2)
                        {
                            Logging.Log(ex2);

                            MessageBox.Show("Process Hacker could not reset your settings. Please delete the folder " +
                                "'wj32' in your Application Data/Local Application Data directories.",
                                "Process Hacker", MessageBoxButtons.OK, MessageBoxIcon.Exclamation);
                        }
                    }
                }

                Win32.ExitProcess(0);
            }
        }

        private static bool ProcessCommandLine(Dictionary<string, string> pArgs)
        {
            if (pArgs.ContainsKey("-e"))
            {
                try
                {
                    ExtendedCmd.Run(pArgs);
                }
                catch (Exception ex)
                {
                    PhUtils.ShowException("Unable to complete the operation", ex);
                }

                return true;
            }

            if (pArgs.ContainsKey("-installkph"))
            {
                try
                {
                    using (var scm = new ServiceManagerHandle(ScManagerAccess.CreateService))
                    {
                        using (var shandle = scm.CreateService(
                            "KProcessHacker",
                            "KProcessHacker",
                            ServiceType.KernelDriver,
                            ServiceStartType.SystemStart,
                            ServiceErrorControl.Ignore,
                            Application.StartupPath + "\\kprocesshacker.sys",
                            null,
                            null,
                            null
                            ))
                        {
                            shandle.Start();
                        }
                    }
                }
                catch (WindowsException ex)
                {

                    Environment.Exit((int)ex.ErrorCode);
                }

                return true;
            }

            if (pArgs.ContainsKey("-uninstallkph"))
            {
                try
                {
                    using (var shandle = new ServiceHandle("KProcessHacker", ServiceAccess.Stop | (ServiceAccess)StandardRights.Delete))
                    {
                        try { shandle.Control(ServiceControl.Stop); }
                        catch { }

                        shandle.Delete();
                    }
                }
                catch (WindowsException ex)
                {

                    Environment.Exit((int)ex.ErrorCode);
                }

                return true;
            }

            if (pArgs.ContainsKey("-ip"))
                InspectPid = int.Parse(pArgs["-ip"]);

            if (pArgs.ContainsKey("-pw"))
            {
                int pid = int.Parse(pArgs["-pw"]);

                SharedThreadProvider = new SharedThreadProvider(Properties.Settings.Default.RefreshInterval);
                SecondarySharedThreadProvider = new SharedThreadProvider(Properties.Settings.Default.RefreshInterval);

                ProcessProvider = new ProcessSystemProvider();
                ServiceProvider = new ServiceProvider();
                SharedThreadProvider.Add(ProcessProvider);
                SharedThreadProvider.Add(ServiceProvider);
                ProcessProvider.RunOnce();
                ServiceProvider.RunOnce();
                ProcessProvider.Enabled = true;
                ServiceProvider.Enabled = true;

                Win32.LoadLibrary(Properties.Settings.Default.DbgHelpPath);

                if (!ProcessProvider.Dictionary.ContainsKey(pid))
                {
                    PhUtils.ShowError("The process (PID " + pid.ToString() + ") does not exist.");
                    Environment.Exit(0);
                    return true;
                }

                ProcessWindow pw = new ProcessWindow(ProcessProvider.Dictionary[pid]);

                Application.Run(pw);

                SharedThreadProvider.Dispose();
                ProcessProvider.Dispose();
                ServiceProvider.Dispose();

                Environment.Exit(0);

                return true;
            }

            if (pArgs.ContainsKey("-pt"))
            {
                int pid = int.Parse(pArgs["-pt"]);

                try
                {
                    using (var phandle = new ProcessHandle(pid, Program.MinProcessQueryRights))
                        Application.Run(new TokenWindow(phandle));
                }
                catch (Exception ex)
                {
                    PhUtils.ShowException("Unable to show token properties", ex);
                }

                return true;
            }

            if (pArgs.ContainsKey("-o"))
            {
                OptionsWindow options = new OptionsWindow(true)
                {
                    StartPosition = FormStartPosition.CenterScreen
                };
                IWin32Window window;

                if (pArgs.ContainsKey("-hwnd"))
                    window = new WindowFromHandle(new IntPtr(int.Parse(pArgs["-hwnd"])));
                else
                    window = new WindowFromHandle(IntPtr.Zero);

                if (pArgs.ContainsKey("-rect"))
                {
                    Rectangle rect = Utils.GetRectangle(pArgs["-rect"]);

                    options.Location = new Point(rect.X + 20, rect.Y + 20);
                    options.StartPosition = FormStartPosition.Manual;
                }

                options.SelectedTab = options.TabPages["tabAdvanced"];
                options.ShowDialog(window);

                return true;
            }

            if (pArgs.ContainsKey(""))
                if (pArgs[""].Replace("\"", "").Trim().ToLower().EndsWith("taskmgr.exe"))
                    StartVisible = true;

            if (pArgs.ContainsKey("-m"))
                StartHidden = true;
            if (pArgs.ContainsKey("-v"))
                StartVisible = true;

            if (pArgs.ContainsKey("-a"))
            {
                try { Unhook(); }
                catch { }
                try { NProcessHacker.KphHookInit(); }
                catch { }
            }

            if (pArgs.ContainsKey("-t"))
            {
                if (pArgs["-t"] == "0")
                    SelectTab = "Processes";
                else if (pArgs["-t"] == "1")
                    SelectTab = "Services";
                else if (pArgs["-t"] == "2")
                    SelectTab = "Network";
            }

            return false;
        }

        public static void Unhook()
        {
            ProcessHacker.Native.Image.MappedImage file =
                new ProcessHacker.Native.Image.MappedImage(Environment.SystemDirectory + "\\ntdll.dll");
            IntPtr ntdll = Win32.GetModuleHandle("ntdll.dll");
            MemoryProtection oldProtection;

            oldProtection = ProcessHandle.GetCurrent().ProtectMemory(
                ntdll,
                (int)file.Size,
                MemoryProtection.ExecuteReadWrite
                );

            for (int i = 0; i < file.Exports.Count; i++)
            {
                var entry = file.Exports.GetEntry(i);

                if (!entry.Name.StartsWith("Nt") || entry.Name.StartsWith("Ntdll"))
                    continue;

                byte[] fileData = new byte[5];

                unsafe
                {
                    IntPtr function = file.Exports.GetFunction(entry.Ordinal).Function;

                    Win32.RtlMoveMemory(
                        function.Decrement(new IntPtr(file.Memory)).Increment(ntdll),
                        function,
                        (5).ToIntPtr()
                        );
                }
            }

            ProcessHandle.GetCurrent().ProtectMemory(
                ntdll,
                (int)file.Size,
                oldProtection
                );

            file.Dispose();
        }

        private static void CheckForPreviousInstance()
        {
            bool found = false;

            WindowHandle.Enumerate((window) =>
                {
                    if (window.GetText().Contains("Process Hacker ["))
                    {
                        int result;

                        window.SendMessageTimeout((WindowMessage)0x9991, 0, 0, SmtoFlags.Block, 5000, out result);

                        if (result == 0x1119)
                        {
                            window.SetForeground();
                            found = true;
                            return false;
                        }
                    }

                    return true;
                });

            if (found)
                Environment.Exit(0);
        }

        public static void StartProcessHackerAdmin()
        {
            StartProcessHackerAdmin("", null, IntPtr.Zero);
        }

        public static void StartProcessHackerAdmin(string args, MethodInvoker successAction)
        {
            StartProcessHackerAdmin(args, successAction, IntPtr.Zero);
        }

        public static void StartProcessHackerAdmin(string args, MethodInvoker successAction, IntPtr hWnd)
        {
            StartProgramAdmin(ProcessHandle.GetCurrent().GetMainModule().FileName,
                args, successAction, ShowWindowType.Show, hWnd);
        }

        public static WaitResult StartProcessHackerAdminWait(string args, IntPtr hWnd, uint timeout)
        {
            return StartProcessHackerAdminWait(args, null, hWnd, timeout);
        }

        public static WaitResult StartProcessHackerAdminWait(string args, MethodInvoker successAction, IntPtr hWnd, uint timeout)
        {
            var info = new ShellExecuteInfo();

            info.cbSize = System.Runtime.InteropServices.Marshal.SizeOf(info);
            info.lpFile = ProcessHandle.GetCurrent().GetMainModule().FileName;
            info.nShow = ShowWindowType.Show;
            info.fMask = 0x40;
            info.lpVerb = "runas";
            info.lpParameters = args;
            info.hWnd = hWnd;

            if (Win32.ShellExecuteEx(ref info))
            {
                if (successAction != null)
                    successAction();

                var result = Win32.WaitForSingleObject(info.hProcess, timeout);

                Win32.CloseHandle(info.hProcess);

                return result;
            }
            else
            {

                return WaitResult.Abandoned;
            }
        }

        public static void StartProgramAdmin(string program, string args,
            MethodInvoker successAction, ShowWindowType showType, IntPtr hWnd)
        {
            var info = new ShellExecuteInfo();

            info.cbSize = System.Runtime.InteropServices.Marshal.SizeOf(info);
            info.lpFile = program;
            info.nShow = showType;
            info.lpVerb = "runas";
            info.lpParameters = args;
            info.hWnd = hWnd;

            if (Win32.ShellExecuteEx(ref info))
            {
                if (successAction != null)
                    successAction();
            }
        }

        public static void TryStart(string command)
        {
            try
            {
                System.Diagnostics.Process.Start(command);
            }
            catch (Exception ex)
            {
                PhUtils.ShowException("Unable to start the process", ex);
            }
        }

        private static Dictionary<string, string> ParseArgs(string[] args)
        {
            Dictionary<string, string> dict = new Dictionary<string, string>();
            string argPending = null;

            foreach (string s in args)
            {
                if (s.StartsWith("-"))
                {
                    if (dict.ContainsKey(s))
                        throw new Exception("Option already specified.");

                    dict.Add(s, "");
                    argPending = s;
                }
                else
                {
                    if (argPending != null)
                    {
                        dict[argPending] = s;
                        argPending = null;
                    }
                    else
                    {
                        if (!dict.ContainsKey(""))
                            dict.Add("", s);
                    }
                }
            }
            return dict;
        }
        public static void ApplyFont(Font font)
        {
            HackerWindow.BeginInvoke(new MethodInvoker(() => { HackerWindow.ApplyFont(font); }));
            foreach (var processWindow in PWindows.Values)
            {
                processWindow.BeginInvoke(new MethodInvoker(() => { processWindow.ApplyFont(font); }));
            }
        }
        public static void CollectGarbage()
        {
            GC.Collect();
            GC.WaitForPendingFinalizers();
            GC.Collect();
            CompactNativeHeaps();
            CollectWorkerThreads();
        }
        public static void CollectWorkerThreads()
        {
            lock (CollectWorkerThreadsLock)
            {
                int workerThreads, completionPortThreads, maxWorkerThreads, maxCompletionPortThreads;
                ThreadPool.GetMaxThreads(out maxWorkerThreads, out maxCompletionPortThreads);
                ThreadPool.GetAvailableThreads(out workerThreads, out completionPortThreads);
                workerThreads = maxWorkerThreads - workerThreads;
                completionPortThreads = maxCompletionPortThreads - completionPortThreads;
                ThreadPool.SetMaxThreads(0, 0);
                ThreadPool.SetMaxThreads(workerThreads, completionPortThreads);
            }
        }
        public static void CompactNativeHeaps()
        {
            foreach (var heap in Heap.GetHeaps())
                heap.Compact(0);
        }
        public static string GetDiagnosticInformation()
        {
            StringBuilder info = new StringBuilder();
            AppDomain app = System.AppDomain.CurrentDomain;
            info.AppendLine("Process Hacker " + Application.ProductVersion);
            info.AppendLine("Process Hacker Build Time: " + Utils.GetAssemblyBuildDate(System.Reflection.Assembly.GetExecutingAssembly(), false));
            info.AppendLine("Application Base: " + app.SetupInformation.ApplicationBase);
            info.AppendLine("Configuration File: " + app.SetupInformation.ConfigurationFile);
            info.AppendLine("CLR Version: " + Environment.Version.ToString());
            info.AppendLine("OS Version: " + Environment.OSVersion.VersionString + " (" + OSVersion.BitsString + ")");
            info.AppendLine("Elevation: " + ElevationType.ToString());
            info.AppendLine("Working set: " + Utils.FormatSize(Environment.WorkingSet));
            if (KProcessHacker.Instance == null)
                info.AppendLine("KProcessHacker: not running");
            else
                info.AppendLine("KProcessHacker: " + KProcessHacker.Instance.Features.ToString());
            info.AppendLine();
            info.AppendLine("OBJECTS");
            int objectsCreatedCount = BaseObject.CreatedCount;
            int objectsFreedCount = BaseObject.FreedCount;
            info.AppendLine("Live: " + (objectsCreatedCount - objectsFreedCount).ToString());
            info.AppendLine("Created: " + objectsCreatedCount.ToString());
            info.AppendLine("Freed: " + objectsFreedCount.ToString());
            info.AppendLine("Disposed: " + BaseObject.DisposedCount.ToString());
            info.AppendLine("Finalized: " + BaseObject.FinalizedCount.ToString());
            info.AppendLine("Referenced: " + BaseObject.ReferencedCount.ToString());
            info.AppendLine("Dereferenced: " + BaseObject.DereferencedCount.ToString());
            info.AppendLine();
            info.AppendLine("PRIVATE HEAP");
            int heapAllocatedCount = MemoryAlloc.AllocatedCount;
            int heapFreedCount = MemoryAlloc.FreedCount;
            int heapReallocatedCount = MemoryAlloc.ReallocatedCount;
            info.AppendLine("Address: 0x" + MemoryAlloc.PrivateHeap.Address.ToString("x"));
            info.AppendLine("Live: " + (heapAllocatedCount - heapFreedCount).ToString());
            info.AppendLine("Allocated: " + heapAllocatedCount.ToString());
            info.AppendLine("Freed: " + heapFreedCount.ToString());
            info.AppendLine("Reallocated: " + heapReallocatedCount.ToString());
            info.AppendLine();
            info.AppendLine("MISCELLANEOUS COUNTERS");
            info.AppendLine("LSA lookup policy handle misses: " + LsaPolicyHandle.LookupPolicyHandleMisses.ToString());
            info.AppendLine();
            info.AppendLine("PROCESS HACKER THREAD POOL");
            info.AppendLine("Worker thread maximum: " + WorkQueue.GlobalWorkQueue.MaxWorkerThreads.ToString());
            info.AppendLine("Worker thread minimum: " + WorkQueue.GlobalWorkQueue.MinWorkerThreads.ToString());
            info.AppendLine("Busy worker threads: " + WorkQueue.GlobalWorkQueue.BusyCount.ToString());
            info.AppendLine("Total worker threads: " + WorkQueue.GlobalWorkQueue.WorkerCount.ToString());
            info.AppendLine("Queued work items: " + WorkQueue.GlobalWorkQueue.QueuedCount.ToString());
            foreach (WorkQueue.WorkItem workItem in WorkQueue.GlobalWorkQueue.GetQueuedWorkItems())
                if (workItem.Tag != null)
                    info.AppendLine("[" + workItem.Tag + "]: " + workItem.Work.Method.Name);
                else
                    info.AppendLine(workItem.Work.Method.Name);
            info.AppendLine();
            info.AppendLine("CLR THREAD POOL");
            int maxWt, maxIoc, minWt, minIoc, wt, ioc;
            ThreadPool.GetAvailableThreads(out wt, out ioc);
            ThreadPool.GetMinThreads(out minWt, out minIoc);
            ThreadPool.GetMaxThreads(out maxWt, out maxIoc);
            info.AppendLine("Worker threads: " + (maxWt - wt).ToString() + " current, " +
                maxWt.ToString() + " max, " + minWt.ToString() + " min");
            info.AppendLine("I/O completion threads: " + (maxIoc - ioc).ToString() + " current, " +
                maxIoc.ToString() + " max, " + minIoc.ToString() + " min");
            info.AppendLine();
            info.AppendLine("PRIMARY SHARED THREAD PROVIDER");
            if (SharedThreadProvider != null)
            {
                info.AppendLine("Count: " + SharedThreadProvider.Count.ToString());
                foreach (var provider in SharedThreadProvider.Providers)
                    info.AppendLine(provider.GetType().FullName +
                        " (Enabled: " + provider.Enabled +
                        ", Busy: " + provider.Busy.ToString() +
                        ", CreateThread: " + provider.CreateThread.ToString() +
                        ")");
            }
            else
            {
                info.AppendLine("(null)");
            }
            info.AppendLine();
            info.AppendLine("SECONDARY SHARED THREAD PROVIDER");
            if (SecondarySharedThreadProvider != null)
            {
                info.AppendLine("Count: " + SecondarySharedThreadProvider.Count.ToString());
                foreach (var provider in SecondarySharedThreadProvider.Providers)
                    info.AppendLine(provider.GetType().FullName +
                        " (Enabled: " + provider.Enabled +
                        ", Busy: " + provider.Busy.ToString() +
                        ", CreateThread: " + provider.CreateThread.ToString() +
                        ")");
            }
            else
            {
                info.AppendLine("(null)");
            }
            info.AppendLine();
            info.AppendLine("WINDOWS");
            info.AppendLine("MemoryEditors: " + MemoryEditors.Count.ToString() + ", " + MemoryEditorsThreads.Count.ToString());
            info.AppendLine("PEWindows: " + PEWindows.Count.ToString() + ", " + PEThreads.Count.ToString());
            info.AppendLine("PWindows: " + PWindows.Count.ToString() + ", " + PThreads.Count.ToString());
            info.AppendLine("ResultsWindows: " + ResultsWindows.Count.ToString() + ", " + ResultsThreads.Count.ToString());
            info.AppendLine();
            info.AppendLine("LOADED MODULES");
            info.AppendLine();
            foreach (ProcessModule module in ProcessHandle.Current.GetModules())
            {
                info.AppendLine("Module: " + module.BaseName);
                info.AppendLine("Location: " + module.FileName);
                DateTime fileCreatedInfo = System.IO.File.GetCreationTime(module.FileName);
                info.AppendLine(
                    "Created: " + fileCreatedInfo.ToLongDateString() + " " +
                    fileCreatedInfo.ToLongTimeString()
                    );
                DateTime fileModifiedInfo = System.IO.File.GetLastWriteTime(module.FileName);
                info.AppendLine(
                    "Modified: " + fileModifiedInfo.ToLongDateString() + " " +
                    fileModifiedInfo.ToLongTimeString()
                    );
                info.AppendLine("Version: " + System.Diagnostics.FileVersionInfo.GetVersionInfo(module.FileName).FileVersion);
                info.AppendLine();
            }
            return info.ToString();
        }
        private static void CurrentDomain_UnhandledException(object sender, UnhandledExceptionEventArgs e)
        {
            UnhandledException(e.ExceptionObject as Exception, e.IsTerminating);
        }
        private static void Application_ThreadException(object sender, ThreadExceptionEventArgs e)
        {
            UnhandledException(e.Exception, false);
        }
        private static void UnhandledException(Exception ex, bool terminating)
        {
            Logging.Log(Logging.Importance.Critical, ex.ToString());
            ErrorDialog ed = new ErrorDialog(ex, terminating);
            ed.ShowDialog();
        }
        public static MemoryEditor GetMemoryEditor(int PID, IntPtr address, long length)
        {
            return GetMemoryEditor(PID, address, length, new MemoryEditorInvokeAction(delegate {}));
        }
        public static MemoryEditor GetMemoryEditor(int PID, IntPtr address, long length, MemoryEditorInvokeAction action)
        {
            MemoryEditor ed = null;
            string id = PID.ToString() + "-" + address.ToString() + "-" + length.ToString();
            if (MemoryEditors.ContainsKey(id))
            {
                ed = MemoryEditors[id];
                ed.Invoke(action, ed);
                return ed;
            }
            if (MemoryEditorsThreaded)
            {
                Thread t = new Thread(new ThreadStart(delegate
                {
                    ed = new MemoryEditor(PID, address, length);
                    if (!ed.IsDisposed)
                        action(ed);
                    if (!ed.IsDisposed)
                        Application.Run(ed);
                    Program.MemoryEditorsThreads.Remove(id);
                }));
                t.SetApartmentState(ApartmentState.STA);
                t.Start();
                Program.MemoryEditorsThreads.Add(id, t);
            }
            else
            {
                ed = new MemoryEditor(PID, address, length);
                if (!ed.IsDisposed)
                    action(ed);
                if (!ed.IsDisposed)
                    ed.Show();
            }
            return ed;
        }
        public static ResultsWindow GetResultsWindow(int PID)
        {
            return GetResultsWindow(PID, new ResultsWindowInvokeAction(delegate { }));
        }
        public static ResultsWindow GetResultsWindow(int PID, ResultsWindowInvokeAction action)
        {
            ResultsWindow rw = null;
            string id = "";
            if (ResultsWindowsThreaded)
            {
                Thread t = new Thread(new ThreadStart(delegate
                {
                    rw = new ResultsWindow(PID);
                    id = rw.Id;
                    if (!rw.IsDisposed)
                        action(rw);
                    if (!rw.IsDisposed)
                        Application.Run(rw);
                    Program.ResultsThreads.Remove(id);
                }));
                t.SetApartmentState(ApartmentState.STA);
                t.Start();
                while (id == "") Thread.Sleep(1);
                Program.ResultsThreads.Add(id, t);
            }
            else
            {
                rw = new ResultsWindow(PID);
                if (!rw.IsDisposed)
                    action(rw);
                if (!rw.IsDisposed)
                    rw.Show();
            }
            return rw;
        }
        public static PEWindow GetPEWindow(string path)
        {
            return GetPEWindow(path, new PEWindowInvokeAction(delegate { }));
        }
        public static PEWindow GetPEWindow(string path, PEWindowInvokeAction action)
        {
            PEWindow pw = null;
            if (PEWindows.ContainsKey(path))
            {
                pw = PEWindows[path];
                pw.Invoke(action, pw);
                return pw;
            }
            if (PEWindowsThreaded)
            {
                Thread t = new Thread(new ThreadStart(delegate
                {
                    pw = new PEWindow(path);
                    if (!pw.IsDisposed)
                        action(pw);
                    if (!pw.IsDisposed)
                        Application.Run(pw);
                    Program.PEThreads.Remove(path);
                }));
                t.SetApartmentState(ApartmentState.STA);
                t.Start();
                Program.PEThreads.Add(path, t);
            }
            else
            {
                pw = new PEWindow(path);
                if (!pw.IsDisposed)
                    action(pw);
                if (!pw.IsDisposed)
                    pw.Show();
            }
            return pw;
        }
        public static ProcessWindow GetProcessWindow(ProcessItem process)
        {
            return GetProcessWindow(process, new PWindowInvokeAction(delegate { }));
        }
        public static ProcessWindow GetProcessWindow(ProcessItem process, PWindowInvokeAction action)
        {
            ProcessWindow pw = null;
            if (PWindows.ContainsKey(process.Pid))
            {
                pw = PWindows[process.Pid];
                pw.Invoke(action, pw);
                return pw;
            }
            if (PWindowsThreaded)
            {
                Thread t = new Thread(new ThreadStart(delegate
                {
                    pw = new ProcessWindow(process);
                    if (!pw.IsDisposed)
                        action(pw);
                    if (!pw.IsDisposed)
                        Application.Run(pw);
                    Program.PThreads.Remove(process.Pid);
                }));
                t.SetApartmentState(ApartmentState.STA);
                t.Start();
                Program.PThreads.Add(process.Pid, t);
            }
            else
            {
                pw = new ProcessWindow(process);
                if (!pw.IsDisposed)
                    action(pw);
                if (!pw.IsDisposed)
                    pw.Show();
            }
            return pw;
        }
        [System.Diagnostics.Conditional("NOT_DEFINED")]
        public static void Void()
        {
            int a = 0;
            int b = a * (a + 0);
            for (a = 0; a < b; a++)
                a += a * (a + b);
        }
        public static void FocusWindow(Form f)
        {
            if (f.InvokeRequired)
            {
                f.BeginInvoke(new MethodInvoker(delegate { Program.FocusWindow(f); }));
                return;
            }
            f.Visible = true;
            if (f.WindowState == FormWindowState.Minimized)
                f.WindowState = FormWindowState.Normal;
            f.Activate();
        }
        public static void UpdateWindowMenu(Menu windowMenuItem, Form f)
        {
            WeakReference<Form> fRef = new WeakReference<Form>(f);
            windowMenuItem.MenuItems.DisposeAndClear();
            MenuItem item;
            item = new MenuItem("&Always On Top");
            item.Tag = fRef;
            item.Click += new EventHandler(windowAlwaysOnTopItemClicked);
            item.Checked = f.TopMost;
            windowMenuItem.MenuItems.Add(item);
            item = new MenuItem("&Close");
            item.Tag = fRef;
            item.Click += new EventHandler(windowCloseItemClicked);
            windowMenuItem.MenuItems.Add(item);
        }
        public static void AddEscapeToClose(this Form f)
        {
            f.KeyPreview = true;
            f.KeyDown += (sender, e) =>
            {
                if (e.KeyCode == Keys.Escape)
                {
                    f.Close();
                    e.Handled = true;
                }
            };
        }
        public static void SetTopMost(this Form f)
        {
            if (HackerWindowTopMost)
                f.TopMost = true;
        }
        public static void SetPhParent(this Form f)
        {
            f.SetPhParent(true);
        }
        public static void SetPhParent(this Form f, bool hideInTaskbar)
        {
            if (Properties.Settings.Default.FloatChildWindows)
            {
                if (hideInTaskbar)
                    f.ShowInTaskbar = false;
                IntPtr oldParent = Win32.SetWindowLongPtr(f.Handle, GetWindowLongOffset.HwndParent, Program.HackerWindowHandle);
                f.FormClosing += (sender, e) => Win32.SetWindowLongPtr(f.Handle, GetWindowLongOffset.HwndParent, oldParent);
            }
        }
        private static void windowAlwaysOnTopItemClicked(object sender, EventArgs e)
        {
            Form f = ((WeakReference<Form>)((MenuItem)sender).Tag).Target;
            if (f == null)
                return;
            f.Invoke(new MethodInvoker(delegate
                {
                    f.TopMost = !f.TopMost;
                    if (f == HackerWindow)
                        HackerWindowTopMost = f.TopMost;
                }));
            UpdateWindowMenu(((MenuItem)sender).Parent, f);
        }
        private static void windowCloseItemClicked(object sender, EventArgs e)
        {
            Form f = ((WeakReference<Form>)((MenuItem)sender).Tag).Target;
            if (f == null)
                return;
            f.Invoke(new MethodInvoker(delegate { f.Close(); }));
        }
    }
}
