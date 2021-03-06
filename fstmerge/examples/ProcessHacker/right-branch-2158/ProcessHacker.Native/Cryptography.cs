

using System;
using System.Runtime.InteropServices;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using ProcessHacker.Common;
using ProcessHacker.Native.Api;
using ProcessHacker.Native.Objects;
using ProcessHacker.Native.Security;

namespace ProcessHacker.Native
{
    public enum VerifyResult : int
    {
        Unknown = 0,
        NoSignature,
        Trusted,
        TrustedInstaller,
        Expired,
        Revoked,
        Distrust,
        SecuritySettings
    }

    public static class Cryptography
    {
        public static readonly Guid DriverActionVerify =
            new Guid("{f750e6c3-38ee-11d1-85e5-00c04fc295ee}");
        public static readonly Guid HttpsProvAction =
            new Guid("{573e31f8-aaba-11d0-8ccb-00c04fc295ee}");
        public static readonly Guid OfficeSignActionVerify =
            new Guid("{5555c2cd-17fb-11d1-85c4-00c04fc295ee}");
        public static readonly Guid WintrustActionGenericCertVerify =
            new Guid("{189a3842-3041-11d1-85e1-00c04fc295ee}");
        public static readonly Guid WintrustActionGenericChainVerify =
            new Guid("{fc451c16-ac75-11d1-b4b8-00c04fb66ea0}");
        public static readonly Guid WintrustActionGenericVerifyV2 =
            new Guid("{00aac56b-cd44-11d0-8cc2-00c04fc295ee}");
        public static readonly System.Guid WintrustActionTrustProviderTest =
            new Guid("{573e31f8-ddba-11d0-8ccb-00c04fc295ee}");

        public static string GetFileSubjectValue(string fileName, string keyName)
        {
            X509Certificate cert = X509Certificate.CreateFromSignedFile(fileName);
            Tokenizer t = new Tokenizer(cert.Subject);


            while (true)
            {
                t.EatWhitespace();
                string key = t.EatId();

                if (string.IsNullOrEmpty(key))
                    return null;

                t.EatWhitespace();
                string equals = t.EatSymbol();

                if (equals != "=")
                    return null;

                t.EatWhitespace();
                string value = t.EatQuotedString();

                if (string.IsNullOrEmpty(value))
                {

                    value = t.EatUntil(',');
                }

                if (string.IsNullOrEmpty(value))
                    return null;

                if (key == keyName)
                    return value;
            }
        }

        public static VerifyResult StatusToVerifyResult(uint status)
        {
            if (status == 0)
                return VerifyResult.Trusted;
            else if (status == 0x800b0100)
                return VerifyResult.NoSignature;
            else if (status == 0x800b0101)
                return VerifyResult.Expired;
            else if (status == 0x800b010c)
                return VerifyResult.Revoked;
            else if (status == 0x800b0111)
                return VerifyResult.Distrust;
            else if (status == 0x80092026)
                return VerifyResult.SecuritySettings;
            else
                return VerifyResult.SecuritySettings;
        }

