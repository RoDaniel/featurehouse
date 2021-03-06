

using System;
using System.Text;
using ProcessHacker.Common;
using ProcessHacker.Common.Objects;
using ProcessHacker.Native.Api;
using ProcessHacker.Native.Objects;

namespace ProcessHacker.Native.Security
{



    public sealed class Sid : BaseObject, IEquatable<Sid>
    {
        private static readonly byte[] _nullSidAuthority = { 0, 0, 0, 0, 0, 0 };
        private static readonly byte[] _worldSidAuthority = { 0, 0, 0, 0, 0, 1 };
        private static readonly byte[] _localSidAuthority = { 0, 0, 0, 0, 0, 2 };
        private static readonly byte[] _creatorSidAuthority = { 0, 0, 0, 0, 0, 3 };
        private static readonly byte[] _nonUniqueAuthority = { 0, 0, 0, 0, 0, 4 };
        private static readonly byte[] _ntAuthority = { 0, 0, 0, 0, 0, 5 };
        private static readonly byte[] _resourceManagerAuthority = { 0, 0, 0, 0, 0, 9 };

        public static Sid FromName(string name)
        {
            return LsaPolicyHandle.LookupPolicyHandle.LookupSid(name);
        }

        public static Sid FromPointer(IntPtr sid)
        {
            return new Sid(new MemoryRegion(sid), false);
        }

        public static Sid GetWellKnownSid(WellKnownSidType sidType)
        {
            using (MemoryAlloc memory = new MemoryAlloc(Win32.SecurityMaxSidSize))
            {
                int memorySize = memory.Size;

                if (!Win32.CreateWellKnownSid(sidType, IntPtr.Zero, memory, ref memorySize))
                    Win32.ThrowLastError();

                return new Sid(memory);
            }
        }

        public static byte[] GetWellKnownSidIdentifierAuthority(WellKnownSidIdentifierAuthority sidAuthority)
        {
            return GetWellKnownSidIdentifierAuthority(sidAuthority, true);
        }

        private static byte[] GetWellKnownSidIdentifierAuthority(WellKnownSidIdentifierAuthority sidAuthority, bool copy)
        {
            byte[] array;

            switch (sidAuthority)
            {
                case WellKnownSidIdentifierAuthority.Null:
                    array = _nullSidAuthority;
                    break;
                case WellKnownSidIdentifierAuthority.World:
                    array = _worldSidAuthority;
                    break;
                case WellKnownSidIdentifierAuthority.Local:
                    array = _localSidAuthority;
                    break;
                case WellKnownSidIdentifierAuthority.Creator:
                    array = _creatorSidAuthority;
                    break;
                case WellKnownSidIdentifierAuthority.NonUnique:
                    array = _nonUniqueAuthority;
                    break;
                case WellKnownSidIdentifierAuthority.NtAuthority:
                    array = _ntAuthority;
                    break;
                case WellKnownSidIdentifierAuthority.ResourceManager:
                    array = _resourceManagerAuthority;
                    break;
                default:
                    throw new ArgumentException("sidAuthority");
            }

            if (copy)
                return array.Duplicate();
            else
                return array;
        }

        public static implicit operator IntPtr(Sid sid)
        {
            return sid.Memory;
        }

        private MemoryRegion _memory;
        private string _systemName;
        private bool _hasAttributes;
        private SidAttributes _attributes;

        private string _stringSid;
        private string _domain;
        private string _name;
        private SidNameUse _nameUse = 0;

        private Sid(MemoryRegion sid, bool owned)
            : base(owned)
        {
            _memory = sid;
        }





        public Sid(string stringSid)
            : this(stringSid, null)
        { }






        public Sid(string stringSid, string systemName)
        {
            IntPtr sidMemory;

            if (!Win32.ConvertStringSidToSid(stringSid, out sidMemory))
                Win32.ThrowLastError();

            _memory = new LocalMemoryAlloc(sidMemory, true);
            _hasAttributes = false;
        }





        public Sid(IntPtr sid)
            : this(sid, null)
        { }






        public Sid(IntPtr sid, string systemName)
            : this(sid, false, 0, systemName)
        { }





        public Sid(SidAndAttributes saa)
            : this(saa.Sid, saa.Attributes)
        { }






        public Sid(IntPtr sid, SidAttributes attributes)
            : this(sid, attributes, null)
        { }







        public Sid(IntPtr sid, SidAttributes attributes, string systemName)
            : this(sid, true, attributes, systemName)
        { }

        private Sid(IntPtr sid, bool hasAttributes, SidAttributes attributes, string systemName)
        {
            NtStatus status;

            _memory = new MemoryAlloc(Win32.RtlLengthSid(sid));

            if ((status = Win32.RtlCopySid(_memory.Size, _memory, sid)) >= NtStatus.Error)
                Win32.ThrowLastError(status);

            _hasAttributes = hasAttributes;
            _attributes = attributes;
            _systemName = systemName;
        }

