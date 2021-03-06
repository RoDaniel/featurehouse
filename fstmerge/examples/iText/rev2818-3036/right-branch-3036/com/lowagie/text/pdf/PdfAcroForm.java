

package com.lowagie.text.pdf;

import java.util.HashSet;

import com.lowagie.text.ExceptionConverter;
import com.lowagie.text.Rectangle;



public class PdfAcroForm extends PdfDictionary {

    private PdfWriter writer;


    
    private HashSet<PdfTemplate> fieldTemplates = new HashSet<PdfTemplate>();

    
    private PdfArray documentFields = new PdfArray();

    
    private PdfArray calculationOrder = new PdfArray();

    
    private int sigFlags = 0;

    
    public PdfAcroForm(PdfWriter writer) {
        super();
        this.writer = writer;
    }
    
    public void setNeedAppearances(boolean value) {
        put(PdfName.NEEDAPPEARANCES, new PdfBoolean(value));
    }

    

    public void addFieldTemplates(HashSet<PdfTemplate> ft) {
        fieldTemplates.addAll(ft);
    }

    

    public void addDocumentField(PdfIndirectReference ref) {
        documentFields.add(ref);
    }

    

    public boolean isValid() {
        if (documentFields.size() == 0) return false;
        put(PdfName.FIELDS, documentFields);
        if (sigFlags != 0)
            put(PdfName.SIGFLAGS, new PdfNumber(sigFlags));
        if (calculationOrder.size() > 0)
            put(PdfName.CO, calculationOrder);
        if (fieldTemplates.isEmpty()) return true;
        PdfDictionary dic = new PdfDictionary();
        for (PdfTemplate template: fieldTemplates) {
            PdfFormField.mergeResources(dic, (PdfDictionary)template.getResources());
        }
        put(PdfName.DR, dic);
        put(PdfName.DA, new PdfString("/Helv 0 Tf 0 g "));
        PdfDictionary fonts = (PdfDictionary)dic.get(PdfName.FONT);
        if (fonts != null) {
            writer.eliminateFontSubset(fonts);
        }
        return true;
    }

    

    public void addCalculationOrder(PdfFormField formField) {
        calculationOrder.add(formField.getIndirectReference());
    }

    

    public void setSigFlags(int f) {
        sigFlags |= f;
    }

    

