

package com.lowagie.text.pdf;

import java.util.ArrayList;
import java.util.Iterator;

import com.lowagie.text.Cell;
import com.lowagie.text.Element;
import com.lowagie.text.Rectangle;
import com.lowagie.text.Row;
import com.lowagie.text.Table;



public class PdfTable extends Rectangle {
    
    
    
    
    private int columns;
    
    
    private ArrayList<PdfCell> headercells;
    
    
    private ArrayList<PdfCell> cells;
    
    
    protected Table table;
    
    
    protected float[] positions;

    

    
    
    PdfTable(Table table, float left, float right, float top, boolean supportUpdateRowAdditions) {
        
        super(left, top, right, top);
        this.table = table;
        table.complete();

        
        cloneNonPositionParameters(table);

        this.columns = table.getColumns();
        positions = table.getWidths(left, right - left);
        
        
        setLeft(positions[0]);
        setRight(positions[positions.length - 1]);
        
        headercells = new ArrayList<PdfCell>();
        cells = new ArrayList<PdfCell>();

        updateRowAdditionsInternal();
        if (supportUpdateRowAdditions) {
            table.deleteAllRows();
        }
    }

    

    
    
    void updateRowAdditions() {
        table.complete();
        updateRowAdditionsInternal();
        table.deleteAllRows();
    }
    
    
    
    private void updateRowAdditionsInternal() {
        
        Row row;
        int prevRows = rows();
        int rowNumber = 0;
        int groupNumber = 0;
        boolean groupChange;
        int firstDataRow = table.getLastHeaderRow() + 1;
        Cell cell;
        PdfCell currentCell;
        ArrayList<PdfCell> newCells = new ArrayList<PdfCell>();
        int rows = table.size() + 1;
        float[] offsets = new float[rows];
        for (int i = 0; i < rows; i++) {
            offsets[i] = getBottom();
        }
        
        
        for (Iterator<Row> rowIterator = table.iterator(); rowIterator.hasNext(); ) {
            groupChange = false;
            row = rowIterator.next();
            if (row.isEmpty()) {
                if (rowNumber < rows - 1 && offsets[rowNumber + 1] > offsets[rowNumber]) offsets[rowNumber + 1] = offsets[rowNumber];
            }
            else {
                for(int i = 0; i < row.getColumns(); i++) {
                    cell = (Cell) row.getCell(i);
                    if (cell != null) {
                        currentCell = new PdfCell(cell, rowNumber+prevRows, positions[i], positions[i + cell.getColspan()], offsets[rowNumber], cellspacing(), cellpadding());
                        try {
                     if (offsets[rowNumber] - currentCell.getHeight() - cellpadding() < offsets[rowNumber + currentCell.rowspan()]) {
                        offsets[rowNumber + currentCell.rowspan()] = offsets[rowNumber] - currentCell.getHeight() - cellpadding();
                            }
                        }
                        catch(ArrayIndexOutOfBoundsException aioobe) {
                            if (offsets[rowNumber] - currentCell.getHeight() < offsets[rows - 1]) {
                                offsets[rows - 1] = offsets[rowNumber] - currentCell.getHeight();
                            }
                        }
                        if (rowNumber < firstDataRow) {
                            currentCell.setHeader();
                            headercells.add(currentCell);
                        }
                        currentCell.setGroupNumber(groupNumber);
                        groupChange |= cell.getGroupChange();
                        newCells.add(currentCell);
                    }
                }
            }
            rowNumber++;
            if( groupChange ) groupNumber++;
        }
        
        
        int n = newCells.size();
        for (int i = 0; i < n; i++) {
            currentCell = newCells.get(i);
            try {
                currentCell.setBottom(offsets[currentCell.rownumber()-prevRows + currentCell.rowspan()]);
            }
            catch(ArrayIndexOutOfBoundsException aioobe) {
                currentCell.setBottom(offsets[rows - 1]);
            }
        }
        cells.addAll(newCells);
        setBottom(offsets[rows - 1]);
    }

    
    
    int rows() {
        return cells.isEmpty() ? 0 : cells.get(cells.size()-1).rownumber()+1; 
    }

    
    public int type() {
        return Element.TABLE;
    }
    
    
    
    ArrayList<PdfCell> getHeaderCells() {
        return headercells;
    }
    
    
    
    boolean hasHeader() {
        return !headercells.isEmpty();
    }
    
    
    
    ArrayList<PdfCell> getCells() {
        return cells;
    }
    
    
    
    int columns() {
        return columns;
    }
    
    
    
    final float cellpadding() {
        return table.getPadding();
    }
    
    
    
    final float cellspacing() {
        return table.getSpacing();
    }
    
    

    public final boolean hasToFitPageTable() {
        return table.isTableFitsPage();
    }

    
    
    public final boolean hasToFitPageCells() {
        return table.isCellsFitPage();
    }

    
    public float getOffset() {
        return table.getOffset();
    }
}
