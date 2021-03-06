namespace ProcessHacker.Components
{
    partial class HandleList
    {



        private System.ComponentModel.IContainer components = null;





        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }

            _highlightingContext.Dispose();
            this.Provider = null;

            base.Dispose(disposing);
        }







        private void InitializeComponent()
        {
            this.components = new System.ComponentModel.Container();
            this.listHandles = new System.Windows.Forms.ListView();
            this.columnType = new System.Windows.Forms.ColumnHeader();
            this.columnName = new System.Windows.Forms.ColumnHeader();
            this.columnHandle = new System.Windows.Forms.ColumnHeader();
            this.vistaMenu = new wyDay.Controls.VistaMenu(this.components);
            this.closeHandleMenuItem = new System.Windows.Forms.MenuItem();
            this.copyHandleMenuItem = new System.Windows.Forms.MenuItem();
            this.menuHandle = new System.Windows.Forms.ContextMenu();
            this.protectedMenuItem = new System.Windows.Forms.MenuItem();
            this.inheritMenuItem = new System.Windows.Forms.MenuItem();
            this.menuItem11 = new System.Windows.Forms.MenuItem();
            this.propertiesHandleMenuItem = new System.Windows.Forms.MenuItem();
            ((System.ComponentModel.ISupportInitialize)(this.vistaMenu)).BeginInit();
            this.SuspendLayout();



            this.listHandles.AllowColumnReorder = true;
            this.listHandles.Columns.AddRange(new System.Windows.Forms.ColumnHeader[] {
            this.columnType,
            this.columnName,
            this.columnHandle});
            this.listHandles.Dock = System.Windows.Forms.DockStyle.Fill;
            this.listHandles.FullRowSelect = true;
            this.listHandles.HideSelection = false;
            this.listHandles.Location = new System.Drawing.Point(0, 0);
            this.listHandles.Name = "listHandles";
            this.listHandles.ShowItemToolTips = true;
            this.listHandles.Size = new System.Drawing.Size(450, 472);
            this.listHandles.Sorting = System.Windows.Forms.SortOrder.Ascending;
            this.listHandles.TabIndex = 3;
            this.listHandles.UseCompatibleStateImageBehavior = false;
            this.listHandles.View = System.Windows.Forms.View.Details;



            this.columnType.Text = "Type";
            this.columnType.Width = 100;



            this.columnName.Text = "Name";
            this.columnName.Width = 250;



            this.columnHandle.Text = "Handle";



            this.vistaMenu.ContainerControl = this;
            this.vistaMenu.DelaySetImageCalls = false;



            this.vistaMenu.SetImage(this.closeHandleMenuItem, global::ProcessHacker.Properties.Resources.cross);
            this.closeHandleMenuItem.Index = 0;
            this.closeHandleMenuItem.Text = "Close";
            this.closeHandleMenuItem.Click += new System.EventHandler(this.closeHandleMenuItem_Click);



            this.vistaMenu.SetImage(this.copyHandleMenuItem, global::ProcessHacker.Properties.Resources.page_copy);
            this.copyHandleMenuItem.Index = 4;
            this.copyHandleMenuItem.Text = "&Copy";



            this.menuHandle.MenuItems.AddRange(new System.Windows.Forms.MenuItem[] {
            this.closeHandleMenuItem,
            this.protectedMenuItem,
            this.inheritMenuItem,
            this.menuItem11,
            this.copyHandleMenuItem,
            this.propertiesHandleMenuItem});
            this.menuHandle.Popup += new System.EventHandler(this.menuHandle_Popup);



            this.protectedMenuItem.Index = 1;
            this.protectedMenuItem.Text = "Protected";
            this.protectedMenuItem.Click += new System.EventHandler(this.protectedMenuItem_Click);



            this.inheritMenuItem.Index = 2;
            this.inheritMenuItem.Text = "Inherit";
            this.inheritMenuItem.Click += new System.EventHandler(this.inheritMenuItem_Click);



            this.menuItem11.Index = 3;
            this.menuItem11.Text = "-";



            this.propertiesHandleMenuItem.Index = 5;
            this.propertiesHandleMenuItem.Text = "&Properties";
            this.propertiesHandleMenuItem.Click += new System.EventHandler(this.propertiesHandleMenuItem_Click);



            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.listHandles);
            this.DoubleBuffered = true;
            this.Name = "HandleList";
            this.Size = new System.Drawing.Size(450, 472);
            ((System.ComponentModel.ISupportInitialize)(this.vistaMenu)).EndInit();
            this.ResumeLayout(false);

        }



        private System.Windows.Forms.ListView listHandles;
        private System.Windows.Forms.ColumnHeader columnType;
        private System.Windows.Forms.ColumnHeader columnName;
        private System.Windows.Forms.ColumnHeader columnHandle;
        private wyDay.Controls.VistaMenu vistaMenu;
        private System.Windows.Forms.ContextMenu menuHandle;
        private System.Windows.Forms.MenuItem closeHandleMenuItem;
        private System.Windows.Forms.MenuItem copyHandleMenuItem;
        private System.Windows.Forms.MenuItem menuItem11;
        private System.Windows.Forms.MenuItem propertiesHandleMenuItem;
        private System.Windows.Forms.MenuItem protectedMenuItem;
        private System.Windows.Forms.MenuItem inheritMenuItem;
    }
}