        protected override void DisposeObject(bool disposing)
        {
            _memory.Dispose(disposing);
        }

        public SidAttributes Attributes
        {
            get { return _attributes; }
        }

        public string DomainName
        {
            get
            {
                if (_domain == null)
                    this.GetNameAndUse(out _domain, out _name, out _nameUse);
                return _domain;
            }
        }

        public byte[] IdentifierAuthority
        {
            get
            {
                unsafe
                {
                    return Utils.Create((*Win32.RtlIdentifierAuthoritySid(this)).Value, 6);
                }
            }
        }

        public bool HasAttributes
        {
            get { return _hasAttributes; }
        }

        public int Length
        {
            get { return Win32.RtlLengthSid(this); }
        }

        public IntPtr Memory
        {
            get { return _memory; }
        }

        public SidNameUse NameUse
        {
            get
            {
                if (_nameUse == 0)
                    this.GetNameAndUse(out _domain, out _name, out _nameUse);
                return _nameUse;
            }
        }

        public string UserName
        {
            get
            {
                if (_name == null)
                    this.GetNameAndUse(out _domain, out _name, out _nameUse);
                return _name;
            }
        }

        public int[] SubAuthorities
        {
            get
            {
                unsafe
                {
                    byte count = *Win32.RtlSubAuthorityCountSid(this);
                    int[] subAuthorities = new int[count];

                    for (int i = 0; i < count; i++)
                        subAuthorities[i] = *Win32.RtlSubAuthoritySid(this, i);

                    return subAuthorities;
                }
            }
        }

        public string StringSid
        {
            get
            {
                if (_stringSid == null)
                    _stringSid = this.GetString();
                return _stringSid;
            }
        }

        public string SystemName
        {
            get { return _systemName; }
        }

        public Sid Clone()
        {
            return new Sid(this);
        }

        public bool DomainEquals(Sid obj)
        {
            bool equal;

            if (!Win32.EqualDomainSid(this, obj, out equal))
                Win32.ThrowLastError();

            return equal;
        }

        public bool Equals(Sid obj)
        {
            return Win32.RtlEqualSid(this, obj);
        }

        public string GetFullName(bool includeDomain)
        {
            try
            {
                if (string.IsNullOrEmpty(this.UserName))
                    return this.StringSid;
                if (includeDomain)
                    return this.DomainName + "\\" + this.UserName;
                else
                    return this.UserName;
            }
            catch
            {
                return this.StringSid;
            }
        }

        public override int GetHashCode()
        {
            int hashCode = 0x12345678;
            byte[] identifierAuthority = this.IdentifierAuthority;
            int[] subAuthorities = this.SubAuthorities;

            for (int i = 0; i < subAuthorities.Length; i++)
            {
                hashCode ^= identifierAuthority[(uint)hashCode % identifierAuthority.Length];

                hashCode ^= (hashCode >> 24) | ((hashCode >> 16) << 8) | ((hashCode >> 24) << 16) | (hashCode << 24);
                hashCode ^= subAuthorities[(uint)hashCode % subAuthorities.Length];
            }

            return hashCode;
        }

        private void GetNameAndUse(out string domain, out string name, out SidNameUse nameUse)
        {
            name = LsaPolicyHandle.LookupPolicyHandle.LookupName(this, out nameUse, out domain);
        }

        public WellKnownSidIdentifierAuthority GetWellKnownIdentifierAuthority()
        {
            byte[] identifierAuthority = this.IdentifierAuthority;

            foreach (WellKnownSidIdentifierAuthority value in
                Enum.GetValues(typeof(WellKnownSidIdentifierAuthority)))
            {
                if (value == WellKnownSidIdentifierAuthority.None)
                    continue;

                if (Utils.Equals(identifierAuthority, GetWellKnownSidIdentifierAuthority(value, false)))
                    return value;
            }

            return WellKnownSidIdentifierAuthority.None;
        }

        private string GetString()
        {
            NtStatus status;
            UnicodeString str = new UnicodeString();

            if ((status = Win32.RtlConvertSidToUnicodeString(ref str, this, true)) >= NtStatus.Error)
                Win32.ThrowLastError(status);

            using (str)
                return str.Read();
        }

        public bool IsValid()
        {
            return Win32.RtlValidSid(this);
        }

        public bool PrefixEquals(Sid obj)
        {
            return Win32.RtlEqualPrefixSid(this, obj);
        }

        public SidAndAttributes ToSidAndAttributes()
        {
            return new SidAndAttributes()
            {
                Attributes = _attributes,
                Sid = this
            };
        }

        public override string ToString()
        {
            return this.StringSid;
        }
    }

    public enum WellKnownSidIdentifierAuthority
    {
        None = 0,
        Null,
        World,
        Local,
        Creator,
        NonUnique,
        NtAuthority,
        ResourceManager
    }
}