        public static VerifyResult VerifyFile(string fileName)
        {
            VerifyResult result = VerifyResult.NoSignature;

            using (MemoryAlloc strMem = new MemoryAlloc(fileName.Length * 2 + 2))
            {
                WintrustFileInfo fileInfo = new WintrustFileInfo();

                strMem.WriteUnicodeString(0, fileName);
                strMem.WriteByte(fileName.Length * 2, 0);
                strMem.WriteByte(fileName.Length * 2 + 1, 0);

                fileInfo.Size = Marshal.SizeOf(fileInfo);
                fileInfo.FilePath = strMem;

                WintrustData trustData = new WintrustData();

                trustData.Size = 12 * 4;
                trustData.UIChoice = 2;
                trustData.UnionChoice = 1;
                trustData.RevocationChecks = WtRevocationChecks.None;
                trustData.ProvFlags = WtProvFlags.Safer;

                if (OSVersion.IsAboveOrEqual(WindowsVersion.Vista))
                    trustData.ProvFlags |= WtProvFlags.CacheOnlyUrlRetrieval;

                using (MemoryAlloc mem = new MemoryAlloc(fileInfo.Size))
                {
                    Marshal.StructureToPtr(fileInfo, mem, false);
                    trustData.UnionData = mem;

                    uint winTrustResult = Win32.WinVerifyTrust(IntPtr.Zero, WintrustActionGenericVerifyV2, ref trustData);

                    result = StatusToVerifyResult(winTrustResult);
                }
            }

            if (result == VerifyResult.NoSignature)
            {
                using (FileHandle sourceFile = FileHandle.CreateWin32(fileName, FileAccess.GenericRead, FileShareMode.Read,
                    FileCreationDispositionWin32.OpenExisting))
                {
                    byte[] hash = new byte[256];
                    int hashLength = 256;

                    if (!Win32.CryptCATAdminCalcHashFromFileHandle(sourceFile, ref hashLength, hash, 0))
                    {
                        hash = new byte[hashLength];

                        if (!Win32.CryptCATAdminCalcHashFromFileHandle(sourceFile, ref hashLength, hash, 0))
                            return VerifyResult.NoSignature;
                    }

                    StringBuilder memberTag = new StringBuilder(hashLength * 2);

                    for (int i = 0; i < hashLength; i++)
                        memberTag.Append(hash[i].ToString("X2"));

                    IntPtr catAdmin;

                    if (!Win32.CryptCATAdminAcquireContext(out catAdmin, DriverActionVerify, 0))
                        return VerifyResult.NoSignature;

                    IntPtr catInfo = Win32.CryptCATAdminEnumCatalogFromHash(catAdmin, hash, hashLength, 0, IntPtr.Zero);

                    if (catInfo == IntPtr.Zero)
                    {
                        Win32.CryptCATAdminReleaseContext(catAdmin, 0);
                        return VerifyResult.NoSignature;
                    }

                    CatalogInfo ci;

                    if (!Win32.CryptCATCatalogInfoFromContext(catInfo, out ci, 0))
                    {
                        Win32.CryptCATAdminReleaseCatalogContext(catAdmin, catInfo, 0);
                        Win32.CryptCATAdminReleaseContext(catAdmin, 0);
                        return VerifyResult.NoSignature;
                    }

                    WintrustCatalogInfo wci = new WintrustCatalogInfo();

                    wci.Size = Marshal.SizeOf(wci);
                    wci.CatalogFilePath = ci.CatalogFile;
                    wci.MemberFilePath = fileName;
                    wci.MemberTag = memberTag.ToString();

                    WintrustData trustData = new WintrustData();

                    trustData.Size = 12 * 4;
                    trustData.UIChoice = 1;
                    trustData.UnionChoice = 2;
                    trustData.RevocationChecks = WtRevocationChecks.None;

                    if (OSVersion.IsAboveOrEqual(WindowsVersion.Vista))
                        trustData.ProvFlags = WtProvFlags.CacheOnlyUrlRetrieval;

                    using (MemoryAlloc mem = new MemoryAlloc(wci.Size))
                    {
                        Marshal.StructureToPtr(wci, mem, false);

                        try
                        {
                            trustData.UnionData = mem;

                            uint winTrustResult = Win32.WinVerifyTrust(IntPtr.Zero, DriverActionVerify, ref trustData);

                            result = StatusToVerifyResult(winTrustResult);
                        }
                        finally
                        {
                            Win32.CryptCATAdminReleaseCatalogContext(catAdmin, catInfo, 0);
                            Win32.CryptCATAdminReleaseContext(catAdmin, 0);
                            Marshal.DestroyStructure(mem, typeof(WintrustCatalogInfo));
                        }
                    }
                }
            }

            return result;
        }
    }
}
