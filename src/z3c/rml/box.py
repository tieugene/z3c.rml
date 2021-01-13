##############################################################################
#
# Copyright (c) 2020 Eugene A. Pivnev <ti.eugene@gmail.com>.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Page Drawing Related Boxed Element Processing
TODO: textBox
"""

from z3c.rml import attr, directive, interfaces


class IXBox(interfaces.IRMLDirectiveSignature):
    """Parent class for checkBox, letterBoxes, textBox"""

    x = attr.Measurement(
        title='X-Position',
        description='The x-position of the lower-left corner of the box.',
        default=0,
        required=True)

    y = attr.Measurement(
        title='Y-Position',
        description='The y-position of the lower-left corner of the box.',
        default=0,
        required=True)

    style = attr.Style(
        title='Style',
        description='The box style that is applied to the letterboxes.',
        required=False)

    boxFillColor = attr.Color(
        title='Box Fill Color',
        description='The color to be used for the background.',
        required=False)

    boxStrokeColor = attr.Color(
        title='Box Strike Color',
        description='The color to be used for the lines making up.',
        required=False)

    label = attr.Text(
        title='Label',
        description='The label.',
        required=False)

    labelFontName = attr.Text(
        title='Label Font Name',
        description='The font used to print the label.',
        required=False)

    labelFontSize = attr.Measurement(
        title='Label Font Size',
        description='The size of the label.',
        required=False)

    labelTextColor = attr.Color(
        title='Label Text Color',
        description='The color of the text of the label of an *Box elements.',
        required=False)

    labelOffsetX = attr.Measurement(
        title='Label X-Offset',
        description='The x-offset of the lower-left corner of the label.',
        default=0,
        required=True)

    labelOffsetY = attr.Measurement(
        title='Label Y-Offset',
        description='The y-offset of the lower-left corner of the label.',
        default=0,
        required=True)

    lineWidth = attr.Measurement(
        title='Line Width',
        description='The width of the ...',
        required=False)


class XBox(directive.RMLDirective):
    """TODO: boxFillColor=None"""
    attrMapping = {'cellWidth': 'boxWidth', 'cellHeight': 'boxHeight'}
    attrExclude = {}

    def applystyle(self, attrs):
        style = attrs.pop('style', None)
        if style:
            for k, v in style.__dict__.items():
                if k not in self.attrExclude:
                    k = self.attrMapping.get(k, k)
                    if k not in attrs:
                        attrs[k] = v


class ICheckBox(IXBox):
    bold = attr.Boolean(
        title='Bold',
        description='...',
        required=False)

    boxWidth = attr.Measurement(
        title='Box Width',
        description='The width of the ...',
        required=False)

    boxHeight = attr.Measurement(
        title='Box Height',
        description='The height of the ...',
        required=False)

    checkStrokeColor = attr.Color(
        title='Check Stroke Color',
        description='The color for the ...',
        required=False)

    checked = attr.Boolean(
        title='Checked',
        description='...',
        required=False)

    graphicOff = attr.Image(
        title='Graphic Off',
        description='Reference to the external file of the image for state Off',
        required=False)

    graphicOn = attr.Image(
        title='Graphic On',
        description='Reference to the external file of the image for state On',
        required=False)

    line1 = attr.Text(
        title='Label 1',
        description='...',
        required=False)

    line2 = attr.Text(
        title='Label 2',
        description='...',
        required=False)

    line3 = attr.Text(
        title='Label 3',
        description='...',
        required=False)


class CheckBox(XBox):
    signature = ICheckBox
    attrExclude = {'name', 'parent', 'alias', 'fontName', 'fontSize', 'textColor', 'alignment'}

    def process(self):
        """
        TODO:
        - graphicO* - w/o edges; transparent
        - bold?
        - label?
        - default boxWidth/boxHeight = ?
        """
        args = dict(self.getAttributeValues())
        self.applystyle(args)
        # go draw
        canvas = attr.getManager(self, interfaces.ICanvasManager).canvas
        x = args['x']
        y = args['y']
        w = args['boxWidth'] if 'boxWidth' in args else canvas.stringWidth('W', canvas._fontname, canvas._fontsize)
        h = args['boxHeight'] if 'boxHeight' in args else canvas._fontsize + 2
        bfc = args.get('boxFillColor')
        bsc = args.get('boxStrokeColor')
        canvas.saveState()
        if 'lineWidth' in args:
            canvas.setLineWidth(args['lineWidth'])
        if bfc:
            canvas.setFillColor(bfc)
        if bsc:
            canvas.setStrokeColor(bsc)
        canvas.rect(x=x, y=y, width=w, height=h, fill=(bfc is not None))
        chk = args.get('checked')
        if chk:
            img = args.get('graphicOn')
            if img:
                canvas.drawImage(img, x, y, w, h)
            else:
                csc = args.get('checkStrokeColor')
                if csc:
                    canvas.setStrokeColor(csc)
                p = canvas.beginPath()
                p.moveTo(x, y)
                p.lineTo(x + w, y + h)
                p.moveTo(x, y + h)
                p.lineTo(x + w, y)
                canvas.drawPath(p, stroke=True, fill=(bfc is not None))
        else:
            img = args.get('graphicOff')
            if img:
                canvas.drawImage(img, x, y, w, h)
        canvas.restoreState()
        # label[s]
        labels = []
        for i in range(3):
            lname = 'line{}'.format(i + 1)
            if lname in args:
                labels.append(args[lname])
        if len(labels):
            canvas.saveState()
            if ('labelFontSize' in args) and not ('labelFontName' in args):
                canvas.setFontSize(args['labelFontSize'])
            elif 'labelFontName' in args:
                canvas.setFont(args['labelFontName'], args.get('labelFontSize'), canvas._fontsize)  # hack
            if 'labelTextColor' in args:
                canvas.setFillColor(args['labelTextColor'])
            x += w + 2
            lh = canvas._fontsize
            x += args.get('labelOffsetX', 0)
            y += args.get('labelOffsetY', 0) + (h + lh * (len(labels) - 1.5)) / 2
            for line in labels:
                canvas.drawString(x=x, y=y, text=line)
                y -= lh
            canvas.restoreState()


class IXTBox(IXBox):
    """Parent class for letterBoxes, textBox"""

    fontName = attr.Text(
        title='Font Name',
        description='The font used to print the content.',
        required=False)

    fontSize = attr.Measurement(
        title='Font Size',
        description='The size of the content text.',
        required=False)

    textColor = attr.Color(
        title='Text Color',
        description='The color for the main contents in the letterboxes or textbox.',
        required=False)

    text = attr.TextNode(  # raw: XMLContent
        title='Text',
        description='The text content.',
        required=True)


class ILetterBoxes(IXTBox):
    """A letter boxes.
    TODO: strokeBottom, strokeLeft, strokeRight, strokeTop"""

    count = attr.Integer(
        title='Count',
        description='Qty of letterboxes to output.',
        required=True)

    boxGap = attr.Measurement(
        title='Box Gap',
        description='The width of ... gap.',
        required=False)

    boxExtraGaps = attr.Sequence(
        title='Box Extra Gaps',
        description='The additional gaps between selected boxes.',
        value_type=attr.Text(),
        required=False)

    boxWidth = attr.Measurement(
        title='Box Width',
        description='The width of the ...',
        required=False)

    boxHeight = attr.Measurement(
        title='Box Height',
        description='The height of the ...',
        required=False)

    combHeight = attr.Float(
        title='Comb Height',
        description='The height of the ...',
        required=False)

    alignment = attr.Choice(
        title='Alignment',
        description='The alignment of the contents of the box.',
        choices=interfaces.ALIGN_CHOICES,
        required=False)

    strokeTop = attr.Boolean(
        title='Stroke Top',
        description='Stroke top edge of boxes',
        required=False)

    strokeBottom = attr.Boolean(
        title='Stroke Bottom',
        description='Stroke bottom edge of boxes',
        required=False)

    strokeLeft = attr.Boolean(
        title='Stroke Left',
        description='Stroke left edge of boxes',
        required=False)

    strokeRight = attr.Boolean(
        title='Stroke Right',
        description='Stroke right edge of boxes',
        required=False)


class LetterBoxes(XBox):
    signature = ILetterBoxes
    attrExclude = {'name', 'parent', 'alias'}

    def process(self):
        """
        Draw: (rectangle + symbol)s [+ label]
        TODO:
        - labelOffSet*
        - alignment
        - default text font = mono, 10pt?
        - default alignments: hCenter, vTop
        """
        args = dict(self.getAttributeValues())
        self.applystyle(args)
        # go draw
        canvas = attr.getManager(self, interfaces.ICanvasManager).canvas
        canvas.saveState()
        if 'lineWidth' in args:
            canvas.setLineWidth(args['lineWidth'])
        if ('fontSize' in args) and not ('fontName' in args):
            canvas.setFontSize(args['fontSize'])
        elif 'fontName' in args:
            canvas.setFont(args['fontName'], args.get('fontSize'), canvas._fontsize)  # hack
        x = args['x']
        y = args['y']
        w = args['boxWidth'] if 'boxWidth' in args else canvas.stringWidth('W', canvas._fontname, canvas._fontsize)
        h = args['boxHeight'] if 'boxHeight' in args else canvas._fontsize + 2
        comb = args.get('combHeight')
        gap = args.get('boxGap', 0)
        dy = (0.5 * h) - (0.25 * canvas._fontsize)
        bfc = args.get('boxFillColor')
        bsc = args.get('boxStrokeColor')
        tc = args.get('textColor')
        text = args['text']
        count = args['count']
        gaps_xtra = [0] * count
        if 'boxExtraGaps' in args:
            for gx in args['boxExtraGaps']:
                i, g = gx.split(':')
                gaps_xtra[int(i) - 1] = attr.Measurement().fromUnicode(g)
        for i in range(count):
            x1 = x + i * (w + gap) + sum(gaps_xtra[:i])
            # draw box
            canvas.saveState()
            if bfc:
                canvas.setFillColor(bfc)
            if bsc:
                canvas.setStrokeColor(bsc)
            # if !stroke* && !combHeight:
            # canvas.rect(x=x1, y=y, width=w, height=h, fill=(bfc is not None))
            if bfc is not None:
                canvas.rect(x=x1, y=y, width=w, height=h, fill=True)
            p = canvas.beginPath()
            if args.get('strokeBottom', True):
                p.moveTo(x1, y)
                p.lineTo(x1 + w, y)
            if args.get('strokeTop', True):
                p.moveTo(x1, y + h)
                p.lineTo(x1 + w, y + h)
            if args.get('strokeLeft', True):
                p.moveTo(x1, y)
                p.lineTo(x1, y + h if comb is None else (y + h) * comb)
            if args.get('strokeRight', True):
                p.moveTo(x1 + w, y)
                p.lineTo(x1 + w, y + h if comb is None else (y + h) * comb)
            canvas.drawPath(p, stroke=True, fill=(bfc is not None))
            canvas.restoreState()
            # draw char
            if i < len(text):
                canvas.saveState()
                if tc:
                    canvas.setFillColor(tc)
                # FIXME: alignment
                canvas.drawCentredString(float(x1 + (float(w) / 2.0)), float(y) + dy, text=text[i])
                canvas.restoreState()
        canvas.restoreState()
        # label
        if 'label' in args:
            canvas.saveState()
            if ('labelFontSize' in args) and not ('labelFontName' in args):
                canvas.setFontSize(args['labelFontSize'])
            elif 'labelFontName' in args:
                canvas.setFont(args['labelFontName'], args.get('labelFontSize'), canvas._fontsize)  # hack
            if 'labelTextColor' in args:
                canvas.setFillColor(args['labelTextColor'])
            y += args.get('labelOffsetY', 0)
            # FIXME: labelAlignment?
            canvas.drawString(x=x + args.get('labelOffsetX', 0), y=y + args.get('labelOffsetY', 0) + h + 2,
                              text=args['label'])
            canvas.restoreState()


class ITextBox(IXTBox):
    """A Text Box
    TODO: borderSpec"""

    boxWidth = attr.Measurement(
        title='Box Width',
        description='The width of the ...',
        required=True)

    boxHeight = attr.Measurement(
        title='Box Height',
        description='The height of the ...',
        required=True)

    align = attr.Choice(
        title='Horizontal alignment',
        description='The horizontal alignment of the contents of the text box.',
        choices=interfaces.ALIGN_CHOICES,
        required=False)

    vAlign = attr.Choice(
        title='Vertical alignment',
        description='The vertical alignment of the contents of the text box.',
        choices=interfaces.ALIGN_CHOICES,
        required=False)

    shrinkToFit = attr.Boolean(
        title='Shrink To Fit',
        description='Shrink to fit.',
        required=False)

    borderSpec = attr.Text(
        title='Border Spec',
        description='Border ...',
        required=False)


class TextBox(directive.RMLDirective):
    signature = ITextBox
