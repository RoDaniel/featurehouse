using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using System.Globalization;
using Eraser.Manager;
using Eraser.Util;
namespace Eraser.DefaultPlugins
{
 public partial class SettingsForm : Form
 {
  public SettingsForm()
  {
   InitializeComponent();
   UXThemeApi.UpdateControlTheme(this);
   foreach (ErasureMethod method in ErasureMethodManager.Items.Values)
    if (method.Guid != new Guid("{0C2E07BF-0207-49a3-ADE8-46F9E1499C01}"))
     fl16MethodCmb.Items.Add(method);
   DefaultPluginSettings settings = DefaultPlugin.Settings;
   if (settings.FL16Method != Guid.Empty)
    foreach (object item in fl16MethodCmb.Items)
     if (((ErasureMethod)item).Guid == settings.FL16Method)
     {
      fl16MethodCmb.SelectedItem = item;
      break;
     }
   if (fl16MethodCmb.SelectedIndex == -1)
   {
    Guid defaultMethodGuid =
     ManagerLibrary.Settings.DefaultFileErasureMethod;
    foreach (object item in fl16MethodCmb.Items)
     if (((ErasureMethod)item).Guid == defaultMethodGuid)
     {
      fl16MethodCmb.SelectedItem = item;
      break;
     }
   }
   if (DefaultPlugin.Settings.EraseCustom != null)
   {
    customMethods = DefaultPlugin.Settings.EraseCustom;
    foreach (Guid guid in customMethods.Keys)
     AddMethod(customMethods[guid]);
   }
   else
    customMethods = new Dictionary<Guid, CustomErasureMethod>();
  }
  private void customMethod_ItemActivate(object sender, EventArgs e)
  {
   CustomMethodEditorForm editorForm = new CustomMethodEditorForm();
   ListViewItem item = customMethod.SelectedItems[0];
   editorForm.Method = (CustomErasureMethod)item.Tag;
   if (editorForm.ShowDialog() == DialogResult.OK)
   {
    CustomErasureMethod method = editorForm.Method;
    removeCustomMethods.Add(method.Guid);
    customMethod.Items.Remove(item);
    customMethods.Remove(method.Guid);
    method = editorForm.Method;
    addCustomMethods.Add(method);
    AddMethod(method);
   }
  }
  private void customMethodAdd_Click(object sender, EventArgs e)
  {
   CustomMethodEditorForm form = new CustomMethodEditorForm();
   if (form.ShowDialog() == DialogResult.OK)
   {
    CustomErasureMethod method = form.Method;
    customMethods.Add(method.Guid, method);
    addCustomMethods.Add(method);
    AddMethod(method);
   }
  }
  private void customMethodContextMenuStrip_Opening(object sender, CancelEventArgs e)
  {
   e.Cancel = customMethod.SelectedIndices.Count == 0;
  }
  private void deleteMethodToolStripMenuItem_Click(object sender, EventArgs e)
  {
   foreach (ListViewItem item in customMethod.SelectedItems)
   {
    CustomErasureMethod method = (CustomErasureMethod)item.Tag;
    if (addCustomMethods.IndexOf(method) >= 0)
     addCustomMethods.Remove(method);
    else
     removeCustomMethods.Add(method.Guid);
    customMethod.Items.Remove(item);
   }
  }
  private void okBtn_Click(object sender, EventArgs e)
  {
   if (fl16MethodCmb.SelectedIndex == -1)
   {
    errorProvider.SetError(fl16MethodCmb, S._("An invalid erasure method was selected."));
    return;
   }
   DefaultPlugin.Settings.FL16Method = ((ErasureMethod)fl16MethodCmb.SelectedItem).Guid;
   foreach (Guid guid in removeCustomMethods)
   {
    customMethods.Remove(guid);
    ErasureMethodManager.Unregister(guid);
   }
   DefaultPlugin.Settings.EraseCustom = customMethods;
   foreach (CustomErasureMethod method in addCustomMethods)
    ErasureMethodManager.Register(new EraseCustom(method), new object[] { method });
   DialogResult = DialogResult.OK;
   Close();
  }
  private void AddMethod(CustomErasureMethod method)
  {
   ListViewItem item = customMethod.Items.Add(method.Name);
   item.SubItems.Add(method.Passes.Length.ToString(CultureInfo.CurrentCulture));
   item.Tag = method;
  }
  private Dictionary<Guid, CustomErasureMethod> customMethods;
  private List<CustomErasureMethod> addCustomMethods = new List<CustomErasureMethod>();
  private List<Guid> removeCustomMethods = new List<Guid>();
 }
}