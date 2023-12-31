import datetime
import json
from typing import Optional, List, Union
import uuid

from chromadb import Collection as ChromaCollection


class Note:
    def __init__(
        self,
        title: str,
        text: str,
        parent_note: Optional["Note"] = None,
        related_notes: Optional[List["Note"]] = [],
        tags: Optional[List[str]] = None,
    ):
        self._id = uuid.uuid4()
        self.title = title
        self.text = text
        self._parent_note_id = parent_note.id if parent_note else None
        self._related_note_ids = (
            [related_note.id for related_note in related_notes] if related_notes else []
        )
        self.date_created = datetime.datetime.now()
        self.type = None
        self.tags = tags if tags else []
        self.status = "active"

    @property
    def id(self):
        return self._id.hex

    @property
    def parent_note(self):
        return self.get(self._parent_note_id)

    @property
    def related_notes(self):
        return [self.get(note_id) for note_id in self._related_note_ids]

    def add_parent(self, parent_note: "Note"):
        if self.parent_note:
            raise ValueError("Note already has a parent")
        self.parent_note = parent_note

    def add_related_notes(self, related_notes: Union[List["Note"], "Note"]):
        if isinstance(related_notes, list):
            self.related_notes.extend(
                [related_notes.id for related_notes in related_notes]
            )
        else:
            self.related_notes.append(related_notes.id)

    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str):
        if tag in self.tags:
            self.tags.remove(tag)

    def to_dict(self):
        note_data = {
            "id": str(self.id),
            "title": self.title,
            "text": self.text,
            "parent_note_id": str(self._parent_note_id)
            if self._parent_note_id
            else None,
            "related_notes_ids": [str(note_id) for note_id in self._related_note_ids],
            "date_created": self.date_created.isoformat(),
            "tags": self.tags,
            "type": self.type,
            "status": self.status,
        }
        if self.type == "literature":
            note_data["reference_id"] = self.reference.id

        return note_data

    def serialize(self):
        return json.dumps(self.to_dict())

    @classmethod
    def deserialize(cls, data):
        note_data = json.loads(data)
        if note_data["type"] == "fleeting":
            note = FleetingNote(
                title=note_data["title"],
                text=note_data["text"],
                tags=note_data["tags"],
            )
        elif note_data["type"] == "literature":
            note = LiteratureNote(
                title=note_data["title"],
                text=note_data["text"],
                reference=LiteraturetReference.get(note_data["reference_id"]),
                tags=note_data["tags"],
            )
        elif note_data["type"] == "permanent":
            note = PermanentNote(
                title=note_data["title"],
                text=note_data["text"],
                tags=note_data["tags"],
            )
        else:
            note = Note(
                title=note_data["title"],
                text=note_data["text"],
                tags=note_data["tags"],
            )
            note.type = note_data["type"]

        note.id = uuid.UUID(note_data["id"])
        note.parent_note_id = (
            uuid.UUID(note_data["parent_note_id"])
            if note_data["parent_note_id"]
            else None
        )
        note.related_note_ids = [uuid.UUID(id) for id in note_data["related_notes_ids"]]
        note.date_created = datetime.datetime.fromisoformat(note_data["date_created"])
        note.status = note_data["status"]

        return note

    def save(self, collection: ChromaCollection):
        note_data = self.to_dict()
        metadata = {
            "type": note_data["type"],
            "tags": note_data["tags"],
            "date_created": note_data["date_created"],
        }
        if self.type == "literature":
            metadata["reference_id"] = note_data.get("reference_id")

        collection.upsert(
            ids=str(self.id),
            documents=json.dumps(note_data),
            metadatas=metadata,
        )

    @classmethod
    def get(cls, collection: ChromaCollection, note_id: str):
        result = collection.get(ids=note_id)
        if result:
            note_data = result[0]
            return Note.deserialize(note_data)
        return None


class FleetingNote(Note):
    def __init__(
        self,
        title: str,
        text: str,
        parent_note: Optional["Note"] = None,
        related_notes: Optional[List["Note"]] = None,
        tags: Optional[List[str]] = None,
    ):
        super().__init__(
            title=title,
            text=text,
            parent_note=parent_note,
            related_notes=related_notes,
            tags=tags,
        )
        self.type = "fleeting"

    def create_permanent(self, title: str, text: str):
        permanent_note = PermanentNote(
            title=title,
            text=text,
            parent_note=self.parent_note,
            related_notes=self.related_notes + [self],
            tags=self.tags,
        )
        self.add_related_notes(permanent_note)
        self.status = "archived"

        return permanent_note


class LiteratureNote(Note):
    def __init__(
        self,
        title: str,
        text: str,
        reference: "LiteraturetReference",
        parent_note: Optional["Note"] = None,
        related_notes: Optional[List["Note"]] = None,
        tags: Optional[List[str]] = None,
    ):
        super().__init__(
            title=title,
            text=text,
            parent_note=parent_note,
            related_notes=related_notes,
            tags=tags,
        )
        self.type = "literature"
        self.reference = reference


class PermanentNote(Note):
    def __init__(
        self,
        title: str,
        text: str,
        parent_note: Optional["Note"] = None,
        related_notes: Optional[List["Note"]] = None,
        tags: Optional[List[str]] = None,
    ):
        super().__init__(
            title=title,
            text=text,
            parent_note=parent_note,
            related_notes=related_notes,
            tags=tags,
        )
        self.type = "permanent"


class LiteraturetReference:
    def __init__(
        self,
        type: str,
        title: str,
        authors: str,
        year: int,
        url: Optional[str] = None,
        publisher: Optional[str] = None,
        journal: Optional[str] = None,
        volume: Optional[str] = None,
        number: Optional[str] = None,
        pages: Optional[str] = None,
        doi: Optional[str] = None,
        isbn: Optional[str] = None,
        **kwargs,
    ):
        self._id = uuid.uuid4()
        self.type = type
        self.title = title
        self.authors = authors
        self.year = year
        self.url = url
        self.publisher = publisher
        self.journal = journal
        self.volume = volume
        self.number = number
        self.pages = pages
        self.doi = doi
        self.isbn = isbn
        self.additional_fields = kwargs
        self.summary = None
        self.notes = []

    @property
    def id(self):
        return self._id.hex

    def add_summary(self, summary):
        self.summary = summary

    def add_note(self, title: str, text: str, **kwargs):
        self.notes.append(
            LiteratureNote(title=title, text=text, reference=self, **kwargs)
        )

    @classmethod
    def get(cls, reference_id):
        return None
