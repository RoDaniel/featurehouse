

package com.lowagie.text.rtf.text;

import java.awt.Color;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.OutputStream;

import com.lowagie.text.Chunk;
import com.lowagie.text.rtf.RtfElement;
import com.lowagie.text.rtf.document.RtfDocument;
import com.lowagie.text.rtf.style.RtfColor;
import com.lowagie.text.rtf.style.RtfFont;



public class RtfChunk extends RtfElement {

    
    private static final byte[] FONT_SUBSCRIPT = "\\sub".getBytes();
    
    private static final byte[] FONT_SUPERSCRIPT = "\\super".getBytes();
    
    private static final byte[] FONT_END_SUPER_SUBSCRIPT = "\\nosupersub".getBytes();
    
    private static final byte[] HIGHLIGHT = "\\highlight".getBytes();

    
    private RtfFont font = null;
    
    private String content = "";
    
    private boolean softLineBreaks = false;
    
    private float superSubScript = 0;
    
    private RtfColor background = null;

    
    public RtfChunk(RtfDocument doc, Chunk chunk) {
        super(doc);
        
        if(chunk == null) {
            return;
        }
        
        if(chunk.getAttributes() != null && chunk.getAttributes().get(Chunk.SUBSUPSCRIPT) != null) {
            this.superSubScript = ((Float)chunk.getAttributes().get(Chunk.SUBSUPSCRIPT)).floatValue();
        }
        if(chunk.getAttributes() != null && chunk.getAttributes().get(Chunk.BACKGROUND) != null) {
            this.background = new RtfColor(this.document, (Color) ((Object[]) chunk.getAttributes().get(Chunk.BACKGROUND))[0]);
        }
        font = new RtfFont(doc, chunk.getFont());
        content = chunk.getContent();
    }
    
    
    public byte[] write() {
        ByteArrayOutputStream result = new ByteArrayOutputStream();
        try {
            writeContent(result);
        } catch(IOException ioe) {
            ioe.printStackTrace();
        }
        return result.toByteArray();
    }
     
    public void writeContent(final OutputStream result) throws IOException
    {
        if(this.background != null) {
            result.write(OPEN_GROUP);
        }
        
        result.write(font.writeBegin());
        if(superSubScript < 0) {
            result.write(FONT_SUBSCRIPT);
        } else if(superSubScript > 0) {
            result.write(FONT_SUPERSCRIPT);
        }
        if(this.background != null) {
            result.write(HIGHLIGHT);
            result.write(intToByteArray(this.background.getColorNumber()));
        }
        result.write(DELIMITER);
           
        document.filterSpecialChar(result, content, false, softLineBreaks || this.document.getDocumentSettings().isAlwaysGenerateSoftLinebreaks());
        
        if(superSubScript != 0) {
            result.write(FONT_END_SUPER_SUBSCRIPT);
        }
        result.write(font.writeEnd());
        
        if(this.background != null) {
            result.write(CLOSE_GROUP);
        }        
    }
    
    
    public void setRtfDocument(RtfDocument doc) {
        super.setRtfDocument(doc);
        this.font.setRtfDocument(this.document);
    }
    
    
    public void setSoftLineBreaks(boolean softLineBreaks) {
        this.softLineBreaks = softLineBreaks;
    }
    
    
    public boolean getSoftLineBreaks() {
        return this.softLineBreaks;
    }
}
