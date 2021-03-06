namespace ProcessHacker.Components
{
    partial class ServiceList
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(ServiceList));
            this.listServices = new System.Windows.Forms.ListView();
            this.columnName = new System.Windows.Forms.ColumnHeader();
            this.columnDescription = new System.Windows.Forms.ColumnHeader();
            this.columnType = new System.Windows.Forms.ColumnHeader();
            this.columnStatus = new System.Windows.Forms.ColumnHeader();
            this.columnStartType = new System.Windows.Forms.ColumnHeader();
            this.columnPID = new System.Windows.Forms.ColumnHeader();
            this.imageList = new System.Windows.Forms.ImageList(this.components);
            this.SuspendLayout();



            this.listServices.AllowColumnReorder = true;
            this.listServices.Columns.AddRange(new System.Windows.Forms.ColumnHeader[] {
            this.columnName,
            this.columnDescription,
            this.columnType,
            this.columnStatus,
            this.columnStartType,
            this.columnPID});
            this.listServices.Dock = System.Windows.Forms.DockStyle.Fill;
            this.listServices.FullRowSelect = true;
            this.listServices.HideSelection = false;
            this.listServices.Location = new System.Drawing.Point(0, 0);
            this.listServices.Name = "listServices";
            this.listServices.ShowItemToolTips = true;
            this.listServices.Size = new System.Drawing.Size(685, 472);
            this.listServices.SmallImageList = this.imageList;
            this.listServices.Sorting = System.Windows.Forms.SortOrder.Ascending;
            this.listServices.TabIndex = 1;
            this.listServices.UseCompatibleStateImageBehavior = false;
            this.listServices.View = System.Windows.Forms.View.Details;



            this.columnName.Text = "Name";
            this.columnName.Width = 150;



            this.columnDescription.Text = "Description";
            this.columnDescription.Width = 260;



            this.columnType.Text = "Type";
            this.columnType.Width = 120;



            this.columnStatus.Text = "Status";
            this.columnStatus.Width = 80;



            this.columnStartType.Text = "Start Type";
            this.columnStartType.Width = 80;



            this.columnPID.Text = "PID";



            this.imageList.ImageStream = ((System.Windows.Forms.ImageListStreamer)(resources.GetObject("imageList.ImageStream")));
            this.imageList.TransparentColor = System.Drawing.Color.Transparent;
            this.imageList.Images.SetKeyName(0, "Win32");
            this.imageList.Images.SetKeyName(1, "Driver");
            this.imageList.Images.SetKeyName(2, "Interactive");
            this.imageList.Images.SetKeyName(3, "FS");



            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.Controls.Add(this.listServices);
            this.DoubleBuffered = true;
            this.Name = "ServiceList";
            this.Size = new System.Drawing.Size(685, 472);
            this.ResumeLayout(false);

        }



        private System.Windows.Forms.ListView listServices;
        private System.Windows.Forms.ColumnHeader columnName;
        private System.Windows.Forms.ImageList imageList;
        private System.Windows.Forms.ColumnHeader columnDescription;
        private System.Windows.Forms.ColumnHeader columnStatus;
        private System.Windows.Forms.ColumnHeader columnPID;
        private System.Windows.Forms.ColumnHeader columnType;
        private System.Windows.Forms.ColumnHeader columnStartType;
    }
}