    public void addFormField(PdfFormField formField) {
        writer.addAnnotation(formField);
    }

    
    public PdfFormField addHtmlPostButton(String name, String caption, String value, String url, BaseFont font, float fontSize, float llx, float lly, float urx, float ury) {
        PdfAction action = PdfAction.createSubmitForm(url, null, PdfAction.SUBMIT_HTML_FORMAT);
        PdfFormField button = new PdfFormField(writer, llx, lly, urx, ury, action);
        setButtonParams(button, PdfFormField.FF_PUSHBUTTON, name, value);
        drawButton(button, caption, font, fontSize, llx, lly, urx, ury);
        addFormField(button);
    return button;
    }

    
    public PdfFormField addResetButton(String name, String caption, String value, BaseFont font, float fontSize, float llx, float lly, float urx, float ury) {
        PdfAction action = PdfAction.createResetForm(null, 0);
        PdfFormField button = new PdfFormField(writer, llx, lly, urx, ury, action);
        setButtonParams(button, PdfFormField.FF_PUSHBUTTON, name, value);
        drawButton(button, caption, font, fontSize, llx, lly, urx, ury);
        addFormField(button);
        return button;
    }

    
    public PdfFormField addMap(String name, String value, String url, PdfContentByte appearance, float llx, float lly, float urx, float ury) {
        PdfAction action = PdfAction.createSubmitForm(url, null, PdfAction.SUBMIT_HTML_FORMAT | PdfAction.SUBMIT_COORDINATES);
        PdfFormField button = new PdfFormField(writer, llx, lly, urx, ury, action);
        setButtonParams(button, PdfFormField.FF_PUSHBUTTON, name, null);
        PdfAppearance pa = PdfAppearance.createAppearance(writer, urx - llx, ury - lly);
        pa.add(appearance);
        button.setAppearance(PdfAnnotation.APPEARANCE_NORMAL, pa);
        addFormField(button);
        return button;
    }

    
    public void setButtonParams(PdfFormField button, int characteristics, String name, String value) {
        button.setButton(characteristics);
        button.setFlags(PdfAnnotation.FLAGS_PRINT);
        button.setPage();
        button.setFieldName(name);
        if (value != null) button.setValueAsString(value);
    }

    
    public void drawButton(PdfFormField button, String caption, BaseFont font, float fontSize, float llx, float lly, float urx, float ury) {
        PdfAppearance pa = PdfAppearance.createAppearance(writer, urx - llx, ury - lly);
        pa.drawButton(0f, 0f, urx - llx, ury - lly, caption, font, fontSize);
        button.setAppearance(PdfAnnotation.APPEARANCE_NORMAL, pa);
    }

    
    public PdfFormField addHiddenField(String name, String value) {
        PdfFormField hidden = PdfFormField.createEmpty(writer);
        hidden.setFieldName(name);
        hidden.setValueAsName(value);
        addFormField(hidden);
        return hidden;
    }

    
    public PdfFormField addSingleLineTextField(String name, String text, BaseFont font, float fontSize, float llx, float lly, float urx, float ury) {
        PdfFormField field = PdfFormField.createTextField(writer, PdfFormField.SINGLELINE, PdfFormField.PLAINTEXT, 0);
        setTextFieldParams(field, text, name, llx, lly, urx, ury);
        drawSingleLineOfText(field, text, font, fontSize, llx, lly, urx, ury);
        addFormField(field);
        return field;
    }

    
    public PdfFormField addMultiLineTextField(String name, String text, BaseFont font, float fontSize, float llx, float lly, float urx, float ury) {
        PdfFormField field = PdfFormField.createTextField(writer, PdfFormField.MULTILINE, PdfFormField.PLAINTEXT, 0);
        setTextFieldParams(field, text, name, llx, lly, urx, ury);
        drawMultiLineOfText(field, text, font, fontSize, llx, lly, urx, ury);
        addFormField(field);
        return field;
    }

    
    public PdfFormField addSingleLinePasswordField(String name, String text, BaseFont font, float fontSize, float llx, float lly, float urx, float ury) {
        PdfFormField field = PdfFormField.createTextField(writer, PdfFormField.SINGLELINE, PdfFormField.PASSWORD, 0);
        setTextFieldParams(field, text, name, llx, lly, urx, ury);
        drawSingleLineOfText(field, text, font, fontSize, llx, lly, urx, ury);
        addFormField(field);
        return field;
    }

    
    public void setTextFieldParams(PdfFormField field, String text, String name, float llx, float lly, float urx, float ury) {
        field.setWidget(new Rectangle(llx, lly, urx, ury), PdfAnnotation.HIGHLIGHT_INVERT);
        field.setValueAsString(text);
        field.setDefaultValueAsString(text);
        field.setFieldName(name);
        field.setFlags(PdfAnnotation.FLAGS_PRINT);
        field.setPage();
    }

    
    public void drawSingleLineOfText(PdfFormField field, String text, BaseFont font, float fontSize, float llx, float lly, float urx, float ury) {
        PdfAppearance tp = PdfAppearance.createAppearance(writer, urx - llx, ury - lly);
        PdfAppearance tp2 = (PdfAppearance)tp.getDuplicate();
        tp2.setFontAndSize(font, fontSize);
        tp2.resetRGBColorFill();
        field.setDefaultAppearanceString(tp2);
        tp.drawTextField(0f, 0f, urx - llx, ury - lly);
        tp.beginVariableText();
        tp.saveState();
        tp.rectangle(3f, 3f, urx - llx - 6f, ury - lly - 6f);
        tp.clip();
        tp.newPath();
        tp.beginText();
        tp.setFontAndSize(font, fontSize);
        tp.resetRGBColorFill();
        tp.setTextMatrix(4, (ury - lly) / 2 - (fontSize * 0.3f));
        tp.showText(text);
        tp.endText();
        tp.restoreState();
        tp.endVariableText();
        field.setAppearance(PdfAnnotation.APPEARANCE_NORMAL, tp);
    }

    
    public void drawMultiLineOfText(PdfFormField field, String text, BaseFont font, float fontSize, float llx, float lly, float urx, float ury) {
        PdfAppearance tp = PdfAppearance.createAppearance(writer, urx - llx, ury - lly);
        PdfAppearance tp2 = (PdfAppearance)tp.getDuplicate();
        tp2.setFontAndSize(font, fontSize);
        tp2.resetRGBColorFill();
        field.setDefaultAppearanceString(tp2);
        tp.drawTextField(0f, 0f, urx - llx, ury - lly);
        tp.beginVariableText();
        tp.saveState();
        tp.rectangle(3f, 3f, urx - llx - 6f, ury - lly - 6f);
        tp.clip();
        tp.newPath();
        tp.beginText();
        tp.setFontAndSize(font, fontSize);
        tp.resetRGBColorFill();
        tp.setTextMatrix(4, 5);
        java.util.StringTokenizer tokenizer = new java.util.StringTokenizer(text, "\n");
        float yPos = ury - lly;
        while (tokenizer.hasMoreTokens()) {
            yPos -= fontSize * 1.2f;
            tp.showTextAligned(PdfContentByte.ALIGN_LEFT, tokenizer.nextToken(), 3, yPos, 0);
        }
        tp.endText();
        tp.restoreState();
        tp.endVariableText();
        field.setAppearance(PdfAnnotation.APPEARANCE_NORMAL, tp);
    }

    
    public PdfFormField addCheckBox(String name, String value, boolean status, float llx, float lly, float urx, float ury) {
        PdfFormField field = PdfFormField.createCheckBox(writer);
        setCheckBoxParams(field, name, value, status, llx, lly, urx, ury);
        drawCheckBoxAppearences(field, value, llx, lly, urx, ury);
        addFormField(field);
        return field;
    }

    
    public void setCheckBoxParams(PdfFormField field, String name, String value, boolean status, float llx, float lly, float urx, float ury) {
        field.setWidget(new Rectangle(llx, lly, urx, ury), PdfAnnotation.HIGHLIGHT_TOGGLE);
        field.setFieldName(name);
        if (status) {
            field.setValueAsName(value);
            field.setAppearanceState(value);
        }
        else {
            field.setValueAsName("Off");
            field.setAppearanceState("Off");
        }
        field.setFlags(PdfAnnotation.FLAGS_PRINT);
        field.setPage();
        field.setBorderStyle(new PdfBorderDictionary(1, PdfBorderDictionary.STYLE_SOLID));
    }

    
    public void drawCheckBoxAppearences(PdfFormField field, String value, float llx, float lly, float urx, float ury) {
        BaseFont font = null;
        try {
            font = BaseFont.createFont(BaseFont.ZAPFDINGBATS, BaseFont.WINANSI, BaseFont.NOT_EMBEDDED);
        }
        catch(Exception e) {
            throw new ExceptionConverter(e);
        }
        float size = (ury - lly);
        PdfAppearance tpOn = PdfAppearance.createAppearance(writer, urx - llx, ury - lly);
        PdfAppearance tp2 = (PdfAppearance)tpOn.getDuplicate();
        tp2.setFontAndSize(font, size);
        tp2.resetRGBColorFill();
        field.setDefaultAppearanceString(tp2);
        tpOn.drawTextField(0f, 0f, urx - llx, ury - lly);
        tpOn.saveState();
        tpOn.resetRGBColorFill();
        tpOn.beginText();
        tpOn.setFontAndSize(font, size);
        tpOn.showTextAligned(PdfContentByte.ALIGN_CENTER, "4", (urx - llx) / 2, (ury - lly) / 2 - (size * 0.3f), 0);
        tpOn.endText();
        tpOn.restoreState();
        field.setAppearance(PdfAnnotation.APPEARANCE_NORMAL, value, tpOn);
        PdfAppearance tpOff = PdfAppearance.createAppearance(writer, urx - llx, ury - lly);
        tpOff.drawTextField(0f, 0f, urx - llx, ury - lly);
        field.setAppearance(PdfAnnotation.APPEARANCE_NORMAL, "Off", tpOff);
    }

    
    public PdfFormField getRadioGroup(String name, String defaultValue, boolean noToggleToOff) {
        PdfFormField radio = PdfFormField.createRadioButton(writer, noToggleToOff);
        radio.setFieldName(name);
        radio.setValueAsName(defaultValue);
        return radio;
    }

    
    public void addRadioGroup(PdfFormField radiogroup) {
        addFormField(radiogroup);
    }

    
    public PdfFormField addRadioButton(PdfFormField radiogroup, String value, float llx, float lly, float urx, float ury) {
        PdfFormField radio = PdfFormField.createEmpty(writer);
        radio.setWidget(new Rectangle(llx, lly, urx, ury), PdfAnnotation.HIGHLIGHT_TOGGLE);
        String name = ((PdfName)radiogroup.get(PdfName.V)).toString().substring(1);
        if (name.equals(value)) {
            radio.setAppearanceState(value);
        }
        else {
            radio.setAppearanceState("Off");
        }
        drawRadioAppearences(radio, value, llx, lly, urx, ury);
        radiogroup.addKid(radio);
        return radio;
    }

    
    public void drawRadioAppearences(PdfFormField field, String value, float llx, float lly, float urx, float ury) {
        PdfAppearance tpOn = PdfAppearance.createAppearance(writer, urx - llx, ury - lly);
        tpOn.drawRadioField(0f, 0f, urx - llx, ury - lly, true);
        field.setAppearance(PdfAnnotation.APPEARANCE_NORMAL, value, tpOn);
        PdfAppearance tpOff = PdfAppearance.createAppearance(writer, urx - llx, ury - lly);
        tpOff.drawRadioField(0f, 0f, urx - llx, ury - lly, false);
        field.setAppearance(PdfAnnotation.APPEARANCE_NORMAL, "Off", tpOff);
    }

    
    public PdfFormField addSelectList(String name, String[] options, String defaultValue, BaseFont font, float fontSize, float llx, float lly, float urx, float ury) {
        PdfFormField choice = PdfFormField.createList(writer, options, 0);
        setChoiceParams(choice, name, defaultValue, llx, lly, urx, ury);
        StringBuffer text = new StringBuffer();
        for (int i = 0; i < options.length; i++) {
            text.append(options[i]).append('\n');
        }
        drawMultiLineOfText(choice, text.toString(), font, fontSize, llx, lly, urx, ury);
        addFormField(choice);
        return choice;
    }

    
    public PdfFormField addSelectList(String name, String[][] options, String defaultValue, BaseFont font, float fontSize, float llx, float lly, float urx, float ury) {
        PdfFormField choice = PdfFormField.createList(writer, options, 0);
        setChoiceParams(choice, name, defaultValue, llx, lly, urx, ury);
        StringBuffer text = new StringBuffer();
        for (int i = 0; i < options.length; i++) {
            text.append(options[i][1]).append('\n');
        }
        drawMultiLineOfText(choice, text.toString(), font, fontSize, llx, lly, urx, ury);
        addFormField(choice);
        return choice;
    }

    
    public PdfFormField addComboBox(String name, String[] options, String defaultValue, boolean editable, BaseFont font, float fontSize, float llx, float lly, float urx, float ury) {
        PdfFormField choice = PdfFormField.createCombo(writer, editable, options, 0);
        setChoiceParams(choice, name, defaultValue, llx, lly, urx, ury);
        if (defaultValue == null) {
            defaultValue = options[0];
        }
        drawSingleLineOfText(choice, defaultValue, font, fontSize, llx, lly, urx, ury);
        addFormField(choice);
        return choice;
    }

    
    public PdfFormField addComboBox(String name, String[][] options, String defaultValue, boolean editable, BaseFont font, float fontSize, float llx, float lly, float urx, float ury) {
        PdfFormField choice = PdfFormField.createCombo(writer, editable, options, 0);
        setChoiceParams(choice, name, defaultValue, llx, lly, urx, ury);
        String value = null;
        for (int i = 0; i < options.length; i++) {
            if (options[i][0].equals(defaultValue)) {
                value = options[i][1];
                break;
            }
        }
        if (value == null) {
            value = options[0][1];
        }
        drawSingleLineOfText(choice, value, font, fontSize, llx, lly, urx, ury);
        addFormField(choice);
        return choice;
    }

    
    public void setChoiceParams(PdfFormField field, String name, String defaultValue, float llx, float lly, float urx, float ury) {
        field.setWidget(new Rectangle(llx, lly, urx, ury), PdfAnnotation.HIGHLIGHT_INVERT);
        if (defaultValue != null) {
            field.setValueAsString(defaultValue);
            field.setDefaultValueAsString(defaultValue);
        }
        field.setFieldName(name);
        field.setFlags(PdfAnnotation.FLAGS_PRINT);
        field.setPage();
        field.setBorderStyle(new PdfBorderDictionary(2, PdfBorderDictionary.STYLE_SOLID));
    }

    
    public PdfFormField addSignature(String name, 
                    float llx, float lly, float urx, float ury) {
        PdfFormField signature = PdfFormField.createSignature(writer);
        setSignatureParams(signature, name, llx, lly, urx, ury);
        drawSignatureAppearences(signature, llx, lly, urx, ury);
        addFormField(signature);
        return signature;
    }
    
    
    public void setSignatureParams(PdfFormField field, String name,
                    float llx, float lly, float urx, float ury) {
        field.setWidget(new Rectangle(llx, lly, urx, ury), PdfAnnotation.HIGHLIGHT_INVERT);
        field.setFieldName(name);
        field.setFlags(PdfAnnotation.FLAGS_PRINT);
        field.setPage();
        field.setMKBorderColor(java.awt.Color.black);
        field.setMKBackgroundColor(java.awt.Color.white);
    }

    
    public void drawSignatureAppearences(PdfFormField field, 
                    float llx, float lly, float urx, float ury) {
        PdfAppearance tp = PdfAppearance.createAppearance(writer, urx - llx, ury - lly);
        tp.setGrayFill(1.0f);
        tp.rectangle(0, 0, urx - llx, ury - lly);
        tp.fill();
        tp.setGrayStroke(0);
        tp.setLineWidth(1);
        tp.rectangle(0.5f, 0.5f, urx - llx - 0.5f, ury - lly - 0.5f);
        tp.closePathStroke();
        tp.saveState();
        tp.rectangle(1, 1, urx - llx - 2, ury - lly - 2);
        tp.clip();
        tp.newPath();
        tp.restoreState();
        field.setAppearance(PdfAnnotation.APPEARANCE_NORMAL, tp);
    }
}