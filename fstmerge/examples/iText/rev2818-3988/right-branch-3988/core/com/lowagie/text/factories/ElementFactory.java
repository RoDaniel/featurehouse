
package com.lowagie.text.factories;

import java.awt.Color;
import java.io.IOException;
import java.net.MalformedURLException;
import java.util.ArrayList;
import java.util.Properties;
import java.util.StringTokenizer;

import com.lowagie.text.Anchor;
import com.lowagie.text.Annotation;
import com.lowagie.text.BadElementException;
import com.lowagie.text.Cell;
import com.lowagie.text.ChapterAutoNumber;
import com.lowagie.text.Chunk;
import com.lowagie.text.ElementTags;
import com.lowagie.text.ExceptionConverter;
import com.lowagie.text.FontFactory;
import com.lowagie.text.Image;
import com.lowagie.text.List;
import com.lowagie.text.ListItem;
import com.lowagie.text.Paragraph;
import com.lowagie.text.Phrase;
import com.lowagie.text.Rectangle;
import com.lowagie.text.Section;
import com.lowagie.text.Table;
import com.lowagie.text.Utilities;
import com.lowagie.text.html.Markup;


public class ElementFactory {

    
    public static Chunk getChunk(Properties attributes) {
        Chunk chunk = new Chunk();

        chunk.setFont(FontFactory.getFont(attributes));
        String value;

        value = attributes.getProperty(ElementTags.ITEXT);
        if (value != null) {
            chunk.append(value);
        }
        value = attributes.getProperty(ElementTags.LOCALGOTO);
        if (value != null) {
            chunk.setLocalGoto(value);
        }
        value = attributes.getProperty(ElementTags.REMOTEGOTO);
        if (value != null) {
            String page = attributes.getProperty(ElementTags.PAGE);
            if (page != null) {
                chunk.setRemoteGoto(value, Integer.parseInt(page));
            } else {
                String destination = attributes
                        .getProperty(ElementTags.DESTINATION);
                if (destination != null) {
                    chunk.setRemoteGoto(value, destination);
                }
            }
        }
        value = attributes.getProperty(ElementTags.LOCALDESTINATION);
        if (value != null) {
            chunk.setLocalDestination(value);
        }
        value = attributes.getProperty(ElementTags.SUBSUPSCRIPT);
        if (value != null) {
            chunk.setTextRise(Float.parseFloat(value + "f"));
        }
        value = attributes.getProperty(Markup.CSS_KEY_VERTICALALIGN);
        if (value != null && value.endsWith("%")) {
            float p = Float.parseFloat(value.substring(0, value.length() - 1)
                    + "f") / 100f;
            chunk.setTextRise(p * chunk.getFont().getSize());
        }
        value = attributes.getProperty(ElementTags.GENERICTAG);
        if (value != null) {
            chunk.setGenericTag(value);
        }
        value = attributes.getProperty(ElementTags.BACKGROUNDCOLOR);
        if (value != null) {
            chunk.setBackground(Markup.decodeColor(value));
        }
        return chunk;
    }

    
    public static Phrase getPhrase(Properties attributes) {
        Phrase phrase = new Phrase();
        phrase.setFont(FontFactory.getFont(attributes));
        String value;
        value = attributes.getProperty(ElementTags.LEADING);
        if (value != null) {
            phrase.setLeading(Float.parseFloat(value + "f"));
        }
        value = attributes.getProperty(Markup.CSS_KEY_LINEHEIGHT);
        if (value != null) {
            phrase.setLeading(Markup.parseLength(value,
                    Markup.DEFAULT_FONT_SIZE));
        }
        value = attributes.getProperty(ElementTags.ITEXT);
        if (value != null) {
            Chunk chunk = new Chunk(value);
            if ((value = attributes.getProperty(ElementTags.GENERICTAG)) != null) {
                chunk.setGenericTag(value);
            }
            phrase.add(chunk);
        }
        return phrase;
    }

    
    public static Anchor getAnchor(Properties attributes) {
        Anchor anchor = new Anchor(getPhrase(attributes));
        String value;
        value = attributes.getProperty(ElementTags.NAME);
        if (value != null) {
            anchor.setName(value);
        }
        value = (String) attributes.remove(ElementTags.REFERENCE);
        if (value != null) {
            anchor.setReference(value);
        }
        return anchor;
    }

    
    public static Paragraph getParagraph(Properties attributes) {
        Paragraph paragraph = new Paragraph(getPhrase(attributes));
        String value;
        value = attributes.getProperty(ElementTags.ALIGN);
        if (value != null) {
            paragraph.setAlignment(value);
        }
        value = attributes.getProperty(ElementTags.INDENTATIONLEFT);
        if (value != null) {
            paragraph.setIndentationLeft(Float.parseFloat(value + "f"));
        }
        value = attributes.getProperty(ElementTags.INDENTATIONRIGHT);
        if (value != null) {
            paragraph.setIndentationRight(Float.parseFloat(value + "f"));
        }
        return paragraph;
    }

    
    public static ListItem getListItem(Properties attributes) {
        ListItem item = new ListItem(getParagraph(attributes));
        return item;
    }

    
    public static List getList(Properties attributes) {
        List list = new List();

        list.setNumbered(Utilities.checkTrueOrFalse(attributes,
                ElementTags.NUMBERED));
        list.setLettered(Utilities.checkTrueOrFalse(attributes,
                ElementTags.LETTERED));
        list.setLowercase(Utilities.checkTrueOrFalse(attributes,
                ElementTags.LOWERCASE));
        list.setAutoindent(Utilities.checkTrueOrFalse(attributes,
                ElementTags.AUTO_INDENT_ITEMS));
        list.setAlignindent(Utilities.checkTrueOrFalse(attributes,
                ElementTags.ALIGN_INDENTATION_ITEMS));

        String value;

        value = attributes.getProperty(ElementTags.FIRST);
        if (value != null) {
            char character = value.charAt(0);
            if (Character.isLetter(character)) {
                list.setFirst(character);
            } else {
                list.setFirst(Integer.parseInt(value));
            }
        }

        value = attributes.getProperty(ElementTags.LISTSYMBOL);
        if (value != null) {
            list
                    .setListSymbol(new Chunk(value, FontFactory
                            .getFont(attributes)));
        }

        value = attributes.getProperty(ElementTags.INDENTATIONLEFT);
        if (value != null) {
            list.setIndentationLeft(Float.parseFloat(value + "f"));
        }

        value = attributes.getProperty(ElementTags.INDENTATIONRIGHT);
        if (value != null) {
            list.setIndentationRight(Float.parseFloat(value + "f"));
        }

        value = attributes.getProperty(ElementTags.SYMBOLINDENT);
        if (value != null) {
            list.setSymbolIndent(Float.parseFloat(value));
        }

        return list;
    }

    
    public static Cell getCell(Properties attributes) {
        Cell cell = new Cell();
        String value;

        cell.setHorizontalAlignment(attributes
                .getProperty(ElementTags.HORIZONTALALIGN));
        cell.setVerticalAlignment(attributes
                .getProperty(ElementTags.VERTICALALIGN));

        value = attributes.getProperty(ElementTags.WIDTH);
        if (value != null) {
            cell.setWidth(value);
        }
        value = attributes.getProperty(ElementTags.COLSPAN);
        if (value != null) {
            cell.setColspan(Integer.parseInt(value));
        }
        value = attributes.getProperty(ElementTags.ROWSPAN);
        if (value != null) {
            cell.setRowspan(Integer.parseInt(value));
        }
        value = attributes.getProperty(ElementTags.LEADING);
        if (value != null) {
            cell.setLeading(Float.parseFloat(value + "f"));
        }
        cell.setHeader(Utilities.checkTrueOrFalse(attributes,
                ElementTags.HEADER));
        if (Utilities.checkTrueOrFalse(attributes, ElementTags.NOWRAP)) {
            cell.setMaxLines(1);
        }
        setRectangleProperties(cell, attributes);
        return cell;
    }

    
    public static Table getTable(Properties attributes) {
        String value;
        Table table;
        try {

            value = attributes.getProperty(ElementTags.WIDTHS);
            if (value != null) {
                StringTokenizer widthTokens = new StringTokenizer(value, ";");
                ArrayList<String> values = new ArrayList<String>();
                while (widthTokens.hasMoreTokens()) {
                    values.add(widthTokens.nextToken());
                }
                table = new Table(values.size());
                float[] widths = new float[table.getColumns()];
                for (int i = 0; i < values.size(); i++) {
                    value = values.get(i);
                    widths[i] = Float.parseFloat(value + "f");
                }
                table.setWidths(widths);
            } else {
                value = attributes.getProperty(ElementTags.COLUMNS);
                try {
                    table = new Table(Integer.parseInt(value));
                } catch (Exception e) {
                    table = new Table(1);
                }
            }

            table.setBorder(Table.BOX);
            table.setBorderWidth(1);
            table.getDefaultCell().setBorder(Table.BOX);

            value = attributes.getProperty(ElementTags.LASTHEADERROW);
            if (value != null) {
                table.setLastHeaderRow(Integer.parseInt(value));
            }
            value = attributes.getProperty(ElementTags.ALIGN);
            if (value != null) {
                table.setAlignment(value);
            }
            value = attributes.getProperty(ElementTags.CELLSPACING);
            if (value != null) {
                table.setSpacing(Float.parseFloat(value + "f"));
            }
            value = attributes.getProperty(ElementTags.CELLPADDING);
            if (value != null) {
                table.setPadding(Float.parseFloat(value + "f"));
            }
            value = attributes.getProperty(ElementTags.OFFSET);
            if (value != null) {
                table.setOffset(Float.parseFloat(value + "f"));
            }
            value = attributes.getProperty(ElementTags.WIDTH);
            if (value != null) {
                if (value.endsWith("%"))
                    table.setWidth(Float.parseFloat(value.substring(0, value
                            .length() - 1)
                            + "f"));
                else {
                    table.setWidth(Float.parseFloat(value + "f"));
                    table.setLocked(true);
                }
            }
            table.setTableFitsPage(Utilities.checkTrueOrFalse(attributes,
                    ElementTags.TABLEFITSPAGE));
            table.setCellsFitPage(Utilities.checkTrueOrFalse(attributes,
                    ElementTags.CELLSFITPAGE));
            table.setConvert2pdfptable(Utilities.checkTrueOrFalse(attributes,
                    ElementTags.CONVERT2PDFP));

            setRectangleProperties(table, attributes);
            return table;
        } catch (BadElementException e) {
            throw new ExceptionConverter(e);
        }
    }

    
    private static void setRectangleProperties(Rectangle rect,
            Properties attributes) {
        String value;
        value = attributes.getProperty(ElementTags.BORDERWIDTH);
        if (value != null) {
            rect.setBorderWidth(Float.parseFloat(value + "f"));
        }
        int border = 0;
        if (Utilities.checkTrueOrFalse(attributes, ElementTags.LEFT)) {
            border |= Rectangle.LEFT;
        }
        if (Utilities.checkTrueOrFalse(attributes, ElementTags.RIGHT)) {
            border |= Rectangle.RIGHT;
        }
        if (Utilities.checkTrueOrFalse(attributes, ElementTags.TOP)) {
            border |= Rectangle.TOP;
        }
        if (Utilities.checkTrueOrFalse(attributes, ElementTags.BOTTOM)) {
            border |= Rectangle.BOTTOM;
        }
        rect.setBorder(border);

        String r = attributes.getProperty(ElementTags.RED);
        String g = attributes.getProperty(ElementTags.GREEN);
        String b = attributes.getProperty(ElementTags.BLUE);
        if (r != null || g != null || b != null) {
            int red = 0;
            int green = 0;
            int blue = 0;
            if (r != null)
                red = Integer.parseInt(r);
            if (g != null)
                green = Integer.parseInt(g);
            if (b != null)
                blue = Integer.parseInt(b);
            rect.setBorderColor(new Color(red, green, blue));
        } else {
            rect.setBorderColor(Markup.decodeColor(attributes
                    .getProperty(ElementTags.BORDERCOLOR)));
        }
        r = (String) attributes.remove(ElementTags.BGRED);
        g = (String) attributes.remove(ElementTags.BGGREEN);
        b = (String) attributes.remove(ElementTags.BGBLUE);
        value = attributes.getProperty(ElementTags.BACKGROUNDCOLOR);
        if (r != null || g != null || b != null) {
            int red = 0;
            int green = 0;
            int blue = 0;
            if (r != null)
                red = Integer.parseInt(r);
            if (g != null)
                green = Integer.parseInt(g);
            if (b != null)
                blue = Integer.parseInt(b);
            rect.setBackgroundColor(new Color(red, green, blue));
        } else if (value != null) {
            rect.setBackgroundColor(Markup.decodeColor(value));
        } else {
            value = attributes.getProperty(ElementTags.GRAYFILL);
            if (value != null) {
                rect.setGrayFill(Float.parseFloat(value + "f"));
            }
        }
    }

    
    public static ChapterAutoNumber getChapter(Properties attributes) {
        ChapterAutoNumber chapter = new ChapterAutoNumber("");
        setSectionParameters(chapter, attributes);
        return chapter;
    }

    
    public static Section getSection(Section parent, Properties attributes) {
        Section section = parent.addSection("");
        setSectionParameters(section, attributes);
        return section;
    }

    
    private static void setSectionParameters(Section section,
            Properties attributes) {
        String value;
        value = attributes.getProperty(ElementTags.NUMBERDEPTH);
        if (value != null) {
            section.setNumberDepth(Integer.parseInt(value));
        }
        value = attributes.getProperty(ElementTags.INDENT);
        if (value != null) {
            section.setIndentation(Float.parseFloat(value + "f"));
        }
        value = attributes.getProperty(ElementTags.INDENTATIONLEFT);
        if (value != null) {
            section.setIndentationLeft(Float.parseFloat(value + "f"));
        }
        value = attributes.getProperty(ElementTags.INDENTATIONRIGHT);
        if (value != null) {
            section.setIndentationRight(Float.parseFloat(value + "f"));
        }
    }

    
    public static Image getImage(Properties attributes)
            throws BadElementException, MalformedURLException, IOException {
        String value;

        value = attributes.getProperty(ElementTags.URL);
        if (value == null)
            throw new MalformedURLException("The URL of the image is missing.");
        Image image = Image.getInstance(value);

        value = attributes.getProperty(ElementTags.ALIGN);
        int align = 0;
        if (value != null) {
            if (ElementTags.ALIGN_LEFT.equalsIgnoreCase(value))
                align |= Image.LEFT;
            else if (ElementTags.ALIGN_RIGHT.equalsIgnoreCase(value))
                align |= Image.RIGHT;
            else if (ElementTags.ALIGN_MIDDLE.equalsIgnoreCase(value))
                align |= Image.MIDDLE;
        }
        if ("true".equalsIgnoreCase(attributes
                .getProperty(ElementTags.UNDERLYING)))
            align |= Image.UNDERLYING;
        if ("true".equalsIgnoreCase(attributes
                .getProperty(ElementTags.TEXTWRAP)))
            align |= Image.TEXTWRAP;
        image.setAlignment(align);

        value = attributes.getProperty(ElementTags.ALT);
        if (value != null) {
            image.setAlt(value);
        }

        String x = attributes.getProperty(ElementTags.ABSOLUTEX);
        String y = attributes.getProperty(ElementTags.ABSOLUTEY);
        if ((x != null) && (y != null)) {
            image.setAbsolutePosition(Float.parseFloat(x + "f"), Float
                    .parseFloat(y + "f"));
        }
        value = attributes.getProperty(ElementTags.PLAINWIDTH);
        if (value != null) {
            image.scaleAbsoluteWidth(Float.parseFloat(value + "f"));
        }
        value = attributes.getProperty(ElementTags.PLAINHEIGHT);
        if (value != null) {
            image.scaleAbsoluteHeight(Float.parseFloat(value + "f"));
        }
        value = attributes.getProperty(ElementTags.ROTATION);
        if (value != null) {
            image.setRotation(Float.parseFloat(value + "f"));
        }
        return image;
    }

    
    public static Annotation getAnnotation(Properties attributes) {
        float llx = 0, lly = 0, urx = 0, ury = 0;
        String value;

        value = attributes.getProperty(ElementTags.LLX);
        if (value != null) {
            llx = Float.parseFloat(value + "f");
        }
        value = attributes.getProperty(ElementTags.LLY);
        if (value != null) {
            lly = Float.parseFloat(value + "f");
        }
        value = attributes.getProperty(ElementTags.URX);
        if (value != null) {
            urx = Float.parseFloat(value + "f");
        }
        value = attributes.getProperty(ElementTags.URY);
        if (value != null) {
            ury = Float.parseFloat(value + "f");
        }

        String title = attributes.getProperty(ElementTags.TITLE);
        String text = attributes.getProperty(ElementTags.CONTENT);
        if (title != null || text != null) {
            return new Annotation(title, text, llx, lly, urx, ury);
        }
        value = attributes.getProperty(ElementTags.URL);
        if (value != null) {
            return new Annotation(llx, lly, urx, ury, value);
        }
        value = attributes.getProperty(ElementTags.NAMED);
        if (value != null) {
            return new Annotation(llx, lly, urx, ury, Integer.parseInt(value));
        }
        String file = attributes.getProperty(ElementTags.FILE);
        String destination = attributes.getProperty(ElementTags.DESTINATION);
        String page = (String) attributes.remove(ElementTags.PAGE);
        if (file != null) {
            if (destination != null) {
                return new Annotation(llx, lly, urx, ury, file, destination);
            }
            if (page != null) {
                return new Annotation(llx, lly, urx, ury, file, Integer
                        .parseInt(page));
            }
        }
        return new Annotation("", "", llx, lly, urx, ury);
    }
}