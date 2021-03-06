

using System;
using System.Collections.Generic;
using System.Text;
using Aga.Controls.Tree.NodeControls;
using System.Drawing;
using Aga.Controls.Tree;

namespace ProcessHacker.Components
{
    public class NodePlotter : BindableControl
    {
        public class PlotterInfo
        {
            public bool UseLongData;
            public bool UseSecondLine;
            public bool OverlaySecondLine;
            public IList<float> Data1;
            public IList<float> Data2;
            public IList<long> LongData1;
            public IList<long> LongData2;
            public Color LineColor1;
            public Color LineColor2;
        }

        private Plotter _plotter;

        public override Size MeasureSize(TreeNodeAdv node, DrawContext context)
        {
            return new Size(this.ParentColumn.Width, this.Parent.RowHeight);
        }

        public override void Draw(TreeNodeAdv node, DrawContext context)
        {
            PlotterInfo info = GetValue(node) as PlotterInfo;

            if (_plotter == null)
            {
                _plotter = new Plotter();
                _plotter.BackColor = Color.Black;
                _plotter.ShowGrid = false;
                _plotter.OverlaySecondLine = false;
            }

            if (info.UseLongData)
            {
                _plotter.UseLongData = true;
                _plotter.LongData1 = info.LongData1;
                _plotter.LongData2 = info.LongData2;
            }
            else
            {
                _plotter.UseLongData = false;
                _plotter.Data1 = info.Data1;
                _plotter.Data2 = info.Data2;
            }

            _plotter.UseSecondLine = info.UseSecondLine;
            _plotter.OverlaySecondLine = info.OverlaySecondLine;
            _plotter.LineColor1 = info.LineColor1;
            _plotter.LineColor2 = info.LineColor2;

            if ((_plotter.Width != context.Bounds.Width - 1 ||
                _plotter.Height != context.Bounds.Height - 1) &&
                context.Bounds.Width > 1 && context.Bounds.Height > 1)
                _plotter.Size = new Size(context.Bounds.Width - 1, context.Bounds.Height - 1);

            _plotter.Draw();

            using (Bitmap b = new Bitmap(_plotter.Width, _plotter.Height))
            {
                _plotter.DrawToBitmap(b, new Rectangle(0, 0, b.Width, b.Height));
                context.Graphics.DrawImage(b, context.Bounds.Location);
            }
        }
    }
}
