namespace Debugger.Interop.CorPub
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Runtime.InteropServices;
    using System.Text;
 [ComImport, Guid("D6315C8F-5A6A-11D3-8F84-00A0C9B4D50C"), InterfaceType((short) 1)]
 public interface ICorPublishAppDomain
 {
  [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType=MethodCodeType.Runtime)]
  void GetID(out uint puId);
  [MethodImpl(MethodImplOptions.InternalCall, MethodCodeType=MethodCodeType.Runtime)]
  void GetName([In] uint cchName, out uint pcchName, [Out, MarshalAs(UnmanagedType.LPWStr)] StringBuilder szName);
 }
}
