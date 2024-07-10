from uuid import uuid1 as uuid
from datetime import datetime
from zipfile import ZipFile
from typing import Optional


class Image:
    def __init__(self, path):
        self.path = path
        self.filename = path.split('/')[-1]

    def to_xml(self) -> str:
        return '<item type="image" isRef="True">%s</item>' % self.filename

    def save(self, zipfile: ZipFile):
        with open(self.path, 'rb') as file:
            zipfile.writestr('Images/%s' % self.filename, file.read())


class Audio:
    def __init__(self, path: str):
        self.path = path
        self.filename = path.split('/')[-1]

    def to_xml(self) -> str:
        return '<item type="audio" isRef="True">%s</item>' % self.filename

    def save(self, zipfile: ZipFile):
        with open(self.path, 'rb') as file:
            zipfile.writestr('Audio/%s' % self.filename, file.read())

Content = str | Image | Audio

class Question:
    def __init__(self, 
                 price: int, 
                 question_content: list[Content] | Content,
                 answer: str, 
                 answer_content: Optional[list[Content] | Content] = None):
        self.price = price
        self.question_content: list[Content]
        if not isinstance(question_content, list):
            self.question_content = [question_content]
        if isinstance(question_content, list):
            self.question_content = question_content
        self.answer = answer

        self.answer_content: list[Content]
        if not answer_content:
            answer_content = []
        if not isinstance(answer_content, list):
            self.answer_content = [answer_content]
        if isinstance(answer_content, list):
            self.answer_content = answer_content

    def to_xml(self) -> str:
        xml = ''
        xml += '<question price="%d">' % self.price
        xml += '<params>'
        xml += '<param name="question" type="content">'
        for content in self.question_content:
            if isinstance(content, str):
                xml += '<item>%s</item>' % content
            elif isinstance(content, Image):
                xml += content.to_xml()
            elif isinstance(content, Audio):
                xml += content.to_xml()
            else:
                assert False, 'Unexpected type in question_content: %s' % type(content)
        xml += '</param>'
        if self.answer_content:
            xml += '<param name="answer" type="content">'
            for content in self.answer_content:
                if isinstance(content, str):
                    xml += '<item>%s</item>' % content
                elif isinstance(content, Image):
                    xml += content.to_xml()
                elif isinstance(content, Audio):
                    xml += content.to_xml()
                else:
                    assert False, 'Unexpected type in question_content: %s' % type(content)
            xml += '</param>'
        
        xml += '</params>'
        xml += '<right>'
        xml += '<answer>%s</answer>' % self.answer
        xml += '</right>'
        xml += '</question>'
        return xml

    def save(self, zipfile: ZipFile):
        for content in *self.question_content, *self.answer_content:
            if isinstance(content, str):
                continue
            content.save(zipfile)

    def multiply_score(self, x: int):
        self.price *= x


class Theme:
    def __init__(self, 
                 name: str, 
                 questions: list[Question]):
        self.name = name
        self.questions = questions

    def to_xml(self) -> str:
        xml = ''
        xml += '<theme name="%s">' % self.name
        xml += '<questions>'
        for question in self.questions:
            xml += question.to_xml()
        xml += '</questions>'
        xml += '</theme>'
        return xml

    def save(self, zipfile: ZipFile):
        for question in self.questions:
            question.save(zipfile)

    def multiply_score(self, x: int):
        for question in self.questions:
            question.multiply_score(x)


class Round:
    def __init__(self, 
                 name: str, 
                 themes: list[Theme], 
                 final: bool = False):
        self.name = name
        self.themes = themes
        self.final = final

    def to_xml(self) -> str:
        xml = ''
        if self.final:
            xml += '<round name="%s" type="final">' % self.name
        else:
            xml += '<round name="%s">' % self.name
        xml += '<themes>'
        for theme in self.themes:
            xml += theme.to_xml()
        xml += '</themes>'
        xml += '</round>'
        return xml

    def save(self, zipfile: ZipFile):
        for theme in self.themes:
            theme.save(zipfile)

    def multiply_score(self, x: int):
        for theme in self.themes:
            theme.multiply_score(x)


class Pack:
    def __init__(self, 
                 name: str, 
                 tag: str, 
                 author: str, 
                 rounds: list[Round]):
        self.name = name
        self.tag = tag
        self.author = author
        self.rounds = rounds

    def to_xml(self) -> str:
        xml = ''
        xml += '<?xml version="1.0" encoding="utf-8"?>'
        xml += '<package name="%s" version="5" id="%s" date="%s" difficulty="5" xmlns="https://github.com/VladimirKhil/SI/blob/master/assets/siq_5.xsd">' % (self.name, uuid(), datetime.today().strftime('%d.%m.%Y'))
        xml += '<tags><tag>%s</tag></tags><info><authors><author>%s</author></authors></info>' % (self.tag, self.author)
        xml += '<rounds>'
        for round in self.rounds:
            xml += round.to_xml()
        xml += '</rounds>'
        xml += '</package>'
        return xml

    def save(self, path: str = 'package.siq'):
        xml = self.to_xml()
        with ZipFile(path, 'w') as zipfile:
            zipfile.writestr('content.xml', xml)
            zipfile.mkdir('Images')
            zipfile.mkdir('Audio')
            for round in self.rounds:
                round.save(zipfile)

    def multiply_score(self, x: int):
        for round in self.rounds:
            round.multiply_score(x)
