import unittest
from neurojot.notes import (
    Note,
    FleetingNote,
    PermanentNote,
    LiteratureNote,
    DocumentReference,
)
import datetime
import uuid


class TestNoteMethods(unittest.TestCase):
    def test_init(self):
        note = Note(
            title="test title",
            text="test text",
            tags=["test", "tag"],
        )
        self.assertEqual(note.title, "test title")
        self.assertEqual(note.text, "test text")
        self.assertEqual(note.tags, ["test", "tag"])
        self.assertEqual(note.type, "fleeting")
        self.assertEqual(note.status, "active")
        self.assertEqual(note.parent_note_id, None)
        self.assertEqual(note.related_note_ids, [])
        self.assertEqual(note.date_created, None)

    def test_add_tag(self):
        note = Note(
            title="test title",
            text="test text",
            tags=["test", "tag"],
        )
        note.add_tag("new tag")
        self.assertEqual(note.tags, ["test", "tag", "new tag"])

    def test_remove_tag(self):
        note = Note(
            title="test title",
            text="test text",
            tags=["test", "tag"],
        )
        note.remove_tag("tag")
        self.assertEqual(note.tags, ["test"])

    def test_to_json(self):
        note = Note(
            title="test title",
            text="test text",
            tags=["test", "tag"],
        )
        note.id = uuid.uuid4()
        note.parent_note_id = uuid.uuid4()
        note.related_note_ids = [uuid.uuid4(), uuid.uuid4()]
        note.date_created = datetime.datetime.now()
        note.status = "test status"
        note.type = "test type"

        note_data = {
            "id": str(note.id),
            "title": note.title,
            "text": note.text,
            "parent_note_id": str(note.parent_note_id) if note.parent_note_id else None,
            "related_notes_ids": [str(note_id) for note_id in note.related_note_ids],
            "date_created": note.date_created.isoformat(),
            "tags": note.tags,
            "type": note.type,
            "status": note.status,
        }

        self.assertEqual(note.to_json(), note_data)

    def test_serialize(self):
        note = Note(
            title="test title",
            text="test text",
            tags=["test", "tag"],
        )
        note.id = uuid.uuid4()
        note.parent_note_id = uuid.uuid4()
        note.related_note_ids = [uuid.uuid4(), uuid.uuid4()]
        note.date_created = datetime.datetime.now()
        note.status = "test status"
        note.type = "test type"

        note_data = {
            "id": str(note.id),
            "title": note.title,
            "text": note.text,
            "parent_note_id": str(note.parent_note_id) if note.parent_note_id else None,
            "related_notes_ids": [str(note_id) for note_id in note.related_note_ids],
            "date_created": note.date_created.isoformat(),
            "tags": note.tags,
            "type": note.type,
            "status": note.status,
        }

        self.assertEqual(note.serialize(), note_data)

    def test_deserialize(self):
        note_data = {
            "id": "f8b6a9a2-6b6c-4a4d-8b9a-2a6b6c4a4d8b",
            "title": "test title",
            "text": "test text",
            "parent_note_id": "f8b6a9a2-6b6c-4a4d-8b9a-2a6b6c4a4d8b",
            "related_notes_ids": [
                "f8b6a9a2-6b6c-4a4d-8b9a-2a6b6c4a4d8b",
                "f8b6a9a2-6b6c-4a4d-8b9a-2a6b6c4a4d8b",
            ],
            "date_created": "2020-01-01T00:00:00",
            "tags": ["test", "tag"],
            "type": "test type",
            "status": "test status",
        }

        note = Note(
            title="test title",
            text="test text",
            tags=["test", "tag"],
        )
        note.id = uuid.UUID(note_data["id"])
        note.parent_note_id = (
            uuid.UUID(note_data["parent_note_id"])
            if note_data["parent_note_id"]
            else None
        )

        note.related_note_ids = [uuid.UUID(id) for id in note_data["related_notes_ids"]]
        note.date_created = datetime.datetime.fromisoformat(note_data["date_created"])
        note.status = note_data["status"]
        note.type = note_data["type"]

        self.assertEqual(Note.deserialize(note_data), note)
        note_data["type"] = "fleeting"
        self.assertIsInstance(Note.deserialize(note_data), FleetingNote)
        note_data["type"] = "permanent"
        self.assertIsInstance(Note.deserialize(note_data), PermanentNote)
        note_data["type"] = "literature"
        note_data["reference_id"] = "f8b6a9a2-6b6c-4a4d-8b9a-2a6b6c4a4d8b"
        self.assertIsInstance(Note.deserialize(note_data), LiteratureNote)
