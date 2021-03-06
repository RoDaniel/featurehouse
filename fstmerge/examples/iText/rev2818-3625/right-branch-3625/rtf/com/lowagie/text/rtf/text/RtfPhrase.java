

package com.lowagie.text.rtf.text;

import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;

import com.lowagie.text.Chunk;
import com.lowagie.text.DocumentException;
import com.lowagie.text.Element;
import com.lowagie.text.Phrase;
import com.lowagie.text.rtf.RtfBasicElement;
import com.lowagie.text.rtf.RtfElement;
import com.lowagie.text.rtf.document.RtfDocument;
import com.lowagie.text.rtf.style.RtfFont;



public class RtfPhrase extends RtfElement {

    
    public static final byte[] PARAGRAPH_DEFAULTS = "\\pard".getBytes();
    
    public static final byte[] PLAIN = "\\plain".getBytes();
    
    public static final byte[] IN_TABLE = "\\intbl".getBytes();
    
    public static final byte[] LINE_SPACING = "\\sl".getBytes();
    
    
    protected ArrayList<RtfBasicElement> chunks = new ArrayList<RtfBasicElement>();
    
    private int lineLeading = 0; 
    
    
    protected RtfPhrase(RtfDocument doc) {
        super(doc);
    }
    
    
    public RtfPhrase(RtfDocument doc, Phrase phrase) {
        super(doc);
        
        if(phrase == null) {
            return;
        }
        
        if(phrase.hasLeading()) {
            this.lineLeading = (int) (phrase.getLeading() * RtfElement.TWIPS_FACTOR);
        } else {
            this.lineLeading = 0;
        }
        
        RtfFont phraseFont = new RtfFont(null, phrase.getFont());
        for(int i = 0; i < phrase.size(); i++) {
            Element chunk = phrase.get(i);
            if(chunk instanceof Chunk) {
                ((Chunk) chunk).setFont(phraseFont.difference(((Chunk) chunk).getFont()));
            }
            try {
                RtfBasicElement[] rtfElements = doc.getMapper().mapElement(chunk);
                for(int j = 0; j < rtfElements.length; j++) {
                    chunks.add(rtfElements[j]);
                }
            } catch(DocumentException de) {
            }
        }
    }
    
        
    public void writeContent(final OutputStream result) throws IOException
    {
        result.write(PARAGRAPH_DEFAULTS);
        result.write(PLAIN);
        if(inTable) {
            result.write(IN_TABLE);
        }
        if(this.lineLeading > 0) {
            result.write(LINE_SPACING);
            result.write(intToByteArray(this.lineLeading));
        }
        for(int i = 0; i < chunks.size(); i++) {
            RtfBasicElement rbe = chunks.get(i);
            rbe.writeContent(result);
        }
    }        
    
    
    public void setInTable(boolean inTable) {
        super.setInTable(inTable);
        for(int i = 0; i < this.chunks.size(); i++) {
            this.chunks.get(i).setInTable(inTable);
        }
    }
    
    
    public void setInHeader(boolean inHeader) {
        super.setInHeader(inHeader);
        for(int i = 0; i < this.chunks.size(); i++) {
            this.chunks.get(i).setInHeader(inHeader);
        }
    }
    
    
    public void setRtfDocument(RtfDocument doc) {
        super.setRtfDocument(doc);
        for(int i = 0; i < this.chunks.size(); i++) {
            this.chunks.get(i).setRtfDocument(this.document);
        }
    }
}
