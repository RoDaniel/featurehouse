

using System;
using System.Collections.Generic;
using System.Text;
using ProcessHacker.Native;
using ProcessHacker.Native.Api;
using ProcessHacker.Native.Security;

namespace ProcessHacker.Native.Objects
{
    public class KeyHandle : NativeHandle<KeyAccess>
    {
        public static KeyHandle Create(
            KeyAccess access,
            string name,
            RegOptions createOptions
            )
        {
            return Create(access, name, 0, null, createOptions);
        }

        public static KeyHandle Create(
            KeyAccess access,
            string name,
            ObjectFlags objectFlags,
            KeyHandle rootDirectory,
            RegOptions createOptions
            )
        {
            KeyCreationDisposition creationDisposition;

            return Create(access, name, objectFlags, rootDirectory, createOptions, out creationDisposition);
        }

        public static KeyHandle Create(
            KeyAccess access,
            string name,
            ObjectFlags objectFlags,
            KeyHandle rootDirectory,
            RegOptions createOptions,
            out KeyCreationDisposition creationDisposition
            )
        {
            NtStatus status;
            ObjectAttributes oa = new ObjectAttributes(name, objectFlags, rootDirectory);
            IntPtr handle;

            try
            {
                if ((status = Win32.NtCreateKey(
                    out handle,
                    access,
                    ref oa,
                    0,
                    IntPtr.Zero,
                    createOptions,
                    out creationDisposition
                    )) >= NtStatus.Error)
                    Win32.ThrowLastError(status);
            }
            finally
            {
                oa.Dispose();
            }

            return new KeyHandle(handle, true);
        }

        private KeyHandle(IntPtr handle, bool owned)
            : base(handle, owned)
        { }

        public KeyHandle(string name, KeyAccess access)
            : this(name, 0, null, access)
        { }

        public KeyHandle(string name, ObjectFlags objectFlags, KeyHandle rootDirectory, KeyAccess access)
        {
            NtStatus status;
            ObjectAttributes oa = new ObjectAttributes(name, objectFlags, rootDirectory);
            IntPtr handle;

            try
            {
                if ((status = Win32.NtOpenKey(
                    out handle,
                    access,
                    ref oa
                    )) >= NtStatus.Error)
                    Win32.ThrowLastError(status);
            }
            finally
            {
                oa.Dispose();
            }

            this.Handle = handle;
        }

        public void Delete()
        {
            NtStatus status;

            if ((status = Win32.NtDeleteKey(this)) >= NtStatus.Error)
                Win32.ThrowLastError(status);
        }

        public void DeleteValue(string name)
        {
            NtStatus status;
            UnicodeString nameStr = new UnicodeString(name);

            try
            {
                if ((status = Win32.NtDeleteValueKey(this, ref nameStr)) >= NtStatus.Error)
                    Win32.ThrowLastError(status);
            }
            finally
            {
                nameStr.Dispose();
            }
        }
    }
}
