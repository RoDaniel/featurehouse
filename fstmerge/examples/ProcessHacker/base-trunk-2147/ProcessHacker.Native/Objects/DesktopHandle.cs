

using System;
using System.Collections.Generic;
using System.Text;
using ProcessHacker.Native.Api;
using ProcessHacker.Native.Security;

namespace ProcessHacker.Native.Objects
{
    public sealed class DesktopHandle : UserHandle<DesktopAccess>
    {
        public static DesktopHandle GetCurrent()
        {
            return GetThreadDesktop(Win32.GetCurrentThreadId());
        }

        public static DesktopHandle GetThreadDesktop(int threadId)
        {
            IntPtr handle = Win32.GetThreadDesktop(threadId);

            if (handle == IntPtr.Zero)
                Win32.ThrowLastError();

            return new DesktopHandle(handle, false);
        }

        public DesktopHandle(string name, bool allowOtherAccountHook, DesktopAccess access)
        {
            this.Handle = Win32.OpenDesktop(name, allowOtherAccountHook ? 1 : 0, false, access);

            if (this.Handle == IntPtr.Zero)
                Win32.ThrowLastError();
        }

        private DesktopHandle(IntPtr handle, bool owned)
            : base(handle, owned)
        { }

        protected override void Close()
        {
            Win32.CloseDesktop(this);
        }

        public void SetCurrent()
        {
            if (!Win32.SetThreadDesktop(this))
                Win32.ThrowLastError();
        }

        public void Switch()
        {
            if (!Win32.SwitchDesktop(this))
                Win32.ThrowLastError();
        }
    }
}
